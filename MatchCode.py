import pandas;
import openpyxl;  # Not used directly: prerequisite for xlsx conversion
from sklearn.feature_extraction.text import TfidfVectorizer;
import os

# Calculates text similarity as described here: https://www.newscatcherapi.com/blog/ultimate-guide-to-text-similarity-with-python
vectorizer = TfidfVectorizer(stop_words='english')


script_path = __file__
base_path = os.path.dirname(script_path)

# If a faculty member isn't found (which is possible) or no abstract is assigned (less possible), 
# they're assigned 0.02, which is just below the average of 0.022. 
def cosine_sim(text1, text2):
    if (text1 == "" or text2 == ""):
      return 0.02
    tfidf = vectorizer.fit_transform([text1, text2])                                                                                                                                                           
    pairwise_similarity = tfidf * tfidf.T 
    return (pairwise_similarity)[0,1]


def PerformMatch(InputAbstracts, InputJudges, InputCrawl="ProfessorInformation.csv"):

  OutputString = ""

  # Reads in data, and errors if it's not present

  InputAbstractRel = os.path.relpath(InputAbstracts, base_path)
  InputJudgeRel = os.path.relpath(InputJudges, base_path)

  # This is a whole kitten caboodle of error checks.

  PosterDataframe = pandas.read_excel(InputAbstractRel, sheet_name=None).popitem()[1]
  if (PosterDataframe.empty):
    OutputString += "\nERROR: Issue with Poster data file "+InputAbstracts+": no data could be extracted"
    #print(OutputString)
    return OutputString
  PosterDataframe.columns = PosterDataframe.columns.str.lower()
  NumberOfPosterTitlesOriginal = PosterDataframe['abstract'].count()
  PosterDataframe = PosterDataframe.dropna(thresh=2)
  JudgesDataframe = pandas.read_excel(InputJudgeRel, sheet_name=None).popitem()[1].dropna(thresh=3)
  if (JudgesDataframe.empty):
    OutputString += "\nERROR: Issue with Judge data file "+InputJudges+": no data could be extracted"
    #print(OutputString)
    return OutputString
  
  

  JudgesDataframe.columns = JudgesDataframe.columns.str.lower()

  
  if not 'judge firstname' in JudgesDataframe.columns:
    OutputString += "\nERROR: Datafile "+InputJudges+" does not have an appropriate 'JUDGE FIRSTNAME' column"
    return OutputString

  if not 'judge lastname' in JudgesDataframe.columns:
    OutputString += "\nERROR: Datafile "+InputJudges+" does not have an appropriate 'JUDGE LASTNAME' column"
    return OutputString
  
  if not 'hour available' in JudgesDataframe.columns:
    OutputString += "\nERROR: Datafile "+InputJudges+" does not have an appropriate 'HOUR AVAILABLE' column"
    return OutputString
  
  if not 'judge' in JudgesDataframe.columns:
    OutputString += "\nERROR: Datafile "+InputJudges+" does not have an appropriate 'JUDGE' column, numbering the judges from 1 to n."
    return OutputString

  if not 'department' in JudgesDataframe.columns:
    OutputString += "\nERROR: Datafile "+InputJudges+" does not have an appropriate 'DEPARTMENT' column"
    return OutputString
  
  if not 'abstract' in PosterDataframe.columns:
    OutputString += "\nERROR: Datafile "+InputAbstracts+" does not have an appropriate 'ABSTRACT' column"
    return OutputString
  
  if not 'advisor firstname' in PosterDataframe.columns:
    OutputString += "\nERROR: Datafile "+InputAbstracts+" does not have an appropriate 'ADVISOR FIRSTNAME' column"
    return OutputString
  
  if not 'advisor lastname' in PosterDataframe.columns:
    OutputString += "\nERROR: Datafile "+InputAbstracts+" does not have an appropriate 'ADVISOR FIRSTNAME' column"
    return OutputString

  if not 'poster #' in PosterDataframe.columns:
    OutputString += "\nERROR: Datafile "+InputAbstracts+" does not have an appropriate 'POSTER #' column"
    return OutputString

  if not 'title' in PosterDataframe.columns:
    OutputString += "\nERROR: Datafile "+InputAbstracts+" does not have an appropriate 'TITLE' column"
    return OutputString

  if not 'program' in PosterDataframe.columns:
    OutputString += "\nERROR: Datafile "+InputAbstracts+" does not have an appropriate 'PROGRAM' column"
    return OutputString


  

  # The posters are associated with their abstract easily. The next segments of code will be largely in service
  # of matching the professor names (as given in the judge document) to their data for abstract matching.

  # Generates full names for the judges (to be used when linking to their profiles)


  JudgeNames = []  
  for x in range(len(JudgesDataframe["judge firstname"])):
    JudgeNames.append(JudgesDataframe["judge firstname"][x]+" "+JudgesDataframe["judge lastname"][x])

  # Find the closest match between each judge and a slug, and associate that judge with the slug's data.
  ProfText = pandas.read_csv(InputCrawl)
  
  if (ProfText.empty):
    OutputString += "\nERROR: Please generate "+InputCrawl+" by running step 0."
    # print(OutputString)
    return OutputString
  
  ProfSlugList = ProfText["0"]
  ProfAbstrList = ProfText["1"]
  ProfessorsNameToData = {"NoNameFound" : ""}

  for currentJudge in JudgeNames:
    bestName = "NoNameFound"
    curAbstr = ""
    bestSimScore = 0
    bestslug = ""
    for i in range(len(ProfSlugList)):
      slug = ProfSlugList[i]
      sim = cosine_sim(slug, currentJudge)
      if (sim > bestSimScore):
        bestName = currentJudge
        curAbstr = ProfAbstrList[i]
        bestSimScore = sim
        bestslug = slug
      
    if bestName == "NoNameFound":
      OutputString += "\nERROR: no match found for judge name '"+currentJudge+"' from the list of judges extracted from Judge file. Check spelling."
    else:
      if (bestSimScore < 0.5): 
        OutputString += "\nWARNING: potential incorrect match. Weakly matched judge from Judges sheet '"+currentJudge+"' to data associated with judge '" + bestslug +"'."
      ProfessorsNameToData[bestName] = curAbstr


  # Determine which judges can judge a poster
  # Also records the compatibility between poster and judge.
  PosterPossibilities = []
  for PosterIndex,PosterRow in PosterDataframe.iterrows():
    PosterPossibilities.append([])
    for JudgeIndex,JudgeRow in JudgesDataframe.iterrows():
      
      isJudgeAvailable = True

      if JudgeRow['hour available'] != 1 and JudgeRow['hour available'] != 2:
        if JudgeRow['hour available'].lower() != 'both':
          OutputString = OutputString + "WARNING: Unexpected input '" + JudgeRow['hour available'] + "' for judge availability, in row "+JudgeIndex
          isJudgeAvailable = False
      elif JudgeRow['hour available'] == 1 and PosterIndex % 2 == 0:
          isJudgeAvailable = False
      elif JudgeRow['hour available'] == 2 and PosterIndex % 2 == 1:
          isJudgeAvailable = False

      if JudgeRow["judge firstname"] + JudgeRow["judge firstname"] == PosterRow["advisor firstname"] + PosterRow["advisor lastname"]:
        isJudgeAvailable = False

      if isJudgeAvailable:
        JudgName = JudgeRow["judge firstname"] +" "+ JudgeRow["judge lastname"]
        if JudgName in ProfessorsNameToData:
          JudgeSim = cosine_sim(ProfessorsNameToData[JudgName], PosterRow['abstract'])
        else:
          JudgeSim = 0
        PosterPossibilities[PosterIndex].append([JudgeSim, JudgName])# or JudgeIndex



  JudgePosters = {}
  for name in JudgeNames:
    JudgePosters[name] = []
  Judge1 = []
  Judge2 = []

  # Since each poster can only have 2 judges, and needs exactly 2, we'll iterate twice.
  # If this errors a lot, I can rewrite it so that we prioritize filling up posters
  # that are hard to fill - but I'm assuming we'll always have a generous amount of
  # judges, and that judges with limited schedules are not the norm.

  for Pindex,Poster in PosterDataframe.iterrows():
    simmax = 0
    judgenamemax = ""
    for tuple in PosterPossibilities[Pindex]:
      if len(JudgePosters[tuple[1]]) < 6 and tuple[0] > simmax:
        simmax = tuple[0]
        judgenamemax = tuple[1]
    if judgenamemax == "":
      OutputString += "\nWARNING: was unable to assign judge 1 for poster "+int(Pindex)+" (none available). Manual adjustment required."
    JudgePosters[judgenamemax].append(Poster["title"])
    Judge1.append(judgenamemax)

  for Pindex,Poster in PosterDataframe.iterrows():
    simmax = 0
    judgenamemax = ""
    for tuple in PosterPossibilities[Pindex]:
      if  len(JudgePosters[tuple[1]]) < 6 and tuple[0] > simmax and tuple[1] not in Judge1: # don't allow the same judge to judge a poster twice
        simmax = tuple[0]
        judgenamemax = tuple[1]
    if judgenamemax == "":
      OutputString += "\nWARNING: was unable to assign judge 2 for poster "+int(Pindex)+" (none available). Manual adjustment required."

    JudgePosters[judgenamemax].append(Poster["title"])
    Judge2.append(judgenamemax)
  
  num_cols = PosterDataframe.shape[1]
  PosterDataframe.insert(num_cols, "judge-1",Judge1)
  PosterDataframe.insert(num_cols+1, "judge-2",Judge2)

  # Convert the horizontal format of JudgePosters into a vertical format
  columns = {  0:[], 1:[], 2:[], 3:[], 4:[], 5:[]  }
  for judge in JudgePosters:
    for i in range(6):
      if i < len(JudgePosters[judge]):
        columns[i].append(JudgePosters[judge][i])
      else:
        columns[i].append("-")

  num_cols = JudgesDataframe.shape[1]
  JudgesDataframe.insert(num_cols, "poster-1", columns[0])
  JudgesDataframe.insert(num_cols+1, "poster-2", columns[1])
  JudgesDataframe.insert(num_cols+2, "poster-3", columns[2])
  JudgesDataframe.insert(num_cols+3, "poster-4", columns[3])
  JudgesDataframe.insert(num_cols+4, "poster-5", columns[4])
  JudgesDataframe.insert(num_cols+5, "poster-6", columns[5])


  # Create the third excel sheet

  JudgeToPoster = pandas.DataFrame(columns=JudgesDataframe['judge'])

  for Pindex,Poster in PosterDataframe.iterrows():
    onerow = []
    for Jindex, Judge in JudgesDataframe.iterrows():
      name = (Judge['judge firstname'] + " " + Judge['judge lastname'])
      if name == Poster['judge-1'] or name == Poster['judge-2']:
        onerow.append(1)
      else:
        onerow.append(0)
    JudgeToPoster.loc[len(JudgeToPoster)] = onerow

  JudgeToPoster.insert(0, "PosterIsVerticalJudgeIsHorizontal", PosterDataframe["poster #"])

  # Final error flag 
  if not NumberOfPosterTitlesOriginal == PosterDataframe['abstract'].count():
    OutputString += "ERROR: Mismatch in length of dataframes ("+NumberOfPosterTitlesOriginal+ " vs " + PosterDataframe['abstract'].count()+"). Poster(s) were dropped. Check input Poster file and ensure that all fields are filled."


  # Write all three dataframes to outputs.
  PosterDataframe.to_excel("OutputPoster.xlsx", index=False)
  JudgesDataframe.to_excel("OutputJudge.xlsx", index=False)
  JudgeToPoster.to_excel("OutputAdjacencyMatrix.xlsx", index=False)

  return OutputString