"""
Calculate MVS for a selected structure.

Author: Joseph P. Santoro
"""
import numpy as np
import os as os

from PyQt5.QtWidgets import QApplication,QFileDialog,QGroupBox,QTabWidget, QLineEdit
from PyQt5.QtWidgets import QComboBox,QTableWidget,QTableWidgetItem,QHeaderView
from PyQt5.QtWidgets import QGridLayout,QVBoxLayout, QHBoxLayout, QWidget
from PyQt5.QtWidgets import QToolTip,QFrame, QLabel, QAbstractItemView
from PyQt5.QtWidgets import QToolBar, QCalendarWidget,QPushButton,QMessageBox
from PyQt5.QtGui import QIcon,QFont,QBrush,QColor
from PyQt5.QtCore import Qt
from connect import *

directory = "\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD"
file = '\\SantoroSleekStylesheet.css'
ss = directory+file
print('Using stylesheet:',ss)

def selectTreatmentPlan(*args, **kwargs):
    selected_plan = plan.currentIndex()
    print(Plans[selected_plan].Name)

def selectContour(*args, **kwargs):
    selected_contour = contours.currentIndex()
    contour_volume = round(Contours[selected_contour].GetRoiVolume(),2)
    print(Contours[selected_contour].OfRoi.Name)
    print('VOLUME:',contour_volume)
    data.setItem(0,0,QTableWidgetItem(str(contour_volume)))
   
def getD(*args, **kwargs):
   DEP = dose_const.text()
   print(DEP)
   data.setItem(0,1,QTableWidgetItem(DEP))
   DoseObject = Plans[plan.currentIndex()].TreatmentCourse.TotalDose
   EP_vol  = DoseObject.GetRelativeVolumeAtDoseValues(RoiName=Contours[contours.currentIndex()].OfRoi.Name, DoseValues=[int(DEP)])
   contour_volume = round(Contours[contours.currentIndex()].GetRoiVolume(),2)
   EP_vol = np.multiply(EP_vol,contour_volume)
   print(type(EP_vol))
   print(len(EP_vol))
   scalar = EP_vol[0]
   scalar = round(scalar,2)
   data.setItem(0,2,QTableWidgetItem(str(scalar)))
   CP_vol = contour_volume - scalar
   CP_vol = round(CP_vol,2)
   data.setItem(0,3,QTableWidgetItem(str(CP_vol)))
   print(EP_vol)
   print(scalar)
   
examination = get_current("Examination")
case = get_current("Case")

#### QT #####
app=QApplication(sys.argv)
wintest = QWidget()
wintest.setWindowTitle('Minimum Volume Spared (complementary volume) calculator')
wintest.resize(600, 300)  
stylesheet_file = open(ss,'r',encoding='utf-8')
stylesheet = stylesheet_file.read()
app.setStyleSheet(stylesheet)
app.setStyle('Fusion')

layout = QGridLayout()

data        = QTableWidget(objectName='Min Volume Spared')
contours    = QComboBox(objectName='Contours')
plan        = QComboBox(objectName='Plan')

dose_const = QLineEdit('0')
dose_const.setToolTip('Enter the Dose DVH endpoint in cGy')

data.setFrameStyle(QFrame.StyledPanel   | QFrame.Sunken)
data.setColumnCount(4)
data.setRowCount(1)
data.setHorizontalHeaderLabels(['Total Volume (cc)', 'Dose DVH Endpoint (cGy)', 'Volume (cc)','MVS (cc)'])
data.setEditTriggers(QAbstractItemView.NoEditTriggers)
data.resizeColumnToContents(0)
data.resizeColumnToContents(1)
data.resizeColumnToContents(2)
data.horizontalHeader().setStretchLastSection(True)
data.setVerticalHeaderLabels([''])

label1 = QLabel("Select a Plan")
label2 = QLabel("Select a Contour")
label4 = QLabel('Enter the Dose DVH endpoint in cGy')
###################################################################

PatientModel = case.PatientModel
StructureSet = PatientModel.StructureSets
Contours     = StructureSet[0].RoiGeometries
Plans        = case.TreatmentPlans

num_of_contours = len(Contours)
num_of_plans    = len(Plans)

for i in range(num_of_contours):
    name = Contours[i].OfRoi.Name
    if Contours[i].HasContours()==True:
     contours.insertItem(i,name)

for i in range(num_of_plans):
    name = Plans[i].Name
    plan.insertItem(i,name)

plan.activated.connect(selectTreatmentPlan)
contours.activated.connect(selectContour)
dose_const.returnPressed.connect(getD)

#######################################################
layout.addWidget(label1,0,0)
layout.addWidget(plan ,      1,0)

layout.addWidget(label2,2,0)
layout.addWidget(contours ,  3,0)

layout.addWidget(label4,4,0)
layout.addWidget(dose_const, 5,0)

layout.addWidget(data ,6,0)

wintest.setLayout(layout)
wintest.show()
app.exec()

