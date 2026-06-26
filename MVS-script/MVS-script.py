"""
Calculate MVS for a selected structure.

Author: Joseph P. Santoro
"""
import numpy as np

from PyQt5.QtWidgets import QApplication, QLineEdit
from PyQt5.QtWidgets import QComboBox, QTableWidget, QTableWidgetItem
from PyQt5.QtWidgets import QGridLayout, QWidget
from PyQt5.QtWidgets import QFrame, QLabel, QAbstractItemView
from connect import *

directory = "\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD"
file = '\\SantoroSleekStylesheet.css'
ss = directory + file
print('Using stylesheet:', ss)
global whichContour


def selectContour(*args, **kwargs):
    selected_contour = contours.currentText()
    contour_volume = round(Contours[selected_contour].GetRoiVolume(), 2)
    print('VOLUME:', contour_volume)
    data.setItem(0, 0, QTableWidgetItem(str(contour_volume)))
    global whichContour
    whichContour = selected_contour
    print("WHICH CONTOUR SELECTED?:", whichContour)


def getD(*args, **kwargs):
    print("We are determining MVS for:", args[0])
    DEP = dose_const.text()
    data.setItem(0, 1, QTableWidgetItem(DEP))
    DoseObject = plan.TreatmentCourse.TotalDose
    EP_vol = DoseObject.GetRelativeVolumeAtDoseValues(RoiName=args[0],
                                                      DoseValues=[int(DEP)])
    contour_volume = round(Contours[args[0]].GetRoiVolume(), 2)
    EP_vol = np.multiply(EP_vol, contour_volume)
    scalar = EP_vol[0]
    scalar = round(scalar, 2)
    data.setItem(0, 2, QTableWidgetItem(str(scalar)))
    CP_vol = contour_volume - scalar
    CP_vol = round(CP_vol, 2)
    data.setItem(0, 3, QTableWidgetItem(str(CP_vol)))


examination = get_current("Examination")
print('The current CT scan is:', examination.Name)
case = get_current("Case")
plan = get_current("Plan")

#### QT #####
app = QApplication(sys.argv)
wintest = QWidget()
wintest.setWindowTitle('Minimum Volume Spared (complementary volume) calculator')
wintest.resize(600, 300)
stylesheet_file = open(ss, 'r', encoding='utf-8')
stylesheet = stylesheet_file.read()
app.setStyleSheet(stylesheet)
app.setStyle('Fusion')

layout = QGridLayout()

data = QTableWidget(objectName='Min Volume Spared')
contours = QComboBox(objectName='Contours')

dose_const = QLineEdit('0')
dose_const.setToolTip('Enter the Dose DVH endpoint in cGy')

data.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)
data.setColumnCount(4)
data.setRowCount(1)
data.setHorizontalHeaderLabels(['Total Volume (cc)', 'Dose DVH Endpoint (cGy)', 'Volume (cc)', 'MVS (cc)'])
data.setEditTriggers(QAbstractItemView.NoEditTriggers)
data.resizeColumnToContents(0)
data.resizeColumnToContents(1)
data.resizeColumnToContents(2)
data.horizontalHeader().setStretchLastSection(True)
data.setVerticalHeaderLabels([''])

label2 = QLabel("Select a Contour")
label4 = QLabel('Enter the Dose DVH endpoint in cGy')
###################################################################

PatientModel = case.PatientModel
StructureSet = PatientModel.StructureSets
Contours = StructureSet[examination.Name].RoiGeometries

num_of_contours = len(Contours)

print('THERE ARE', num_of_contours, 'contours')
for i in range(num_of_contours):
    name = Contours[i].OfRoi.Name
    print('Checking contour', i, name)
    if Contours[i].HasContours() == True:
        print('Adding:', name, 'to the list\n')
        contours.insertItem(i, name)

contours.activated.connect(selectContour)
dose_const.returnPressed.connect(lambda: getD(whichContour))

#######################################################

layout.addWidget(label2, 1, 0)
layout.addWidget(contours, 2, 0)

layout.addWidget(label4, 3, 0)
layout.addWidget(dose_const, 4, 0)

layout.addWidget(data, 5, 0)

wintest.setLayout(layout)
wintest.show()
app.exec()
