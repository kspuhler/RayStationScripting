"""
GUIs for bladder and fiducial testing containing 2 GUI classes.

This contains two GUI classes; the bladder filling check GUI and
the fiducial integrity check GUI
Created on Thu Feb 29 10:25:51 2024.

@author: santoj14.
"""



from CKsimulationClass import CKsimulation

from PyQt5.QtWidgets import (QGroupBox,
                             QTabWidget,
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
sys.path.append("F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD\CKBladderandFiducialChecks")
sys.path.append("\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD\CKBladderandFiducialChecks")

"""THIS IS THE BLADDER FILLING GUI"""

class BladderTestGUI(QWidget,CKsimulation):
    """A GUI to display Bladder filling metrics and quality."""
    
    def __init__(self, *args):   
        super().__init__()

        print('initializing bladder GUI')
        self.ok    = "\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD\CKBladderandFiducialChecks\check3.png"
        self.notok = "\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD\CKBladderandFiducialChecks\checkNG.png"
        self.warn  = "\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD\CKBladderandFiducialChecks\exclimation.png"
        
        self.createFiducialROI()
        self.findFiducials()
        self.insertFiducialMarkers()
        self.deleteFiducialROI()
        
        self.resize(300, 150)  
        self.setWindowTitle('CK Bladder Filling Check')
        
        self.layout = QGridLayout()
        self.table  = QTableWidget(objectName='Bladder and Prostate Statistics')
        self.table.setFrameStyle(QFrame.StyledPanel   | QFrame.Sunken)
        self.table.setColumnCount(3)
        self.table.setRowCount(3)
        self.table.setColumnWidth(2, 10)
        
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setHorizontalHeaderLabels(['Organ', 'Volume (cc)', ''])

        self.testThisBladder()
        
        self.layout.addWidget(self.table ,0,0)
        self.setLayout(self.layout)
    
    def testThisBladder(self, *args, **argv):
        """Populate the GUI with some data and test the bladder filling."""
        Bladder_volume  = round(self.Bladder_volume,2)
        Prostate_volume = round(self.Prostate_volume,2)
        Ratio           = round(self.Ratio,2)
        
        self.table.setItem(0,0,QTableWidgetItem('Bladder'))
        self.table.setItem(1,0,QTableWidgetItem('Prostate'))
        self.table.setItem(2,0,QTableWidgetItem('Ratio'))
        self.table.setItem(0,1,QTableWidgetItem(str(Bladder_volume)))
        self.table.setItem(1,1,QTableWidgetItem(str(Prostate_volume)))
        self.table.setItem(2,1,QTableWidgetItem(str(Ratio)))
        
        if Bladder_volume>=250. and Ratio>=2.0:
         oklabel = QLabel()
         oklabel.setText("")
         oklabel.setScaledContents(True)
         pixmap = QPixmap()
         pixmap.load(self.ok,'.png')
         pixmap = pixmap.scaledToWidth(50)
         oklabel.setPixmap(pixmap)
         self.table.setCellWidget(0,2,oklabel)
        elif Bladder_volume>=250 or Ratio>=1.5:
          notoklabel = QLabel()
          notoklabel.setText("")
          notoklabel.setScaledContents(True)
          pixmap2 = QPixmap()
          pixmap2.load(self.warn,'.png')
          pixmap2 = pixmap2.scaledToWidth(100)
          notoklabel.setPixmap(pixmap2)
          self.table.setCellWidget(0,2,notoklabel)
        else:
         notoklabel = QLabel()
         notoklabel.setText("")
         notoklabel.setScaledContents(True)
         pixmap2 = QPixmap()
         pixmap2.load(self.notok,'.png')
         pixmap2 = pixmap2.scaledToWidth(100)
         notoklabel.setPixmap(pixmap2)
         self.table.setCellWidget(0,2,notoklabel)    
        
        self.layout.addWidget(self.table ,0,0)
        self.setLayout(self.layout)
        
"""THIS IS THE FIDUCIAL INTEGRITY GUI"""

class FiducialTestGUI(QWidget,CKsimulation):
    """A GUI to determine fiducial implant quality."""
    
    def __init__(self, *args):   
        super().__init__()
        print('initializing fiducial GUI')
        self.ok    = "\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD\CKBladderandFiducialChecks\check3.png"
        self.notok = "\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD\CKBladderandFiducialChecks\checkNG.png"
        self.warn  = "\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD\CKBladderandFiducialChecks\exclimation.png"
        self.message_tx=''
        
        
        self.getFiducialCoordinates()
        self.calculateFiducialSpacings()
        self.calculateFiducialAngles()
        self.minAngleTest()
        self.num_fiducials = self.count_fiducials()
    
        self.resize(1400, 900)  
        self.setWindowTitle('CK Fiducial Integrity Check')
        self.layout = QGridLayout()
    
        self.fiddata   = QTableWidget(objectName='Fiducial Data')
        self.fidspace  = QTableWidget(objectName='Fiducial Spacing')
        self.fidangles = QTableWidget(objectName='Minimum Angle Test') 

        self.messages = QLabel()
        #messages.setStyleSheet('background-color: gray')
        self.messages.setFrameStyle(QFrame.StyledPanel   | QFrame.Sunken)
        self.messages.setAlignment(Qt.AlignTop)
        self.messages.setText('This is a test')

        self.fiddata.setFrameStyle(QFrame.StyledPanel   | QFrame.Sunken)
        self.fidspace.setFrameStyle(QFrame.StyledPanel  | QFrame.Sunken)
        self.fidangles.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)

        self.fiddata.setColumnCount(4)
        self.fidspace.setColumnCount(3)
        self.fidangles.setColumnCount(3)
        self.fiddata.horizontalHeader().setStretchLastSection(True)
        self.fiddata.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.fidspace.setColumnWidth(2, 10)
        self.fidspace.horizontalHeader().setSectionResizeMode(0,QHeaderView.Stretch)
        self.fidspace.horizontalHeader().setSectionResizeMode(1,QHeaderView.Stretch)

        self.fidangles.setColumnWidth(2, 10)
        self.fidangles.horizontalHeader().setSectionResizeMode(0,QHeaderView.Stretch)
        self.fidangles.horizontalHeader().setSectionResizeMode(1,QHeaderView.Stretch)
        
    #theFont = QFont("Tahoma", 13, QFont.Bold)
        self.fiddata.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.fiddata.setHorizontalHeaderLabels(['Name', 'X (cm)', 'Y (cm)', 'Z (cm)'])
        self.fidspace.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.fidspace.setHorizontalHeaderLabels(['Fiducial Combination', 'Spacing (cm)', ''])
    #fidspace.verticalHeader().setDefaultSectionSize(70)
        self.fidangles.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.fidangles.setHorizontalHeaderLabels(['Angle btwn. segments', 'Angle (degrees)', ''])        
    #def addLayout (arg__1, row, column, rowSpan, columnSpan[, alignment=Qt.Alignment()])
    
        setFiducialInformation(self)
        setFiducialSpacingInfo(self)
        setFiducialAngleInfo(self)
        
        self.layout.addWidget(self.fiddata  ,0,0,2,1)
        self.layout.addWidget(self.fidangles,2,0,6,1)
        self.layout.addWidget(self.fidspace ,7,0,3,1)
        self.layout.addWidget(self.messages ,0,1,10,1)

        self.setLayout(self.layout)

def setFiducialInformation(self,*args):
    """Display fiducial names and coordinates."""
    self.fiddata.setRowCount(self.num_fiducials)
    
    for i in range (0,self.num_fiducials):

        x = round( self.coord_np[i][0],3)
        y = round( self.coord_np[i][1],3)
        z = round( self.coord_np[i][2],3)
        pt_name = self.names_np[i]
        
        self.fiddata.setItem(i,0,QTableWidgetItem(pt_name))
        self.fiddata.setItem(i,1,QTableWidgetItem(str(x)))
        self.fiddata.setItem(i,2,QTableWidgetItem(str(y)))
        self.fiddata.setItem(i,3,QTableWidgetItem(str(z)))
        
def setFiducialSpacingInfo(self, *args):
    """Display N distances bewteen M fiducials."""
    num_pairs=len(self.name_pairs)
    self.fidspace.setRowCount(num_pairs)
    
    for i in range(0, num_pairs):
        name     = str(self.name_pairs[i])
        name = name.replace('[','').replace('\'','').replace(']','')
        distance = self.pair_distance[i]
        
        self.fidspace.setItem(i,0,QTableWidgetItem(str(name)))
        self.fidspace.setItem(i,1,QTableWidgetItem(str(distance)))
        
        if distance >= 2.0:
          oklabel = QLabel()
          oklabel.setText("")
          oklabel.setScaledContents(True)
          pixmap = QPixmap()
          pixmap.load(self.ok,'.png')
          pixmap = pixmap.scaledToWidth(100)
          oklabel.setPixmap(pixmap)
          self.fidspace.setCellWidget(i,2,oklabel)
        else:
          warninglabel = QLabel()
          warninglabel.setText("")
          warninglabel.setScaledContents(True)
          pixmap = QPixmap()
          pixmap.load(self.warn,'.png')
          warninglabel.setPixmap(pixmap)
          self.fidspace.setCellWidget(i,2,warninglabel)
          self.message_tx+=('The spacing between fiducials: '+ str(name)+' is less than 2cm\n\n')
          self.messages.setText(self.message_tx)
        
def setFiducialAngleInfo(self,*args):
    """Display the K angles between L connected 3-point (fiducial) segments.""" 
    self.fidangles.setRowCount(1)
    rowPosition = 0
    num_angs = len(self.angle_names_formatted)
             
    for i in range (0,num_angs):
      ang_name = self.angle_names_formatted[i]
      angle    = self.angles[i]
      self.fidangles.setItem(rowPosition,0,QTableWidgetItem(ang_name))
      self.fidangles.setItem(rowPosition,1,QTableWidgetItem(str(angle)))
    
      if (angle >= 15.0) and (angle<=165.0):
       oklabel = QLabel()
       oklabel.setText("")
       oklabel.setScaledContents(True)
       pixmap = QPixmap()
       pixmap.load(self.ok,'.png')
       pixmap = pixmap.scaledToWidth(100)
       oklabel.setPixmap(pixmap)
   
       self.fidangles.setCellWidget(rowPosition,2,oklabel)
       rowPosition = self.fidangles.rowCount()
       self.fidangles.insertRow(rowPosition)
     
       self.message_tx+=('Angle: ' + str(rowPosition)+' passes the minimum angle requirement\n')
       self.messages.setText(self.message_tx)
     
      else:
       notoklabel = QLabel()
       notoklabel.setText("")
       notoklabel.setScaledContents(True)
       pixmap = QPixmap()
       pixmap.load(self.notok,'.png')
       notoklabel.setPixmap(pixmap)
     
       self.fidangles.setCellWidget(rowPosition,2,notoklabel)
       rowPosition = self.fidangles.rowCount()
       self.fidangles.insertRow(rowPosition)
     
       self.message_tx+=('The angle formed by fiducials:\n'+ str(ang_name)+'\n does not pass the minimum angle requirement\n\n')
       self.messages.setText(self.message_tx)

