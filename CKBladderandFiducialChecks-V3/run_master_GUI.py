"""
Created on Fri Feb 14 13:15:39 2025.

@author: santoj14
"""

import sys

sys.path.append("F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD\CKBladderandFiducialChecks-V3")
sys.path.append("\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD\CKBladderandFiducialChecks-V3")
ss = "\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD\CKBladderandFiducialChecks-V3\SantoroSleekStylesheet.css"

from CKsimulation_GUI import BladderTestGUI, FiducialTestGUI
from PyQt5.QtWidgets import QApplication

print('opening the gui')
app = QApplication(sys.argv)

stylesheet_file = open(ss,'r',encoding='utf-8')
stylesheet = stylesheet_file.read()

app.setStyleSheet(stylesheet)
app.setStyle('Fusion')

window = BladderTestGUI()
window.setGeometry(50,50,550, 400) 
window.show()

window2 = FiducialTestGUI()
window2.setGeometry(450,50,550, 700) 
window2.show()

app.exec_()

