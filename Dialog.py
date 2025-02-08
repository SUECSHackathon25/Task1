# This file controls the UI of the code: thus, don't worry too much about
# what happens in here.

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import os
import time
import ctypes

from MatchCode import PerformMatch
from CrawlSyracuseDirectory import CrawlForUser

myappid = 'postermatcher.syr.v01'
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)


script_path = __file__
base_path = os.path.dirname(script_path)

def getLastUpdatedAuxData():
  if (os.path.exists(base_path +"/ProfessorInformation.csv")):
    pathn = base_path +"/ProfessorInformation.csv"
    return time.ctime(os.path.getmtime(pathn))
  
def getLastUpdatedAuxDataWeeksAgo():
  if (os.path.exists(base_path +"/ProfessorInformation.csv")):
    pathn = base_path +"/ProfessorInformation.csv"
    return (time.time() - os.path.getmtime(pathn) ) / 604800
  


if hasattr(Qt, 'AA_EnableHighDpiScaling'):
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)

if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)


heading = QFont("Arial", 12)
bodyfont = QFont("Arial", 10)
littlefont = QFont("Arial", 6)
bodyfontbold = QFont("Arial", 10)
bodyfontbold.setBold(True)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowIcon(QIcon('go-orange.png'))
        self.setWindowTitle("Poster Matching")
        self.setFixedWidth(600)
        self.setFixedHeight(400)

        ctr = QFrame()
        self.setCentralWidget(ctr)
        layout = QVBoxLayout()
        ctr.setLayout(layout)
        
        firststeplabel = QLabel("Step 1: Get Auxiliary Data")
        firststeplabel.setFont(heading)
        layout.addWidget(firststeplabel)

        firststeptext = QLabel("If no data is found, or if it is sufficiently out of date (i.e. not from this semester), matching data must be fetched. This process will take 3-5 minutes, dependent on internet speed. This generates a file called ProfessorInformation.csv which must be present for step 2. If you have done this step recently, no need to repeat it.")
        firststeptext.setWordWrap(True)
        firststeptext.setFont(bodyfont)
        layout.addWidget(firststeptext)

        firststeptextw = QLabel("This window will not respond until this process is complete.")
        firststeptextw.setFont(bodyfontbold)
        layout.addWidget(firststeptextw)

        firststepbutton = QPushButton("Get/Update Data")
        firststepbutton.setFont(bodyfont)
        def DoCrawl():
            try:
              result = CrawlForUser()
              if result == 0:
                firststepbutton.setStyleSheet('background-color : green')
                firststepoutput.setText("Data updated successfully. Last updated: "+str(getLastUpdatedAuxData()))
              else:
                firststepbutton.setStyleSheet('background-color : yellow')
                firststepoutput.setText("There was an error while fetching data. Please try again or consult the README.")
            except:
                firststepbutton.setStyleSheet('background-color : red')
               
                
            
        firststepbutton.clicked.connect(DoCrawl)
        layout.addWidget(firststepbutton)

        firststepoutput = QLabel("")
        firststepoutput.setFont(littlefont)
        layout.addWidget(firststepoutput)

        if getLastUpdatedAuxData() != 0:
           firststepoutput.setText("Existing data found. Last updated: "+str(getLastUpdatedAuxData()) + " (approx. " + str(round(getLastUpdatedAuxDataWeeksAgo())) + " weeks ago)")
           if round(getLastUpdatedAuxDataWeeksAgo()) > 8:
             firststepoutput.setStyleSheet('background-color : yellow')
        else:
           firststepoutput.setText("No data found.")
           
        


        
        firststeplabel = QLabel("\nStep 2: Perform Matching")
        firststeplabel.setFont(heading)
        layout.addWidget(firststeplabel)

        fileselect1 = QHBoxLayout()
        selectbutton1 = QPushButton("Select Judge File")
        selectedfile1 = QLabel("None")

        def selectFile1():
            selectedfile1.setText(QFileDialog.getOpenFileName()[0])
            if selectedfile1.text() == "" :
              selectedfile1.setText("None")

        selectbutton1.clicked.connect(selectFile1)

        fileselect1.addWidget(selectbutton1)
        fileselect1.addWidget(selectedfile1)
        fileselect1.addStretch()

        layout.addLayout(fileselect1)


        fileselect2 = QHBoxLayout()
        selectbutton2 = QPushButton("Select Poster Data File")
        selectedfile2 = QLabel("None")

        
        def selectFile2():
            selectedfile2.setText(QFileDialog.getOpenFileName()[0])
            if selectedfile2.text() == "" :
              selectedfile2.setText("None")

        selectbutton2.clicked.connect(selectFile2)

        fileselect2.addWidget(selectbutton2)
        fileselect2.addWidget(selectedfile2)
        fileselect2.addStretch()

        layout.addLayout(fileselect2)

        selectbutton1.setFont(bodyfont)
        selectbutton2.setFont(bodyfont)
        selectedfile1.setFont(littlefont)
        selectedfile2.setFont(littlefont)

        secondsteptext = QLabel("Select the two input .xlsx files and generate three output files for input to the judging website. This process may take a few minutes, and the window will be unresponsive whilst running. If you don't see any .xlsx output files, move this .exe and the .csv file out of your Downloads and try again. For any errors, consult the README. The output files will be in the directory: \n"+base_path)
        secondsteptext.setWordWrap(True)
        secondsteptext.setFont(bodyfont)
        layout.addWidget(secondsteptext)

        secondstepbutton = QPushButton("Generate Matches")
        secondstepbutton.setFont(bodyfont)

        outputstr2 = QLabel("")
        outputstr2.setFont(littlefont)

        def PerformMatchOnData():
            outputstr2.setText( PerformMatch(selectedfile2.text(), selectedfile1.text()))
            
            if outputstr2.text() == "":
                secondstepbutton.setStyleSheet('background-color : green')
                outputstr2.setText("Files are contained within " +base_path + " .")
            elif "ERROR" in outputstr2.text():
                secondstepbutton.setStyleSheet('background-color : red')
            else:
                secondstepbutton.setStyleSheet('background-color : yellow')

        secondstepbutton.clicked.connect(PerformMatchOnData)
        layout.addWidget(secondstepbutton)
        layout.addWidget(outputstr2)

        layout.addStretch()

app = QApplication([])
window = MainWindow()
window.show()
app.exec()
