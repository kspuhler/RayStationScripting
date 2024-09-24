"""
Created on Fri Mar  1 16:05:56 2024.

@author: Joseph P. Santoro
"""

import os
import sys

sys.path.append("F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD\CKBladderandFiducialChecks")
sys.path.append("\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD\CKBladderandFiducialChecks")
ss = "\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD\CKBladderandFiducialChecks\SantoroSleekStylesheet.css"


from CKsimulation_GUI import BladderTestGUI
from PyQt5.QtWidgets import QApplication
import sys

print('------------ Executing startup script ----------------')
app = QApplication(sys.argv)
stylesheet_file = open(ss,'r',encoding='utf-8')
stylesheet = stylesheet_file.read()
app.setStyleSheet(stylesheet)
app.setStyle('Fusion')
window = BladderTestGUI()
window.show()
app.exec_()
          