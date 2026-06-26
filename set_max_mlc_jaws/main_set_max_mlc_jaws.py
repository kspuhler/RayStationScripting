""" 
set_max_mlc_jaws\main_set_max_mlc_jaws.py

The GUI allows the user to change a beam to a maximum MLC and Jaw size as determined by
another beam's MLC and Jaw settings.  The tool is helpful for reducing the size of beams,
when their optimized MLC and Jaws are larger than a givn limit often established by an 
initial physician's field shape.  Ex: Breast Tangents

Created on 11/10/2025

@author: clanco01
"""
from __future__ import annotations

# === DEBUG SETTINGS ===
_DEBUG_THIS_MODULE = False
_ALERT_PHYSICIST_ON_ALL_USES = False

# === Raystation import ===
try:
    from connect import set_progress, await_user_input, get_current
except Exception:
    pass

# === WORKING DIRECTORY ===
import sys
sys.path.append(r"\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
sys.path.append(r"F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")

# === Main library imports ===
from PyQt5.QtWidgets import QGroupBox
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QCheckBox, QHBoxLayout#, QVBoxLayout
from PyQt5.QtWidgets import QGridLayout, QWidget, QPushButton
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
import tkinter as tk
from tkinter import messagebox
import time

# === Local imports ===
from RSutil.LogUtil.rs_logging import LOGGERS, set_logger_mode
from RSutil.ErrorsUtil.error_dispatcher import DispatcherConfig
from RSutil.ErrorsUtil.rs_errors import report_error
from RSutil.ErrorsUtil.error_codes import PROMPT_USER, ALERT_PHYSICIST, ABORT_SCRIPT
from RSutil.patient_data_util import PatientDataUtil
from breast_sib.SetMaxMLCAndJawPositions import SetMaxMLCAndJawPositions
from set_max_mlc_jaws.copy_beam_set import CopyBeamSet
from set_max_mlc_jaws.delete_closed_segment import DeleteClosedSegment

# === Setup Logger ===
_logger = LOGGERS["set_max_mlc_jaws"]
if _DEBUG_THIS_MODULE:
    set_logger_mode(_logger, "debug")

def _alert_physicist_error(
        exc: Exception, 
        metadata: dict | None = None, 
        message: str | None = None
):                                              
    if not _DEBUG_THIS_MODULE:
        cfg = DispatcherConfig()
        cfg.alert_recipients = ["owen.clancey@nyulangone.org"]
        report_error(
                error_def=ALERT_PHYSICIST.SYSF_UNHANDLED_EXCEPTION, 
                original_exception=exc, 
                context={"module": "main_set_max_mlc_jaws.py"},
                metadata=metadata,
                message=message,
                dispatcher_config=cfg,
            )

if _ALERT_PHYSICIST_ON_ALL_USES:
    e = RuntimeError("INFO ONLY - Set Max MLC and Jaws script initialized.  Review patient data in logs.")
    _alert_physicist_error(e, message=__name__)



class SetMaxBeamShape(QWidget):
    """A GUI front-end for setting the MLC and Jaws of a beam to no larger than another beam."""

    def __init__(self, *args):
        _logger.info("Initializating SetMaxBeamShape...")
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        self._app = app
        
        super().__init__()
        
        self.path_ss = "\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD\SantoroSleekStylesheet.css"
        
        # Set current progress bar
        set_progress('Copying beam set...', percentage = -1)
        CopyBeamSet(get_current("BeamSet"), get_current("Plan"), get_current("Examination").Name)

        self.beams = get_current("BeamSet").Beams
        self.button_array =[]
        self.cpComboArray = []
        self.selected_beam_index = 0
        
        self.setWindowTitle("Set Max Beam MLC and Jaws")
        self.resize(400, 200)
        self.setToolTip(self.__doc__)

        self.layout = QGridLayout()

        self.doIt = QPushButton('Go')
        self.dontdoIt = QPushButton('Cancel')

        self.doIt.setMinimumWidth(100)
        self.dontdoIt.setMinimumWidth(100)
        self.label = QLabel("  Beam to Change             Beam Defining Max MLC and Jaws")

        self.num_of_beams = len(self.beams)

        #Connect widgets to actions
        self.doIt.clicked.connect(self.isChecked)
        self.dontdoIt.clicked.connect(self.exit_script)

        self.buttonGroupBox = QGroupBox('')
        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.addWidget(self.doIt), self.buttonLayout.addWidget(self.dontdoIt)
        self.buttonGroupBox.setLayout(self.buttonLayout)
        self.buttonLayout.setAlignment(Qt.AlignLeft)
        self.hightlightButtons()
        self.doIt.setToolTip('Set Max Beam MLC and Jaws')

        self.makeRadioButtonGroup()
        
        self.layout.addWidget(self.label, 0, 0)
        self.layout.addWidget(self.beamGroupBox, 1,0)
        self.layout.addWidget(self.buttonGroupBox, 2, 0)
       
        self.setLayout(self.layout)
        
        # Set current progress bar
        set_progress('User setting parameters...', percentage = -1)
        _logger.info("User setting parameters...")

    # === Error handling ===
    def _prompt_user_acknowledge(
            self, 
            exc: Exception, 
            metadata: dict | None = None, 
            message: str | None = None
    ):                                                  
        report_error(
                error_def=PROMPT_USER.UIUX_USER_ACKNOWLEDGE, 
                original_exception=exc, 
                context={"module": "main_set_max_mlc_jaws.py"},
                metadata={},
                message=message,
            )
    
    def _abort_script_error(
            self, 
            exc: Exception, 
            metadata: dict | None = None, 
            message: str | None = None
    ):
        report_error(
                error_def=ABORT_SCRIPT.DATA_REQUIRED_MISSING, 
                original_exception=exc, 
                context={"module": "main_set_max_mlc_jaws.py"},
                metadata={},
                message=message,
            )
        raise RuntimeError(str(exc))

    def update_beam_mlc_jaws(self, max_beam_name):
        
        print(f"Beam to change:  {self.beams[self.selected_beam_index].Name}    Max Beam: {self.beams[max_beam_name].Name}")
        
        # Update beam to change based upon max beam
        SetMaxMLCAndJawPositions(self.beams[self.selected_beam_index], self.beams[max_beam_name])
        
        # Delete any close MLC segments
        DeleteClosedSegment(self.beams[self.selected_beam_index])
        
    def makeRadioButtonGroup(self, *args, **kwargs):
        """Make a group box of checkboxes to select beams."""
        self.beamGroupBox = QGroupBox('')
        self.beam_layout = QGridLayout()
        
        #fill the radio button box with beam names
        for i in range(self.num_of_beams):
            name = self.beams[i].Name
            self.radioBeams = QCheckBox(name)
            self.cpComboBox = QComboBox()
            self.button_array.append(self.radioBeams)
            self.cpComboArray.append(self.cpComboBox)
            
            self.beam_layout.addWidget(self.radioBeams,i,0)
            self.beam_layout.addWidget(self.cpComboBox,i,1)
            
            for beam in self.beams:
                if beam.Name != name:
                    self.cpComboBox.addItem(beam.Name)
                 
            
        print('There are ',len(self.button_array), 'beams')
        self.beamGroupBox.setLayout(self.beam_layout)
    
    def isChecked(self, *args, **kwargs):
        """Check which beams are to be reshaped and then reshape them.""" 
        # Set current progress bar
        set_progress('Updating selected beams...', percentage = -1)
        
        errors = []
        for i in range(self.num_of_beams):
            if self.button_array[i].isChecked() == True:
                self.selected_beam_index = i
                max_beam_name = str(self.cpComboArray[self.selected_beam_index].currentText())
                if len(self.beams[max_beam_name].Segments) != 1:
                    errors.append(max_beam_name)
        
        if errors: 
            unique_errors = list(set(errors))
            root = tk.Tk()
            root.withdraw()  # Hide the root window
            root.attributes('-topmost', True)
            messagebox.showerror("Error", f"The following beams have multiple segments and can not be used to define the maximum MLC and Jaw positions:\n\n {unique_errors}")
            root.destroy()  # Cleanly destroy the root window
            
            # Set current progress bar
            set_progress('User setting parameters...', percentage = -1)
            
        else:
            updated_beams = []
            for i in range(self.num_of_beams):
                if self.button_array[i].isChecked() == True:
                    self.selected_beam_index = i
                    max_beam_name = str(self.cpComboArray[self.selected_beam_index].currentText())
                    self.update_beam_mlc_jaws(max_beam_name)
                    updated_beams.append(self.beams[self.selected_beam_index].Name)
            
            # Print a message box to the user for which beams were updated
            root = tk.Tk()
            root.withdraw()  # Hide the root window
            root.attributes('-topmost', True)
            
            # Set current progress bar
            set_progress('Finished!!', percentage = -1)
            
            # Set message box
            messagebox.showinfo("Updated Beams", f"The beam set was copied with the following beams updated:\n\n {updated_beams}")
            root.destroy()  # Cleanly destroy the root window
            
            # Exit application
            QApplication.quit()
        
    def exit_script(self):
        QApplication.quit()  # Ends the Qt loop
        
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

    def main(self, stylesheet_path: str | None = None) -> None:
        """
        Launch the SetMaxBeamShape GUI.

        Called from run_set_max_mlc_jaws.main().
        Ensures there is a QApplication, applies the stylesheet,
        shows the window, and starts the Qt event loop so the
        window stays open until the user is done.
        """
        # Make sure we have a QApplication
        app = getattr(self, "_app", None)
        if app is None:
            app = QApplication.instance()
            if app is None:
                app = QApplication(sys.argv)
            self._app = app

        # Try to load the stylesheet and set style
        try:
            if stylesheet_path is None:
                stylesheet_path = self.path_ss
            with open(stylesheet_path, "r", encoding="utf-8") as f:
                app.setStyleSheet(f.read())
            app.setStyle("Fusion")
        except Exception as e:
            _logger.warning(
                "Warning: could not load stylesheet %s: %s",
                stylesheet_path,
                e,
            )

        # Show the window (again, in case) and start the event loop
        self.show()
        try:
            app.exec_()  # <- keeps the window open until closed
        except Exception as e:
            _alert_physicist_error(e, message=__name__)
            _logger.error("[FAILED] in %s.  Email notification sent.  Exception: %s", __name__, str(e))
            set_progress("Waiting for user to hit play button...", percentage = -1)
            await_user_input(message="[FAILED] script.  Physicist alerted to address the issue.")
            set_progress("Sending physicist notification...", percentage = -1)
            time.sleep(3)
            self._abort_script_error(exc=e, message=str(e))
