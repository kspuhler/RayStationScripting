"""
Set the MLC aperture of a control point in the selected beam to the open jaw size of the beam

@author: santoj14.
"""
from PyQt5.QtWidgets import QGroupBox
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QCheckBox, QHBoxLayout, QVBoxLayout
from PyQt5.QtWidgets import QGridLayout, QWidget, QPushButton
from PyQt5.QtWidgets import QLabel

from PyQt5.QtCore import Qt

import sys
try:
    from connect import *
except:
    pass

sys.path.append("F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD\MLC2JAW")
sys.path.append("\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD\MLC2JAW")

class setMLC2JAWGUI(QWidget):
    """A GUI front-end for setting an MLC aperture to jaw settings for the 1st segment in an MLC beam."""

    def __init__(self, *args):

        super().__init__()

        self.examination = get_current("Examination")
        self.case = get_current("Case")
        self.beam_set = get_current("BeamSet")
        self.treatment_plan = get_current("Plan")
        self.Plans = self.case.TreatmentPlans
        self.beam = self.beam_set.Beams

        self.num_segments = []
        self.selected_beam = []
        self.button_array =[]
        self.num_CP_inBeam = []
        self.cpComboArray = []
        self.selected_beam_index = 0
        
        self.setWindowTitle('Set MLC to Jaws')
        self.resize(400, 200)
        self.setToolTip(self.__doc__)

        self.layout = QGridLayout()

        self.doIt = QPushButton('Go')
        self.dontdoIt = QPushButton('Cancel')

        self.doIt.setMinimumWidth(100)
        self.dontdoIt.setMinimumWidth(100)
        self.label = QLabel("      Beam                       Segment Number")

        self.num_of_beams = len(self.beam_set.Beams)

        #Connect widgets to actions
        self.doIt.clicked.connect(self.isChecked)
        self.dontdoIt.clicked.connect(sys.exit)

        self.buttonGroupBox = QGroupBox('')
        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.addWidget(self.doIt), self.buttonLayout.addWidget(self.dontdoIt)
        self.buttonGroupBox.setLayout(self.buttonLayout)
        self.buttonLayout.setAlignment(Qt.AlignLeft)
        self.hightlightButtons()
        self.doIt.setToolTip('Change the MLC to the Jaw Size')

        self.makeRadioButtonGroup()
        
        self.layout.addWidget(self.label, 0, 0)
        self.layout.addWidget(self.beamGroupBox, 1,0)
        self.layout.addWidget(self.buttonGroupBox, 2, 0)
       
        self.setLayout(self.layout)
        self.show()

    def move_MLC2JAW(self, *args, **kwargs):
        """Set the MLC aperture to the open jaw position for the selected beam."""
        print('-------MOVING MLCs---------')
        
        segment = self.cpComboArray[self.selected_beam_index].currentText()
        seg = int(segment)-1
        print("CHANGING SEGMENT:",seg)
        
        x1_positions = self.beam[self.selected_beam_index].Segments[0].LeafPositions[0]  #left
        x2_positions = self.beam[self.selected_beam_index].Segments[0].LeafPositions[1]  #Right
        open_jaws = self.beam[self.selected_beam_index].InitialJawPositions

        self.num_CP_inBeam = len(self.beam[self.selected_beam_index].Segments)
        print('NUMBER OF CONTROL POINTS IN THIS BEAM IS:', self.num_CP_inBeam)
        print('JAW SETTINGS [X1,X2,Y1,Y2]:', open_jaws)
        print('MLC POSITIONS BEFORE\n')
        print('X1 MLC POSITIONS\n', x1_positions, '\n')
        print('X2 MLC POSITIONS\n', x2_positions, '\n')

        for i in range(len(x1_positions)):
            if x1_positions[i] != x2_positions[i]:#SKIP CLOSED LEAF PAIRS
                x1_positions[i] = open_jaws[0]
                x2_positions[i] = open_jaws[1]

        print('MLC POSITIONS AFTER\n')
        print('X1 MLC POSITIONS\n', x1_positions, '\n')
        print('X2 MLC POSITIONS\n', x2_positions)

        leaf_positions = ([x1_positions, x2_positions])
        self.beam[self.selected_beam_index].Segments[seg].LeafPositions = leaf_positions

    def makeRadioButtonGroup(self, *args, **kwargs):
        """Make a group box of checkboxes to select beams."""
        self.beamGroupBox = QGroupBox('')
        self.beamAndCPLayout = QGridLayout()
        
        #fill the radio button box with beam names
        for i in range(self.num_of_beams):
            name = self.beam[i].Name
            self.radioBeams = QCheckBox(name)
            self.cpComboBox = QComboBox()
            self.button_array.append(self.radioBeams)
            self.cpComboArray.append(self.cpComboBox)
            
            self.beamAndCPLayout.addWidget(self.radioBeams,i,0)
            self.beamAndCPLayout.addWidget(self.cpComboBox,i,1)
            
            for j in range(len(self.beam[i].Segments)):
                self.cpComboBox.addItem(str(j+1))
                 
            
        print('There are ',len(self.button_array), 'beams')
        self.beamGroupBox.setLayout(self.beamAndCPLayout)
        #self.beamAndCPLayout.setAlignment(Qt.AlignRight)
    
    def isChecked(self, *args, **kwargs):
        """Check which beams are to be reshaped and then reshape them.""" 
        for i in range(self.num_of_beams):
            
            if self.button_array[i].isChecked() == True:
             self.selected_beam_index = i
             self.move_MLC2JAW()
        print('\n')
            
        
    def hightlightButtons(self, *args, **kwargs):
        """Highlight the buttons when you mouse over them."""
        self.doIt.setStyleSheet("QPushButton::hover"
                                "{"
                                "background-color : grey;"
                                "}")
        self.dontdoIt.setStyleSheet("QPushButton::hover"
                                    "{"
                                    "background-color : grey;"
                                    "}")
