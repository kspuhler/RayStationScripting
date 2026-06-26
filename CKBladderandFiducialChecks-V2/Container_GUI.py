"""
GUIs for bladder and fiducial testing containing 2 GUI classes.

This contains two GUI classes; the bladder filling check GUI and
the fiducial integrity check GUI
Created on Thu Feb 29 10:25:51 2024.

@author: santoj14.
"""

from CKsimulation_GUI import BladderTestGUI, FiducialTestGUI

from PyQt5.QtWidgets import (
                               QGridLayout, 
                               QWidget,
                               QLabel,
                               )

from PyQt5.QtGui import (QFont)

class ContainerGUI(QWidget):
    """Master GUI."""
    
    def __init__(self, *args):   
        super().__init__()
    
        self.setGeometry(50,50,950, 750)  
        self.setWindowTitle('Bladder Filling and Fiducial Implant Checker')
        self.layout = QGridLayout()
        
        self.bladder_checker  = BladderTestGUI()
        self.fiducial_checker = FiducialTestGUI()
        self.fiducial_checker.playButton.clicked.connect(self.put_baby_in_the_corner)
        
        self.label1  = QLabel("Bladder Filling Checker")
        self.label2  = QLabel("Fiducial Integrity Checker")
        font = QFont()
        font.setCapitalization(True)
        font.setBold(True)
        
        self.label1.setFont(font)
        self.label2.setFont(font)
        self.label1.setStyleSheet("border: 1px solid white;") # Set border style
        self.label2.setStyleSheet("border: 1px solid white;") # Set border style
        
        self.layout.addWidget(self.label1,           0,0)
        self.layout.addWidget(self.label2,           0,1)
        self.layout.addWidget(self.bladder_checker , 1,0)
        self.layout.addWidget(self.fiducial_checker ,1,1)
       
        self.setLayout(self.layout)
        
        
    def put_baby_in_the_corner(self, *args):
        """Send window to back."""
        self.lower()
        print('PLAY BUTTON WAS CLICKED IN CONTAINER GUI')
        