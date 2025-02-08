This requires Python 3 and the following modules: requests, beautiful soup 4, pandas, nltk, pyqt, pandas, openpyxl, sklearn. But in a final version, this can be exported to a .exe file to be run by an administrator with little technical know-how.

A green button after clicking means that the output was produced successfully. A yellow output means that a reasonably correct output was
achieved, but you should check it for accuracy. A red output means that the output, if any, is likely not usable.

If you're running into errors:

* Manually check the output files -- if you are getting only WARNINGs, particularly only "Potential incorrect match", then the output is probably usable.
* Check that the input files match the format described below.
* Check the input files for typos.
* If you're not seeing any output files but the button is green, move this executable onto the desktop, and/or disable antivirus -- Google for more information, this is out of the program's control.



Input files

All column names are case insensitive. However, they are sensitive to punctuation and spacing. Due to time constraints, trailing whitespace will also trigger an error.
The input files must be .xlsx, with one sheet per file containing the proper information.
First and last name must be in separate columns.
The input file of judge information must have columns with the titles of "Judge Firstname" and "Judge Lastname"; "Hour available" which can contain the values 1, 2, or both; "Judge", which must contain numbers 1 to the number of judges; and "Department", whose entries must not be blank but are not important to the execution, and any blank entries can be filled with a -.
The input file of abstract information must have at least the columns "Advisor Firstname", "Advisor Lastname", "Title", "Poster #", and "Abstract". 
Please ensure that all cells contain information -- if necessary, hyphens (-) can fill empty cells.


Errors and Warnings

Step 0:
If Step 0 fails, either the search program was interrupted prematurely or some external factor prohibited it from acquiring data properly -- Syracuse blocking crawlers, internet connectivity issues, or antivirus/OS blocking internet access. 

'Issue with data file' -- must be fixed. The specified file could not be found. Try moving the file into the same directory as the executable and try again.
'Datafile does not have appropriate column' -- must be fixed. The file is lacking a column which is required for this code. You will need to acquire this data.
'Please generate InputCrawl' -- must be fixed. Run Step 1 successfully to resolve. 
'No match found for judge' -- should be fixed. This typically indicates a typo in the Judge file that should be fixed. This practically means that the judge will not be assigned to judge any posters.
'Potential incorrect match' -- if the two names are the same person, this error is OK. Check for typos. Otherwise, this means that this judge will be assigned potentially less accurately, but this is not fatal.
'Mismatch in length of dataframes' -- must be fixed. this happens if there are too many empty cells in a row in the Poster input, and thus a poster is removed. Find the offending row and fill in cells.
'Unexpected input for judge availability' -- the judge availability is not 1, 2, or 'both'. Correct manually, otherwise the judge will not be included.
'Was unable to match judge' -- this means that no judges were found available to judge this poster, and the output will need to be corrected manually in order to ensure that the poster is properly judged.