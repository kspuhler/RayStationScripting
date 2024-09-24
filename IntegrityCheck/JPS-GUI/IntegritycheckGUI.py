"""

Created on Fri Mar  8 14:25:54 2024.

@author: santoj14
"""
from PyQt5.QtWidgets import (QGroupBox,
                             QTabWidget,
                             QFileDialog,
                             QComboBox,
                             QTableWidget,
                             QTableWidgetItem,
                             QHeaderView,
                             QGridLayout, 
                             QWidget,
                             QToolTip,
                             QFrame, 
                             QLabel, 
                             QAbstractItemView,
                             QToolBar, 
                             QPushButton,
                             QMessageBox)
from PyQt5.QtGui import (QIcon,
                         QFont,
                         QBrush,
                         QColor, 
                         QPixmap)
from PyQt5.QtCore import Qt
import sys


class IntegrityCheckGUI(QWidget):
    """A GUI to determine fiducial implant quality."""
    
    def __init__(self, *args):   
        super().__init__()
        print('Initializing Integrity Check GUI')
        self.ok    = ":/icons/check3.png"
        self.notok = ":/icons/red-x2.png"
        self.message_tx=''
        self.fsRS = ''
        self.file_stringAria = ''
    
        self.resize(1300, 600) 
        self.setWindowTitle('Plan Data Integrity Check')
        self.layout = QGridLayout()
        
        createButtonBar(self)
        self.layout.addWidget(self.button_bar,0,0)
        
        self.patient_info_labels=['Patient','MRN','Raystation Plan Name','Aria/IDMS Plan Name']
                                  
        self.demographics_table  = QTableWidget(objectName='Patient and Plan Info')
        self.demographics_table.setFrameStyle(QFrame.StyledPanel   | QFrame.Sunken)
        self.demographics_table.setColumnCount(1)
        self.demographics_table.setRowCount(4)
        self.demographics_table.setVerticalHeaderLabels(self.patient_info_labels)
        self.demographics_table.setHorizontalHeaderLabels([''])
        
        self.demographics_table.horizontalHeader().setSectionResizeMode(0,QHeaderView.Stretch)
        
        self.layout.addWidget(self.demographics_table ,1,0)

        self.setLayout(self.layout)

    def openDICOM(self, *args):
         """OPEN A PLAN DICOM OBJECTS."""
         try: 
          self.dlgRS = QFileDialog().getOpenFileName(parent=self,
                                                 caption="Select a RayStation DICOM Plan File",
                                                 filter="*.dcm")
           
          print(self.dlgRS[0])
          fsRS = self.dlgRS[0] 
          self.demographics_table.setItem(2,0,QTableWidgetItem(fsRS))
           
          self.dlgAriaIDMS = QFileDialog().getOpenFileName(parent=self,
                                                    caption="Select a Aria/IDMS DICOM Plan File",
                                                    filter="*.dcm")
           
          fsAriaIDMS = self.dlgAriaIDMS[0]          
          self.demographics_table.setItem(3,0,QTableWidgetItem(fsAriaIDMS))
           
       
         except:
            self.file_stringAria=''
            fsRS=''
            fsAriaIDMS = ''
            print('RATPHARTZ')
            
def createButtonBar(self,*args):
    """Create a button bar."""
    self.button_bar = QToolBar()
    
    self.btn1 = QPushButton('')
    #self.btn1.clicked.connect(self.initializePrintObject)
    self.btn1.clicked.connect(self.openDICOM)
    self.btn1.setIcon(QIcon('icons/open.png'))
    self.btn1.setToolTip("Open a Raystation and an Aria plan DICOM file")
    self.button_bar.addWidget(self.btn1)
    
    self.btn2 = QPushButton('')
    self.btn2.setEnabled(False)
    #self.btn2.clicked.connect(lambda x: self.printDialog.makeReport())
    self.btn2.setIcon(QIcon('icons/print3.png'));
    self.btn2.setToolTip("Print a PDF report")
    self.button_bar.addWidget(self.btn2)
    
    self.btn3 = QPushButton('')
    #self.btn3.clicked.connect(self.closeAll)
    self.btn3.setIcon(QIcon('icons/close.png'))
    self.btn3.setToolTip("Close the Application")
    self.button_bar.addWidget(self.btn3)
    
    self.btn4 = QPushButton('')
    #self.btn4.clicked.connect(self.helpYoSelf)
    self.btn4.setIcon(QIcon('icons/help.png'))
    self.btn4.setToolTip("Help Me")
    self.btn4.toggle()
    self.button_bar.addWidget(self.btn4)
    

        
