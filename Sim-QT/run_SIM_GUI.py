"""
Raystation script:CT SIM Script.

A main script to run SIM GUI application.

Created on Wed Sep  4 15:03:55 2024.
@author: Joseph P. Santoro
"""

import sys

sys.path.append("\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD\Sim-QT")
ss = "\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD\SantoroSleekStylesheetSIM.css" 

from SimGUIClass import SimInterfaceGUI
from PyQt5.QtWidgets import QApplication
import sys

print('------------ Executing startup script ----------------')
app = QApplication(sys.argv)
stylesheet_file = open(ss,'r',encoding='utf-8') 
stylesheet = stylesheet_file.read()
app.setStyleSheet(stylesheet)
app.setStyle('Fusion')
window = SimInterfaceGUI()
window.show()
app.exec_()
