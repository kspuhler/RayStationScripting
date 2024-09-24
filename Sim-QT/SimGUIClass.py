"""
A class that provides a frontend for various automated plan creation scripts.

These are meant to be run during a virtual simulation at the sim but can be run 
anytime afterward

@author:Frontend class:                Joseph P. Santoro PhD
@author:Backend plan creation classes: Karl D. Spuhler
"""

try:
    from connect import *
except:
    pass

import sys

sys.path.append("\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
sys.path.append("F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")

"""Packages from Sim Templates that create plans for various sites"""
from Sim.Templates.Isocenters import Isocenters
from Sim.Templates.Pelvis import Pelvis, ProstateCK
from Sim.Templates.Breast import Breast
from Sim.Templates.HeadAndNeck import HeadAndNeck
from Sim.Templates.OpposedLats import OpposedLats
from Sim.Templates.BreastBilateral import BreastBilateral

from PyQt5.QtWidgets import QGroupBox,QSpinBox, QApplication,QMessageBox
from PyQt5.QtWidgets import QGridLayout, QWidget, QPushButton, QVBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from datetime import datetime


class SimInterfaceGUI(QWidget):
    """A GUI front-end for the SIM."""
    
    def __init__(self, *args):
        """Initialize an instance."""
        super().__init__()
        self.setWindowTitle('SIM Plan Chooser')
        self.resize(400, 350)  
        self.setToolTip(self.__doc__)

        self.layout = QGridLayout()
        self.selection = []
        self.numIso = 2
        
        self.buttonPanels()
        
        self.layout.addWidget(self.buttonGroupBox1,0,0)
        self.layout.addWidget(self.buttonGroupBox2,0,1)
        self.setLayout(self.layout)
        self.show()
        
    def makeTemplate(self, *args, **kwargs):
        """Connect each button to the appropriate plan creation script."""
        now = datetime.now()
        now = now.strftime('%m-%d-%y')
        pname = 'SIM' + now
        
        if self.selection == "Single Iso":
            tmp = Isocenters(numberOfIsocenters=1, planName = pname, beamSetName = 'SIM')
            
        elif  self.selection == "Multi Iso":
            tmp = Isocenters(numberOfIsocenters=self.numIso, planName = pname, beamSetName = 'SIM')
            
        elif  self.selection == "Lt Breast Tangents":
            tmp = Breast(2, 'left', pname, 'SIM')
            
        elif self. selection == "Lt Breast 3 Field": 
            tmp = Breast(3, 'left', pname, 'SIM')
            
        elif  self.selection == "Lt Breast 4 Field":
            tmp = Breast(4, 'left', pname, 'SIM')
            
        elif  self.selection == "Rt Breast Tangents":
            tmp = Breast(2, 'right', pname, 'SIM')
    
        elif  self.selection == "Rt Breast 3 Field": 
            tmp = Breast(3, 'right', pname, 'SIM')
            
        elif  self.selection == "Rt Breast 4 Field":
            tmp = Breast(4, 'right', pname, 'SIM')
            
        elif  self.selection == "Bilateral Breast":
            tmp = BreastBilateral(pname, 'SIM')
        
        elif  self.selection == "Pelvis":
            tmp = Pelvis(1, pname, 'SIM')
            
        elif  self.selection == "Prostate CK":
            tmp = ProstateCK(1, pname, 'SIM')
            
        elif  self.selection == "Head and Neck":
            tmp = HeadAndNeck(1, pname, 'SIM')
    
        elif  self.selection == "Opposed Lats":
            tmp = OpposedLats(numberOfIsocenters=self.numIso, planName = pname, beamSetName = 'SIM')
            
        return
    
    def buttonPanels(self, *args, **kwargs):
      """All the buttons, their layouts and their functions."""
      self.SingleIso = QPushButton('Single Iso')
      self.SingleIso.setToolTip('Creates a plan with a single isocenter')
      self.SingleIso.clicked.connect(self.clickBait)
      
      self.MultiIso  = QPushButton('Multi Iso') 
      self.MultiIso.setToolTip('Creates a plan with muliple isocenters')
      self.MultiIso.clicked.connect(self.clickBait)
      
      self.LtBrTang  = QPushButton('Lt Breast Tangents')
      self.LtBrTang.clicked.connect(self.clickBait)
      self.LtBr3Fld  = QPushButton('Lt Breast 3 Field')
      self.LtBr3Fld.clicked.connect(self.clickBait)
      self.LtBr4Fld  = QPushButton('Lt Breast 4 Field')
      self.LtBr4Fld.clicked.connect(self.clickBait)
      self.RtBrTang  = QPushButton('Rt Breast Tangents')
      self.RtBrTang.clicked.connect(self.clickBait)
      self.RtBr3Fld  = QPushButton('Rt Breast 3 Field')
      self.RtBr3Fld.clicked.connect(self.clickBait)
      self.RtBr4Fld  = QPushButton('Rt Breast 4 Field')
      self.RtBr4Fld.clicked.connect(self.clickBait)
      self.BilatBr   = QPushButton('Bilateral Breast')
      self.BilatBr.clicked.connect(self.clickBait)
      self.Pelvis    = QPushButton('Pelvis')
      self.Pelvis.clicked.connect(self.clickBait)
      self.ProsCK    = QPushButton('Prostate CK')
      self.ProsCK.clicked.connect(self.clickBait)
      self.HandN     = QPushButton('Head and Neck')
      self.HandN.clicked.connect(self.clickBait)
      self.OppLats   = QPushButton('Opposed Lats')
      self.OppLats.clicked.connect(self.clickBait)
      
      self.buttonGroupBox1 = QGroupBox('Breast Plans')
      self.buttonGroupBox2 = QGroupBox('General Plans')
      self.buttonLayout1 = QVBoxLayout()
      self.buttonLayout2 = QVBoxLayout()
      
      self.buttonLayout1.addWidget(self.LtBrTang), self.buttonLayout1.addWidget(self.LtBr3Fld),self.buttonLayout1.addWidget(self.LtBr4Fld)
      self.buttonLayout1.addWidget(self.RtBrTang), self.buttonLayout1.addWidget(self.RtBr3Fld),self.buttonLayout1.addWidget(self.RtBr4Fld)
      self.buttonLayout1.addWidget(self.BilatBr)
      self.buttonGroupBox1.setLayout(self.buttonLayout1)
      self.buttonLayout1.setAlignment(Qt.AlignTop)
      
      self.buttonLayout2.addWidget(self.SingleIso), self.buttonLayout2.addWidget(self.Pelvis)
      self.buttonLayout2.addWidget(self.ProsCK), self.buttonLayout2.addWidget(self.HandN)
      
      self.MultIsoNum = QSpinBox()
      self.MultIsoNum.setValue(2)
      self.MultIsoNum.setMinimum(2)
      self.MultIsoNum.setToolTip('Enter the number of Isocenters')
      self.MultIsoNum.valueChanged.connect(self.get_num_isos)
      
      self.numIsoGroupBox = QGroupBox('Multiple Isocenter Plans') 
      
      self.numIsoGroupBoxLayout = QVBoxLayout()
      self.numIsoGroupBoxLayout.addWidget(self.MultIsoNum)
      self.numIsoGroupBoxLayout.addWidget(self.MultiIso)
      self.numIsoGroupBoxLayout.addWidget(self.OppLats)
      
      self.numIsoGroupBox.setLayout(self.numIsoGroupBoxLayout)
      self.buttonLayout2.addWidget(self.numIsoGroupBox)
      self.buttonGroupBox2.setLayout(self.buttonLayout2)
      self.buttonLayout2.setAlignment(Qt.AlignTop)
      
      self.SingleIso.setFont(QFont('Times', 16))
      
      self.hightlightButtons()
      
    def clickBait(self, *args, **kwargs):
        """Make these buttons do stuff."""    
        sender = self.sender()
        print(f"Clicked button: {sender.text()}")
        self.selection = sender.text()
        try:
         self.makeTemplate()
         QApplication.quit()
        except Exception as err:
         print(f"Unexpected {err=}, {type(err)=}")
         self.error_handling(str(err))

    def get_num_isos(self, *args, **kwargs):
        """Get current value for number of isocenters.""" 
        self.numIso = self.MultIsoNum.value()
        print("Number of isocenters set to:",self.numIso)
        
       
    def hightlightButtons(self,*args,**kwargs):
        """Highlight the buttons when you mouse over them."""
        self.buttonGroupBox1.setStyleSheet("QPushButton::hover"
                             "{"
                             "background-color : grey;"
                             "}") 
        
        self.buttonGroupBox2.setStyleSheet("QPushButton::hover"
                             "{"
                             "background-color : grey;"
                             "}") 
        
    def error_handling(self, *args, **kwargs):
        """Error handling popup."""
        self.error_handle = QMessageBox()
        msg = args[0]
        self.error_handle.setIcon(QMessageBox.Critical)
        self.error_handle.setWindowTitle("Error")
        self.error_handle.setText(msg)
        self.error_handle.exec_()