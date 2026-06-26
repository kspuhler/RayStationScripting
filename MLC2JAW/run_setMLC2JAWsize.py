"""
Created on Wed Aug 14 14:32:19 2024.
@author: Joseph P. Santoro
"""

import sys

sys.path.append("F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD\MLC2JAW")
sys.path.append("\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD\MLC2JAW")
ss = "\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD\SantoroSleekStylesheet.css"


from setMLC2JAWsizeGUIClass import setMLC2JAWGUI
from PyQt5.QtWidgets import QApplication
import sys

print('------------ Executing startup script ----------------')
app = QApplication(sys.argv)
stylesheet_file = open(ss,'r',encoding='utf-8')
stylesheet = stylesheet_file.read()
app.setStyleSheet(stylesheet)
app.setStyle('Fusion')
window = setMLC2JAWGUI()
window.show()
app.exec_()