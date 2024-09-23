"""
Created on Wed Aug 14 11:16:59 2024.

@author: santoj14

Field-in-Field user interface.

This application emulates the Auto Field-in-Field button in Raystation but adds 
some functionality specific to breast FinF planning.
"""

from PyQt5.QtWidgets import QGroupBox, QLineEdit
from PyQt5.QtWidgets import QComboBox,QTableWidget,QTableWidgetItem
from PyQt5.QtWidgets import QGridLayout, QWidget, QPushButton, QHBoxLayout
from PyQt5.QtWidgets import QFrame, QLabel, QStyledItemDelegate,QMessageBox

from PyQt5.QtCore import Qt

import sys
from FieldinFieldClass import FieldinField

sys.path.append("F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD\BreastFiF")
sys.path.append("\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD\BreastFif")


class ROdelegate(QStyledItemDelegate):
    """Trick a QT Table Widget object to be read-only using the setItemDelegateForColumn method.""" 
    
    def createEditor(*args, **kwargs):
        """Return a message that this is read-only."""
        print("This is read-only")


class FieldinFieldGUI(QWidget, FieldinField):
    """A GUI front-end for breast-specific planning using the RS Auto field-in-field."""
    
    def __init__(self, *args):
        
        super().__init__()
        
        self.num_of_beams  = self.beam_set.Beams
        
        self.Target_contours=[]
        self.selected_name=[]
        
        self.setWindowTitle('Sort-of-EZ-Fluence')
        self.resize(500, 550)  
        self.setToolTip(self.__doc__)

        self.layout = QGridLayout()

        self.contours    = QComboBox(objectName='Targets')
        self.beams       = QTableWidget(objectName='Beams')
        self.doIt        = QPushButton('Start')
        self.dontdoIt    = QPushButton('Cancel')
        
        self.doIt.setMinimumWidth(100)
        self.dontdoIt.setMinimumWidth(100)
        self.contours.setToolTip('Select the FiF target. This must be the same target contour specified in the Rx')
        self.label = QLabel("Select a Target")

        self.beams.setFrameStyle(QFrame.StyledPanel   | QFrame.Sunken)
        self.beams.setColumnCount(2)

        self.beams.setHorizontalHeaderLabels(['Beams               ', 'No. of Segments'])

        #MAKE FIRST COLUMN READ ONLY
        delegate = ROdelegate()
        self.beams.setItemDelegateForColumn(0,delegate)

        self.beams.resizeColumnToContents(0)
        self.beams.horizontalHeader().setStretchLastSection(True)
        self.beams.setVerticalHeaderLabels([''])

        self.num_of_contours = len(self.Contours)
        self.num_of_beams    = len(self.beam_set.Beams)
        self.beams.setRowCount(self.num_of_beams)

        for i in range(self.num_of_contours):
            name = self.Contours[i].OfRoi.Name
            Type = self.Contours[i].OfRoi.Type
            if (self.Contours[i].HasContours()==True) and (Type=='Ptv' or Type=='Ctv' or Type=='Gtv'):
             self.contours.insertItem(i,name)
             self.Target_contours.append(self.Contours[i])
        
        #initialize the target contour to the first target in the list
        self.selected_name = self.Target_contours[0].OfRoi.Name
        
        #initialize the number of subfields per beam to default
        for i in range(self.num_of_beams):
            name = self.beam_set.Beams[i].Name
            print(name)
            self.beams.setItem(i,0,QTableWidgetItem(name))
            self.num_segments.append(3)
            self.beams.setItem(i,1,QTableWidgetItem(str(self.num_segments[i])))
        self.beams.setToolTip('Enter the number of desired subfields per beam (0-10). Enter 0 for an unmodulated (open) field')

        self.segGroupBox = QGroupBox('Segmentation Settings')
        
        self.min_seg_mu = QLabel('Min. segment MU per fraction')
        self.min_seg_ar = QLabel('Min. segment Area [cm\u00b2]')
        self.min_num_pr = QLabel('Min. number of open leaf pairs')
        self.min_leafen = QLabel('Min. leaf end separation [cm]')
        
        #Get default values and populate the GUI
        seg_settings=self.get_segmentation_settings()
        
        self.min_seg_muVAL = QLineEdit(str(seg_settings[0])) 
        self.min_seg_muVAL.setMaximumWidth(50)
        self.min_seg_arVAL = QLineEdit(str(seg_settings[1]))
        self.min_seg_arVAL.setMaximumWidth(50)
        self.min_num_prVAL = QLineEdit(str(seg_settings[2]))
        self.min_num_prVAL.setMaximumWidth(50)
        self.min_leafenVAL = QLineEdit(str(seg_settings[3]))
        self.min_leafenVAL.setMaximumWidth(50)
        
        self.min_seg_muVAL.setToolTip('Minimum number of segment MUs per fraction. A minimum of 5 is suggested')
        self.min_seg_arVAL.setToolTip('Minimum area of individual segments in cm\u00b2. 4cm\u00b2 is suggested as a starting point')
        self.min_num_prVAL.setToolTip('Minimum number of open (opposing) leaf pairs (1-10). 1 is suggested as a starting point')
        self.min_leafenVAL.setToolTip('Minimum opposing leaf end separation in cm (0-10cm). 0 is a suggested starting point')
        
        self.gr_layout = QGridLayout()
        self.gr_layout.addWidget(self.min_seg_mu,0,0), self.gr_layout.addWidget(self.min_seg_muVAL,0,1)
        self.gr_layout.addWidget(self.min_seg_ar,1,0), self.gr_layout.addWidget(self.min_seg_arVAL,1,1)
        self.gr_layout.addWidget(self.min_num_pr,2,0), self.gr_layout.addWidget(self.min_num_prVAL,2,1)
        self.gr_layout.addWidget(self.min_leafen,3,0), self.gr_layout.addWidget(self.min_leafenVAL,3,1)
        
        self.segGroupBox.setLayout(self.gr_layout)

        self.contours.activated.connect(self.selectContour)
        self.doIt.clicked.connect(lambda: self.run_fif(self.selected_name))
        self.dontdoIt.clicked.connect(sys.exit)
        
        self.min_seg_muVAL.editingFinished.connect(self.changeSegParameter1ViaGui)
        self.min_seg_arVAL.editingFinished.connect(self.changeSegParameter2ViaGui)
        self.min_num_prVAL.editingFinished.connect(self.changeSegParameter3ViaGui)
        self.min_leafenVAL.editingFinished.connect(self.changeSegParameter4ViaGui)
        
        self.beams.cellChanged.connect(self.getSegsPerBeam)
        
        self.buttonGroupBox = QGroupBox('')
        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.addWidget(self.doIt), self.buttonLayout.addWidget(self.dontdoIt)
        self.buttonGroupBox.setLayout(self.buttonLayout)
        self.buttonLayout.setAlignment(Qt.AlignLeft)
        self.hightlightButtons()
        self.doIt.setToolTip('Start the Field-in-Field calculator')
        
        self.layout.addWidget(self.label,  0,0)
        self.layout.addWidget(self.contours,1,0)

        self.layout.addWidget(self.beams,2,0)
        self.layout.addWidget(self.buttonGroupBox ,4,0)
        self.layout.addWidget(self.segGroupBox,3,0)

        self.setLayout(self.layout)
        self.show()
        
    def selectContour(self,*args, **kwargs):
        """Select a target contour for the FiF calculator to target. Must be the same as what the Rx is targetting."""
        self.selected_contour = self.contours.currentIndex()
        self.selected_name    = self.Target_contours[self.selected_contour].OfRoi.Name
        
        print(self.selected_name)

    def getSegsPerBeam(self,*args, **kwargs):
        """Get and set the user-specified number of per beam subfields. Set to 0 for an open field."""
        beam_index = self.beams.currentRow()
        a = float(self.beams.item(beam_index,1).text())
        if a>=0 and a<=10:
         self.num_segments[beam_index]=a
         print('Beam number:',beam_index,' set to ',self.num_segments[beam_index],' subfields')
        else:
            self.beams.setItem(beam_index,1,QTableWidgetItem(str(3)))
            print('Value must be between 0 and 10')
            msg = 'Value must be between 0 and 10'
            err = QMessageBox()
            err.setIcon(QMessageBox.Critical)
            err.setWindowTitle("Value out of range")
            err.setText(msg)
            err.exec_()
            
    def changeSegParameter1ViaGui(self, *args, **kwargs):
        """Set Parameter 1, minimum segment MU value from the GUI."""
        [a,b,c,d]=self.get_segmentation_settings()
        a=float(self.min_seg_muVAL.text())
        self.set_segmentation_settings(a,b,c,d)
        print('Min. segment MU per fraction changed to:',self.min_seg_muVAL.text())
        
    def changeSegParameter2ViaGui(self, *args, **kwargs):
        """Set Parameter 2, minimum segment area from the GUI."""
        [a,b,c,d]=self.get_segmentation_settings()
        b=float(self.min_seg_arVAL.text())
        self.set_segmentation_settings(a,b,c,d)
        print('Min. segment Area changed to:',self.min_seg_arVAL.text())
        
    def changeSegParameter3ViaGui(self, *args, **kwargs):
        """Set Parameter 1, minimum number of open leaf pairs from the GUI."""
        [a,b,c,d]=self.get_segmentation_settings()
        c=float(self.min_num_prVAL.text())
        print(c)
        if c>=1.0 and c<=10.0:
         self.set_segmentation_settings(a,b,c,d)
         print('Min. number of open leaf pairs changed to:',self.min_num_prVAL.text())
        else:
            print('Value must be between 1 and 10')
            msg = 'Value must be between 1 and 10'
            err = QMessageBox()
            err.setIcon(QMessageBox.Critical)
            err.setWindowTitle("Value out of range")
            err.setText(msg)
            err.exec_()
    
    def changeSegParameter4ViaGui(self, *args, **kwargs):
        """Set Parameter 1, minimum leaf spacing from the GUI."""
        [a,b,c,d]=self.get_segmentation_settings()
        d=float(self.min_leafenVAL.text())
        if d>=0.0 and d<=10.0:
         self.set_segmentation_settings(a,b,c,d)
         print('Min. leaf end separation changed to:',self.min_leafenVAL.text())
        else:
            self.min_leafenVAL.undo()
            
            print('Value must be between 0 and 10')
            msg = 'Value must be between 0 and 10'
            err = QMessageBox()
            err.setIcon(QMessageBox.Critical)
            err.setWindowTitle("Value out of range")
            err.setText(msg)
            err.exec_()
            
    def hightlightButtons(self,*args,**kwargs):
        """Highlight the buttons when you mouse over them."""
        self.doIt.setStyleSheet("QPushButton::hover"
                             "{"
                             "background-color : grey;"
                             "}") 
        self.dontdoIt.setStyleSheet("QPushButton::hover"
                             "{"
                             "background-color : grey;"
                             "}") 
        
        
        
        
        
        