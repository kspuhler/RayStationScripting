# -*- coding: utf-8 -*-
""" Front-end code for the setting the maximum MLC and Jaw position GUI.
The GUI allows the user to change a beam to a maximum MLC and Jaw size as determined by
another beam's MLC and Jaw settings.  The tool is helpful for reducing the size of beams,
when their optimized MLC and Jaws are larger than a givn limit often established by an 
initial physician's field shape.  Ex: Breast Tangents

Created on Tue Apr  1 09:10:43 2025

@author: clanco01
"""

import sys

sys.path.append("F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD\Set_Max_MLC_And_Jaws")
sys.path.append("\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD\Set_Max_MLC_And_Jaws")
ss = "\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD\SantoroSleekStylesheet.css"

from SetMaxBeamShape import SetMaxBeamShape
from PyQt5.QtWidgets import QApplication

print('------------ Executing startup script ----------------')
app = QApplication(sys.argv)
stylesheet_file = open(ss,'r',encoding='utf-8')
stylesheet = stylesheet_file.read()
app.setStyleSheet(stylesheet)
app.setStyle('Fusion')
window = SetMaxBeamShape()
window.show()
app.exec_()
print("End of script.  User cancelled or closed the window.")

