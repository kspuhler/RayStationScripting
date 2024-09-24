"""
Created on Thu Feb 22 09:04:05 2024.

@author: Joseph P. Santoro.
"""

import sys
import os

sys.path.append("F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD\CKBladderandFiducialChecks")
sys.path.append("\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD\CKBladderandFiducialChecks")
ss = "\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD\CKBladderandFiducialChecks\SantoroSleekStylesheet.css"

from CKsimulation_GUI import FiducialTestGUI
from PyQt5.QtWidgets import QApplication



print('opening the gui')
app = QApplication(sys.argv)
stylesheet_file = open(ss,'r',encoding='utf-8')
stylesheet = stylesheet_file.read()
app.setStyleSheet(stylesheet)
app.setStyle('Fusion')
window = FiducialTestGUI()
window.show()
app.exec_()
