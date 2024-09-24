"""

Created on Sat Mar  9 07:44:46 2024.

@author: Joseph P. Santoro
"""

from IntegritycheckGUI import IntegrityCheckGUI
from PyQt5.QtWidgets import QApplication
import sys


if __name__ == '__main__':
    
    print('------------ Executing Integrity check startup script ----------------')
    app = QApplication(sys.argv)
    stylesheet_file = open('SantoroSleekStylesheet.css','r',encoding='utf-8')
    stylesheet = stylesheet_file.read()
    app.setStyleSheet(stylesheet)
    app.setStyle('Fusion')
    window = IntegrityCheckGUI()
    window.show()
    #sys.exit(app.exec_())