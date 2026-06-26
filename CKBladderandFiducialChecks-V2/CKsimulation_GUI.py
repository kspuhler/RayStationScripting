"""
GUIs for bladder and fiducial testing containing 2 GUI classes.

This contains two GUI classes; the bladder filling check GUI and
the fiducial integrity check GUI
Created on Thu Feb 29 10:25:51 2024.

@author: santoj14.
"""

from CKsimulationClass import CKsimulation

from connect import await_user_input

from PyQt5.QtWidgets import (QGroupBox,
                             QComboBox,
                             QTableWidget,
                             QTableWidgetItem,
                             QHeaderView,
                             QGridLayout,
                             QHBoxLayout,
                             QVBoxLayout,
                             QWidget,
                             QFrame, 
                             QLabel, 
                             QAbstractItemView,
                             QToolBar, 
                             QPushButton,
                             QMessageBox,
                             QApplication
                             )

from PyQt5.QtGui import (QIcon, QPixmap)

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
        
        self.play = "\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD\CKBladderandFiducialChecks-V2\play2.jpg"
        self.info = "\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD\CKBladderandFiducialChecks-V2\info.png"
         
        self.setWindowTitle('CK Bladder Filling Check')
        
        self.IsTargetSelected  = 0
        self.IsBladderSelected = 0
        print(self.IsBladderSelected*self.IsTargetSelected)
        
        self.layout = QGridLayout()
        
        self.button_bar = QToolBar()
        
        self.playButton = QPushButton("")
        self.playButton.setDisabled(True)
        self.icon = QIcon(self.play)
        self.playButton.setIcon(self.icon)
        self.button_bar.addWidget(self.playButton)
        self.playButton.clicked.connect(self.testThisBladder)
        
        self.infoButton = QPushButton("")
        self.icon2 = QIcon(self.info)
        self.infoButton.setIcon(self.icon2)
        self.button_bar.addWidget(self.infoButton)
        self.infoButton.clicked.connect(self.helpMe)
        
        self.label1  = QLabel("Select a GTV Structure")
        self.label2 = QLabel("Select a Bladder Structure")
        self.Targets  = QComboBox(objectName='Targets')
        self.Critical = QComboBox(objectName='Critical')
        self.Targets.textActivated.connect(self.select_Target)
        self.Critical.textActivated.connect(self.select_Bladder)
        
        for i,j in enumerate(self.contour_list):
            self.Targets.insertItem(i,self.contour_list[i])
            self.Critical.insertItem(i,self.contour_list[i])
            
        self.dropDownGroupBox = QGroupBox('')
        self.dropDownLayout = QHBoxLayout()
        self.dropDownLayout.addWidget(self.Targets)
        self.dropDownLayout.addWidget(self.Critical)
        self.dropDownGroupBox.setLayout(self.dropDownLayout)
        
        self.labelGroupBox = QGroupBox('')
        self.labelLayout = QHBoxLayout()
        self.labelLayout.addWidget(self.label1)
        self.labelLayout.addWidget(self.label2)
        self.labelGroupBox.setLayout(self.labelLayout)
        
        self.table  = QTableWidget(objectName='Bladder and Prostate Statistics')
        self.table.setFrameStyle(QFrame.StyledPanel   | QFrame.Sunken)
        self.table.setColumnCount(3)
        self.table.setRowCount(3)
        self.table.setColumnWidth(2, 10)
        
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setHorizontalHeaderLabels(['Organ', 'Volume (cc)', 'Status'])
       
        self.layout.addWidget(self.button_bar,0,0)
        self.layout.addWidget(self.labelGroupBox,1,0)
        self.layout.addWidget(self.dropDownGroupBox,2,0)
       
        self.layout.addWidget(self.table ,3,0)
        self.setLayout(self.layout)
        
    def select_Target(self,*args):
        """Select a target contour from the dropdown."""
        self.selected_Target = self.Targets.currentText()
        print('Target is:',self.selected_Target)
        self.IsTargetSelected = 1
        if self.IsTargetSelected*self.IsBladderSelected==1:
            self.playButton.setDisabled(False)
               
    def select_Bladder(self, *args):
        """Select a Bladder contour from the dropdown."""
        self.selected_Bladder = self.Critical.currentText()
        print('Bladder is:',self.selected_Bladder)
        self.IsBladderSelected = 1
        if self.IsTargetSelected*self.IsBladderSelected==1:
            self.playButton.setDisabled(False)
    
    def bladder_check(self, *args):
        """
        Check of prostate GTV and bladder contours exist.
        
        Then calculate stats.
        """
        if (self.selected_Bladder in self.contour_list) and (self.Contours[self.selected_Bladder].HasContours() == True) and (
            self.selected_Target in self.contour_list and self.Contours[self.selected_Target].HasContours() == True):
            self.Bladder_volume = round(self.Contours[self.selected_Bladder].GetRoiVolume(), 2)
            self.Prostate_volume = round(self.Contours[self.selected_Target].GetRoiVolume(), 2)
            self.Ratio = round(self.Bladder_volume / self.Prostate_volume, 2)
      
    def testThisBladder(self, *args, **argv):
        """Populate the GUI with some data and test the bladder filling."""
        self.bladder_check()
        
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
         
        elif (Bladder_volume<250 and Ratio>2.0) or (Bladder_volume>250 and Ratio<2.0):
          notoklabel = QLabel()
          notoklabel.setText("")
          notoklabel.setScaledContents(True)
          pixmap2 = QPixmap()
          pixmap2.load(self.warn,'.png')
          pixmap2 = pixmap2.scaledToWidth(100)
          notoklabel.setPixmap(pixmap2)
          self.table.setCellWidget(0,2,notoklabel)
          
        elif Bladder_volume<250 and Ratio<2.0:
         notoklabel = QLabel()
         notoklabel.setText("")
         notoklabel.setScaledContents(True)
         pixmap2 = QPixmap()
         pixmap2.load(self.notok,'.png')
         pixmap2 = pixmap2.scaledToWidth(100)
         notoklabel.setPixmap(pixmap2)
         self.table.setCellWidget(0,2,notoklabel)
    
    def helpMe(self, *args):
        """More information about the app."""
        self.BladderInfo = QMessageBox()
        self.BladderInfo.setWindowTitle("Bladder App Information")
        
        bladder_label_1T = QLabel("If the bladder volume >= 250cc AND the ratio of the Bladder to the GTV Volume is >= 2.0")
        bladder_label_1P = QLabel()
        pixmap = QPixmap()
        pixmap.load(self.ok,'.png')
        pixmap = pixmap.scaledToWidth(50)
        bladder_label_1P.setPixmap(pixmap)
        
        bladder_label_2T = QLabel("If the bladder volume <250cc OR the ratio of the Bladder to the GTV Volume is < 2.0")
        bladder_label_2P = QLabel()
        pixmap2 = QPixmap()
        pixmap2.load(self.warn,'.png')
        pixmap2 = pixmap2.scaledToWidth(50)
        bladder_label_2P.setPixmap(pixmap2)
        
        bladder_label_3T = QLabel(" If the bladder volume <250cc AND the ratio of the Bladder to the GTV Volume is <2.0")
        bladder_label_3P = QLabel()
        pixmap3 = QPixmap()
        pixmap3.load(self.notok,'.png')
        pixmap3 = pixmap3.scaledToWidth(50)
        bladder_label_3P.setPixmap(pixmap3)
        
        layout = self.BladderInfo.layout()
        button_box = self.BladderInfo.findChildren(QWidget, "qt_msgbox_buttonbox")[0]
        layout_index = layout.indexOf(button_box)
        print('LAYOUT OF BUTTON BOX:', layout_index)
        layout.addWidget(bladder_label_1T,0,1)
        layout.addWidget(bladder_label_1P,1,1)
        layout.addWidget(bladder_label_2T,2,1)
        layout.addWidget(bladder_label_2P,3,1)
        layout.addWidget(bladder_label_3T,4,1)
        layout.addWidget(bladder_label_3P,5,1)
        layout.addWidget(button_box, 6,1)
                
        self.BladderInfo.show()
        self.BladderInfo.raise_()
        QApplication.setActiveWindow(self.BladderInfo)
        
        
"""THIS IS THE FIDUCIAL INTEGRITY GUI"""

class FiducialTestGUI(QWidget,CKsimulation):
    """A GUI to determine fiducial implant quality."""
    
    def __init__(self, *args):   
        super().__init__()
        print('initializing fiducial GUI')
        self.ok    = "\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD\CKBladderandFiducialChecks\check3.png"
        self.notok = "\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD\CKBladderandFiducialChecks\checkNG.png"
        self.warn  = "\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD\CKBladderandFiducialChecks\exclimation.png"
        
        self.play = "\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD\CKBladderandFiducialChecks-V2\play2.jpg"
        self.info = "\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD\CKBladderandFiducialChecks-V2\info.png"
        
        self.pause_msg = """Please place fiducial markers by going into Structure Definition->POI's 
                            Select the Fiducial (i.e. Fid1)
                            Right Click on fiducial name in the list
                            Move POI to slice intersection
                            Finetune using the Move POI tool
                            Finally, click the Play button on the bottom left of the RayStation scripting window"""
        
        self.message_tx=''
    
        self.setWindowTitle('CK Fiducial Integrity Check')
        self.layout = QGridLayout()
    
        self.button_bar = QToolBar()
        
        self.playButton = QPushButton("")
        self.playButton.setDisabled(True)
        self.icon = QIcon(self.play)
        self.playButton.setIcon(self.icon)
        self.button_bar.addWidget(self.playButton)
        self.playButton.clicked.connect(self.find_and_place)
        
        self.infoButton = QPushButton("")
        self.icon2 = QIcon(self.info)
        self.infoButton.setIcon(self.icon2)
        self.button_bar.addWidget(self.infoButton)
        self.infoButton.clicked.connect(self.helpMe)
        
        self.label1  = QLabel("Select a Target Structure Containing the Fiducials")
        self.Targets  = QComboBox(objectName='Targets')
        self.Targets.textActivated.connect(self.select_Target)
        
        for i,j in enumerate(self.contour_list):
            self.Targets.insertItem(i,self.contour_list[i])
        
        self.dropDownGroupBox = QGroupBox('')
        self.dropDownLayout = QVBoxLayout()
        self.dropDownLayout.addWidget(self.label1)
        self.dropDownLayout.addWidget(self.Targets)
        self.dropDownGroupBox.setLayout(self.dropDownLayout)
        
        self.fiddata   = QTableWidget(objectName='Fiducial Data')
        self.fidspace  = QTableWidget(objectName='Fiducial Spacing')
        self.fidangles = QTableWidget(objectName='Minimum Angle Test') 

        self.fiddata.setFrameStyle(QFrame.StyledPanel   | QFrame.Sunken)
        self.fidspace.setFrameStyle(QFrame.StyledPanel  | QFrame.Sunken)
        self.fidangles.setFrameStyle(QFrame.StyledPanel | QFrame.Sunken)

        self.fiddata.setColumnCount(4)
        self.fidspace.setColumnCount(3)
        self.fidangles.setColumnCount(3)
        
        self.fiddata.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.fidspace.setColumnWidth(2, 10)
        self.fidspace.horizontalHeader().setSectionResizeMode(0,QHeaderView.Stretch)
        self.fidspace.horizontalHeader().setSectionResizeMode(1,QHeaderView.Stretch)

        self.fidangles.setColumnWidth(2, 10)
        self.fidangles.horizontalHeader().setSectionResizeMode(0,QHeaderView.Stretch)
        self.fidangles.horizontalHeader().setSectionResizeMode(1,QHeaderView.Stretch)
        
        self.fiddata.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.fiddata.setHorizontalHeaderLabels(['Name', 'X (cm)', 'Y (cm)', 'Z (cm)'])
        
        self.fidspace.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.fidspace.setHorizontalHeaderLabels(['Fiducial Combination', 'Spacing (cm)', ''])
        
        self.fidangles.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.fidangles.setHorizontalHeaderLabels(['Angle btwn. segments', 'Angle (degrees)', ''])
        
        self.layout.addWidget(self.button_bar, 0,0) 
        self.layout.addWidget(self.dropDownGroupBox, 0,1)
        self.layout.addWidget(self.fiddata   , 3,0,1,2)
        self.layout.addWidget(self.fidspace  , 4,0,1,2)
        self.layout.addWidget(self.fidangles , 7,0,1,2)

        self.setLayout(self.layout)

    def select_Target(self,*args):
        """
        Select a target contour.
           
        This should be the a target contour containing the fiducial markers.
        """
        self.selected_Target = self.Targets.currentText()
        print('Target is:',self.selected_Target)
        self.playButton.setDisabled(False)
                   
    def find_and_place(self, *args):
        """Locate high-Z markers in a volume and contour them."""  
        """Then insert 4 template fiducials in a line"""
        print('PLAY BUTTON WAS CLICKED IN FIND AND PLACE METHOD')
        self.createFiducialROI()
        self.findFiducials()
        self.insertFiducialMarkers()
        self.deleteFiducialROI()
        self.lower()

        await_user_input(message=self.pause_msg)
        
        self.evaluate_fiducials()
        QApplication.setActiveWindow(self)
        
    def evaluate_fiducials(self, *args):
        """Test the fiducial placement."""
        self.init_current_CT()
        print("FROM evaluate_fiducials():The exam is:", self.exam_name)
        
        self.getFiducialCoordinates()
        self.calculateFiducialSpacings()
        self.calculateFiducialAngles()
        self.minAngleTest()
        
        setFiducialInformation(self)
        setFiducialSpacingInfo(self)
        setFiducialAngleInfo(self)        

    def helpMe(self, *args):
        """More information about the app."""
        self.FiducialInfo = QMessageBox()
        self.FiducialInfo.setIcon(QMessageBox.Information)
        self.FiducialInfo.setWindowTitle("Fiducial Check Information")
        msg=""" 
                The Fiducial Integrity Checker will calculate all the possible triangles that can be constructed with N fiducials
                
                The requirement is that there exists at least one triangle whose angles are all greater than 15 degrees
                
                If such a triangle is found, the fiducials will pass the so-called minimum angle test, otherwise they will fail and require remediation or expanded margins.
                
                This app will list all the constiuent angles of the a N possible triangles and their values in degrees
                
                This will also check the relative spacing bewtween the fiducials. If this value is <2.0cm, they will be flagged. 
                
                
               """
        self.FiducialInfo.setText(msg)
        self.FiducialInfo.show()
        self.FiducialInfo.raise_()
        QApplication.setActiveWindow(self.FiducialInfo)
        
def setFiducialInformation(self,*args):
    """Display fiducial names and coordinates."""
    self.num_fiducials = self.count_fiducials()
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

