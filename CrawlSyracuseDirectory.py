# Needs to be done only once per semester (in any case where the faculty would change)
# Will take a few minutes (4-5)

import requests;
from bs4 import BeautifulSoup as bs;
import pandas

import nltk 
nltk.download('punkt_tab')

from nltk.corpus import stopwords
nltk.download('stopwords')


from nltk.tokenize import word_tokenize
 
stop_words = set(stopwords.words('english'))

rootStaffDirectory = "https://ecs.syracuse.edu/faculty-staff/"

def CrawlForUser():

  page = requests.get(rootStaffDirectory) # get the HTML page
  soup = bs(page.content, features="html.parser") # put the HTML page into soup
  divs = soup.findAll("div", class_="profile-name") # get all the profile pictures

  ScrapedData = []

  for div in divs:
    linkname = div.find("a").get("href") # Get the link to the faculty page

    slug = linkname[len(rootStaffDirectory):].replace('-', ' ') # length of 'https://ecs.syracuse.edu/faculty-staff/', 
    print(slug)
      # gets the slug and replaces hyphens with spaces for matching later on

    page = requests.get(linkname) # get the HTML page for this professor
    soup = bs(page.content, features="html.parser") # put the HTML page into soup

    # the div 'entry-content' contains the content of the professor's faculty page.
    # In addition to some non-useful data, this contains interests and publications,
    # which should be useful for tokenizing. 
    # The selection is deliberately broad to capture as much data as possible w/out errors.

    data = str(soup.find("div", class_="entry-content").get_text())

    # We modify and strip down the data to only include meaningful words, removing stopwords and punctuation
    tokens = word_tokenize(data)
    tokens=[word.lower() for word in tokens if word.isalpha()]
    tokens = [w for w in tokens if not w.lower() in stop_words]
    data = " ".join(tokens)

    ScrapedData.append( [slug, data])

    

  # Write the data into a csv for future use

  df = pandas.DataFrame(ScrapedData)

  filepath = 'ProfessorInformation.csv'
  df.to_csv(filepath, index=False)

  return 0
