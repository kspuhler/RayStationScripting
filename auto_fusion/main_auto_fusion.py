""" 
The user selects the fixed (refernce) and moving (target) images for fusion.  
More than one moving image can be selected.
The user selected target structure can be another structure with contours or a
DLS-created  structure.  The fusion is centered around the target structure
using a fusion box focus region and rigid body registration.
Either a frame of reference or image registration fusion can be performed.
CT and MRIs are the only image types allowed.

version 3.0

Created on 10/01/2025

@author: clanco01
"""

from __future__ import annotations

# === DEBUG SETTINGS ===
_DEBUG_THIS_MODULE = False
_ALERT_PHYSICIST_ON_ALL_USES = False

# === Raystation import ===
try:
    from connect import get_current, set_progress, await_user_input
except Exception:
    pass

# === WORKING DIRECTORY ===
import sys
sys.path.append(r"\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
sys.path.append(r"F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")


# === Main library imports ===
import math
import copy
import sys
import clr
clr.AddReference('System.Windows.Forms')
from System.Windows.Forms import SendKeys
import time
import tkinter as tk
from tkinter import messagebox
from typing import Optional

# === Local imports ===
from RSutil.LogUtil.rs_logging import LOGGERS, set_logger_mode
from auto_fusion.ui_auto_fusion import AutoFusionSelectionWindow
from auto_fusion.constants_auto_fusion import dls_model_for, SKIP_POPUP_ROI_NAMES, ALIGNMENT_ROTATIONS
from RSutil.ErrorsUtil.error_dispatcher import DispatcherConfig
from RSutil.ErrorsUtil.rs_errors import report_error
from RSutil.ErrorsUtil.error_codes import PROMPT_USER, ALERT_PHYSICIST, ABORT_SCRIPT
from RSutil.patient_data_util import PatientDataUtil

# === Setup Logger ===
_logger = LOGGERS["auto_fusion"]
if _DEBUG_THIS_MODULE:
    set_logger_mode(_logger, "debug")

def _alert_physicist_error(
        exc: Exception, 
        metadata: Optional[dict] = None, 
        message: Optional[str] = None
):  
    if not _DEBUG_THIS_MODULE:                                            
        cfg = DispatcherConfig()
        cfg.alert_recipients = ["owen.clancey@nyulangone.org"]
        report_error(
                error_def=ALERT_PHYSICIST.SYSF_UNHANDLED_EXCEPTION, 
                original_exception=exc, 
                context={"module": "main_auto_fusion.py"},
                metadata=metadata,
                message=message,
                dispatcher_config=cfg,
            )

if _ALERT_PHYSICIST_ON_ALL_USES:
    e = RuntimeError("INFO ONLY - AutoFusion script initialized.  Review patient data in logs.")
    _alert_physicist_error(e, message=__name__)


class AutoFusion:
    def __init__(self):
        
        # Initalize PatientDataUtil
        try:
            self.pdu = PatientDataUtil()
            self.case = self.pdu.get_current_case()
            self.roi_names = self.pdu.get_roi_names()
            self.patient_model  = self.pdu.get_current_patient_model()
        except Exception as e:
            _logger.error("PatientDataUtil() failed in AutoFusion initialization: %s", e)
            self._abort_script_error(exc=e, message=str(e))
        
        # Initialize all attributes
        self.box_size = {}
        self.fixed_exam = None
        self.fixed_name = None
        self.fusion_roi_name = None
        self.moving_exam = None
        self.moving_names = None
        self.registration_number = -1
        self.selected_values = {}
        self.target_center = {}
        self.target_roi_name = None
        self.skip_popup_roi_names = SKIP_POPUP_ROI_NAMES
        self.translation = {}
        self.run_dls_flag = True
        self.box_min_size = 10
        self.box_max_size = 30
        self.max_char_reg_name = 64
        self.registration_type = "Frame of Reference"
        
        # Logger
        _logger.info("AutoFusion initialized...")

    # === Error handling ===
    def _prompt_user_acknowledge(
            self, 
            exc: Exception, 
            metadata: Optional[dict] = None, 
            message: Optional[str] = None
    ):                                                  
        report_error(
                error_def=PROMPT_USER.UIUX_USER_ACKNOWLEDGE, 
                original_exception=exc, 
                context={"module": "main_auto_fusion.py"},
                metadata={},
                message=message,
            )
    
    def _abort_script_error(
            self, 
            exc: Exception, 
            metadata: Optional[dict] = None, 
            message: Optional[str] = None
    ):
        _logger.debug("Inside _abort_script_error()")                                            
        report_error(
                error_def=ABORT_SCRIPT.DATA_REQUIRED_MISSING, 
                original_exception=exc, 
                context={"module": "main_auto_fusion.py"},
                metadata={},
                message=message,
            )
        raise RuntimeError(str(exc))
    
    def get_registration_number_from_name(self, registration_name):
        
        # Find the registration number
        for i, registration in enumerate(self.case.RigidRegistrations):
            if registration.Name == registration_name:
                self.registration_number = i
                break  # Stop searching after the first match
                
        if self.registration_number == -1:
            _logger.error("Registration name not found")
            exit()
    
    def get_box_size(self):
        # Get the corners of the ROI bounding box and center of the ROI
        bounds = self.patient_model.StructureSets[self.fixed_name].RoiGeometries[self.target_roi_name].GetBoundingBox()
        center = self.patient_model.StructureSets[self.fixed_name].RoiGeometries[self.target_roi_name].GetCenterOfRoi()
        
        # Get the maximum distance between the center and bounding box
        max_distance = max(
            abs(center[axis] - bounds[i][axis])
            for axis in ['x', 'y', 'z']
            for i in (0, 1)
        )
        
        # Set box size
        edge_length = min(self.box_max_size, max(self.box_min_size, 2 * max_distance))
        self.box_size = {"x": edge_length, "y": edge_length, "z": edge_length}
    
    def create_unique_fusion_roi_name(self, base_name="FusionBox"):
        # Start with base name
        self.fusion_roi_name = base_name
        suffix = 1
    
        # Keep modifying the name until it's unique
        while self.fusion_roi_name in self.roi_names:
            self.fusion_roi_name = f"{base_name}_{suffix}"
            suffix += 1
    
    def create_unique_registration_name(self, initial_registration_name):
        existing_registration_names = [registration.Name for registration in self.case.RigidRegistrations]
        
        # Initialize name
        registration_name = initial_registration_name
        suffix = 1
    
        # Keep modifying the name until it's unique
        while registration_name in existing_registration_names:
            registration_name = f"{initial_registration_name}_{suffix}"
            suffix += 1
            
        return registration_name[:self.max_char_reg_name]
    
    def check_for_skipping_user_popup(self):
        # Find CT and MR Examinations
        ct_exams = self.pdu.get_ct_exams()
        mr_exams = self.pdu.get_mr_exams()
    
        if len(ct_exams) != 1 or len(mr_exams) != 1:
            return
    
        self.fixed_name = ct_exams[0].Name
        self.fixed_exam = ct_exams[0]
        self.moving_names = mr_exams[0].Name
        self.moving_exam = mr_exams[0]
    
        # Find the first target ROI that exists and has a PrimaryShape
        for name in self.skip_popup_roi_names:
            if name in self.roi_names:
                if self.pdu.has_contours_on_ct(name, self.fixed_name):
                    self.target_roi_name = name
                    _logger.info(f"Assigned target roi name to {name}")
                    return
    
    def create_external(self, exam, exam_name):
        # Create if no External exists in the ROI list of the Patient Model
        if not self.pdu.has_roi_external():
            # Set current progress bar
            set_progress('Creating External structure...', percentage = -1)
            _logger.info("Creating External ROI...")
            try:
                self.patient_model.CreateRoi(Name="External", Color="Green", Type="External", TissueName="", RbeCellTypeName=None, RoiMaterial=None)
            except Exception as e:
                _logger.error(f"Error: {e}")
        
        # Check if the exam has contours for external
        if not self.pdu.has_roi_external_contour_on_ct(exam_name):
            # Set current progress bar
            set_progress('Creating External contours...', percentage = -1)
            _logger.info("Creating External ROI contours...")
            self.patient_model.RegionsOfInterest["External"].CreateExternalGeometry(Examination=exam, ThresholdLevel=-250)
    
    def calculate_target_center(self):
        self.target_center = self.patient_model.StructureSets[self.fixed_name].RoiGeometries[self.target_roi_name].GetCenterOfRoi()
        _logger.info(f"Target center of ROI target {self.target_roi_name} is: {self.target_center}")
    
    def calculate_initial_translation(self):
        # Calculate series center coordinate
        fixed_bb = self.fixed_exam.Series[0].ImageStack.GetBoundingBox()
        moving_bb = self.moving_exam.Series[0].ImageStack.GetBoundingBox()
        _logger.info(f"Fixed Bounding Box: {fixed_bb}")
        _logger.info(f"Moving Bounding Box: {moving_bb}")
        
        fixed_center_coord = {
            "x": (fixed_bb[1]["x"] - fixed_bb[0]["x"])/2 + fixed_bb[0]["x"],
            "y": (fixed_bb[1]["y"] - fixed_bb[0]["y"])/2 + fixed_bb[0]["y"],
            "z": (fixed_bb[1]["z"] - fixed_bb[0]["z"])/2 + fixed_bb[0]["z"],
        }
        moving_center_coord = {
            "x": (moving_bb[1]["x"] - moving_bb[0]["x"])/2 + moving_bb[0]["x"],
            "y": (moving_bb[1]["y"] - moving_bb[0]["y"])/2 + moving_bb[0]["y"],
            "z": (moving_bb[1]["z"] - moving_bb[0]["z"])/2 + moving_bb[0]["z"],
        }
        
        # Calculate the translation vector to put the moving image center over the target center on the CT
        self.translation = {
            "x": self.target_center["x"] + fixed_center_coord["x"] - moving_center_coord["x"],
            "y": self.target_center["y"] + fixed_center_coord["y"]  - moving_center_coord["y"],
            "z": self.target_center["z"] + fixed_center_coord["z"]  - moving_center_coord["z"],
        }
        _logger.info(f"Moving image transation: {self.translation}")
        
    def fusion_popup(self):
    
        # Set current progress bar
        set_progress('User window open and user selecting inputs...', percentage = -1)
        
        # Use selection window to get selected values for fusion
        window = AutoFusionSelectionWindow()
        window.mainloop()
        
        # Assign output
        self.selected_values = window.get_values()
        self.fixed_name = self.selected_values["ReferenceImageName"]
        self.moving_names = self.selected_values["FusingImageName"]
        self.target_roi_name = self.selected_values["TargetName"]
        self.registration_type = self.selected_values["RegistrtaionType"]
        
        # Log selected values
        _logger.info(f"Fusion Popup Selected Values: {self.selected_values}")
    
    def get_exam(self, exam_name, image_type="fixed"):
        
        # Get exam
        exam = self.pdu.get_exam_with_exam_name(exam_name)
        
        # Check exam type and assign
        exam_type = exam.EquipmentInfo.Modality
        if exam_type not in ["CT", "MR"]:
            title = "Error"
            message = f"{exam.Name} series type is not a CT or MRI.  Not currently supported."
            self.user_message(title, message)
            exit()
            
        if image_type == "fixed":
            self.fixed_exam = exam
            self.fixed_exam.SetPrimary()
        else:
            self.moving_exam = exam
            self.moving_exam.SetSecondary()
    
    def create_fusion_box(self):
        
        _logger.info("Creating fusion box...")
        
        # Create the fusion box
        fusion_box = self.case.PatientModel.CreateRoi(Name=self.fusion_roi_name, Color="SaddleBrown", Type="Control", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)

        # Create the box with user input properties and centered at the target center
        fusion_box.CreateBoxGeometry(Size=self.box_size, Examination=self.fixed_exam, Center=self.target_center, Representation="TriangleMesh", VoxelSize=None)

    def set_window_level(self):
        ct_window_level = {"x": 100, "y": 750}
        mri_window_level = {"x": 500, "y": 1000}
        
        for exam in self.case.Examinations:
            if exam.EquipmentInfo.Modality == 'CT':
                exam.Series[0].LevelWindow = ct_window_level
            elif exam.EquipmentInfo.Modality == 'MR':
                exam.Series[0].LevelWindow = mri_window_level

    # def get_center_series_coord(self, series):
        
    #     # Get center x and y coordinates
    #     center = {}
    #     center["x"] = series.ImageStack.NrPixels.x/ 2 * series.ImageStack.PixelSize.x + series.ImageStack.Corner.x
    #     center["y"] = series.ImageStack.NrPixels.y/ 2 * series.ImageStack.PixelSize.y + series.ImageStack.Corner.y
        
    #     # Get center z coordinate
    #     center_slice = len(series.ImageStack.SlicePositions) / 2 - 0.5
    #     center_slice_floor = math.floor(center_slice)
    #     center_slice_ceil = math.ceil(center_slice)
    #     center_slice_position = (series.ImageStack.SlicePositions[center_slice_floor] + series.ImageStack.SlicePositions[center_slice_ceil]) / 2
    #     center["z"] = center_slice_position + series.ImageStack.Corner.z
        
    #     return center
        
    @staticmethod
    def set_fusion_display_mode():
        try:
            # Select the drop down mean for fusion type display
            ui = get_current("ui")
            time.sleep(0.2)
            ui.TitleBar.Navigation.MenuItem["Patient modeling"].Button.Click()
            time.sleep(0.2)
            ui.TabControl_Modules.TabItem["Image registration"].Select()
            time.sleep(0.2)
            ui.TabControl_ToolBar.TabItem["Fusion"].Select()
            time.sleep(0.2)
            ui.TabControl_ToolBar.ToolBarGroup[0].DisplayModeToolPanel.ComboBox.ToggleButton.Click()
            
            # Send key presses to move to "Checkers" 
            for _ in range(5):
                SendKeys.SendWait("{UP}")
                time.sleep(0.2)
            SendKeys.SendWait("{DOWN}")  # Move from default to next item
            time.sleep(0.2)
            SendKeys.SendWait("{ENTER}")  # Select it
        except Exception as e:
            _logger.warning(f"User likely clicking during automated UI adjustments: {e}")
    
    @staticmethod
    def set_ui_to_image_registration():
        try:
            ui = get_current("ui")
            time.sleep(0.2)
            ui.ToolPanel.TabItem['ROIs'].Select()
            time.sleep(0.2)
            ui.TitleBar.Navigation.MenuItem["Patient modeling"].Button.Click()
            time.sleep(0.2)
            ui.TabControl_Modules.TabItem["Image registration"].Select()
            time.sleep(0.2)
            ui.TabControl_ToolBar.TabItem["Automatic tools"].Select()
        except Exception as e:
            _logger.warning(f"User likely clicking during automated UI adjustments: {e}")

    @staticmethod
    def user_message(title, message):
        
        # Create a temporary Tkinter window (it won't be shown)
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        
        # Make the temporary window topmost
        root.attributes('-topmost', True)
        
        # Display an information message box with an OK button
        messagebox.showinfo(title, message)
        
        # Destroy the hidden Tkinter window
        root.destroy()

    def pause_for_manual_registration(self):
        
        # Set fusion display mode
        self.set_fusion_display_mode()
        
        # Set to manual tools
        ui = get_current("ui")
        time.sleep(0.2)
        ui.TabControl_ToolBar.TabItem["Manual tools"].Select()
        
        # Await user interaction
        message = "Coarsely align images manually and then hit the Script execution play button."
        set_progress(message, percentage = -1)
        await_user_input(message=message)
    
    def get_initial_alignment(self, moving_name):
        moving_image_pp = self.case.Examinations[moving_name].PatientPosition
        fixed_image_pp = self.case.Examinations[self.fixed_name].PatientPosition
        rotations = ALIGNMENT_ROTATIONS[f"{moving_image_pp}-{fixed_image_pp}"]
        trans_and_center = {
            "Translation": self.translation,
            "RotationCenter": { 'x': 0, 'y': 0, 'z': 0 }
        }
        initial_alignment = {**rotations, **trans_and_center}
        _logger.info(f"Initial Alignment: {initial_alignment}")
        return initial_alignment
    
    def create_for_registration(self, moving_name):
        
        # Set current progress bar
        set_progress(f'Performing registration of {moving_name} to {self.fixed_name}...', percentage = -1)
        
        # Update registration name to match Raystation nomenclature
        initial_registration_name = "Frame-of-reference " + moving_name + " -> " + self.fixed_name
        
        # Set uniue registration name
        registration_name = self.create_unique_registration_name(initial_registration_name)
        
        # Create FoR registration
        self.case.CreateNamedIdentityFrameOfReferenceRegistration(FromExaminationName=moving_name, 
                                                                  ToExaminationName=self.fixed_name, 
                                                                  RegistrationName=registration_name, 
                                                                  Description=None)
        
        # Set initial rigid rotation transformation
        self.case.SetFoRRegistrationRigidTransformation(FromExaminationName=moving_name, 
                                                        ToExaminationName=self.fixed_name,     
                                                        RigidTransformation=self.get_initial_alignment(moving_name))
        
        # Perform ROI based registration or user intereaction for CT registration
        if self.moving_exam.EquipmentInfo.Modality == "CT" or self.fixed_exam.PatientPosition != self.moving_exam.PatientPosition:
            try:
                self.case.ComputeROIBasedFoRRegistration(FloatingExaminationName=moving_name, ReferenceExaminationName=self.fixed_name, DiscardRotations=False, RoiNames=[self.target_roi_name])
            except Exception:
                pass
        
        # Allow for user to manually adjust initial rigid transformation
        self.pause_for_manual_registration()
        
        # Perform gray level based image registration appended to the end of the list of registrations
        set_progress(f'Performing registration of {moving_name} to {self.fixed_name}...', percentage = -1)
        self.case.ComputeGrayLevelBasedRigidRegistration(FloatingExaminationName=moving_name,
                                                         ReferenceExaminationName=self.fixed_name,
                                                         RegistrationName=registration_name,
                                                         UseOnlyTranslations=False, 
                                                         HighWeightOnBones=False, 
                                                         InitializeImages=False, 
                                                         FocusRoisNames=[self.fusion_roi_name])
    
    def create_image_registration(self, moving_name):
        # Set current progress bar
        set_progress(f'Performing registration of {moving_name} to {self.fixed_name}...', percentage = -1)
        
        # Update registration name to match Raystation nomenclature
        initial_registration_name = "Image registration " + moving_name + " -> " + self.fixed_name
        
        # Set uniue registration name
        registration_name = self.create_unique_registration_name(initial_registration_name)
        
        # Create image registration
        self.case.CreateNamedIdentityImageRegistration(FromExaminationName=moving_name, 
                                                       ToExaminationName=self.fixed_name, 
                                                       RegistrationName=registration_name, 
                                                       Description=None)
        
        # Find registration number
        self.get_registration_number_from_name(registration_name)
        
        # Set initial rigid rotation transformation
        self.case.RigidRegistrations[self.registration_number].SetImageRegistrationRigidTransformation(
            RigidTransformation=self.get_initial_alignment(moving_name)
        )
        
        # Perform ROI based registration or user intereaction for CT registration
        if self.moving_exam.EquipmentInfo.Modality == "CT" or self.fixed_exam.PatientPosition != self.moving_exam.PatientPosition:
            try:
                self.case.RigidRegistrations[self.registration_number].ComputeROIBasedImageRegistration(DiscardRotations=False, RoiNames=[self.target_roi_name])
            except Exception:
                pass
        
        # Allow for user to manually adjust initial rigid transformation
        self.pause_for_manual_registration()
        
        # Perform gray level based image registration appended to the end of the list of registrations
        set_progress(f'Performing registration of {moving_name} to {self.fixed_name}...', percentage = -1)
        self.case.RigidRegistrations[self.registration_number].ComputeGrayLevelBasedImageRegistration(UseOnlyTranslations=False, 
                                                                                                      HighWeightOnBones=False, 
                                                                                                      InitializeImages=False, 
                                                                                                      FocusRoisNames=[self.fusion_roi_name]) 
    
    def run_dls_model(self, ct_exam, dls_model_name, roi_name):
        
        # Set current progress bar
        set_progress(f"Running DLS for {roi_name} on {ct_exam.Name}...", percentage = -1)
        
        # Run DLS
        ct_exam.RunDeepLearningSegmentationComposite(ExaminationsAndRegistrations={ ct_exam.Name: None }, ModelNamesAndRoisToInclude={ dls_model_name: [roi_name] })
     
    def roi_has_contours(self, exam_name, roi_name):
        if self.case.PatientModel.StructureSets[exam_name].RoiGeometries[roi_name].HasContours():
            return True
        return False
    
    def process_fusion_structure(self, ct_exam, roi_name):
        if self.run_dls_flag:
            _logger.info("Running DSL model...")
            model = dls_model_for(roi_name)
            if model is None:
                return
        
            if roi_name in self.roi_names:
                if not self.pdu.has_contours_on_ct(roi_name, ct_exam.Name):
                    self.run_dls_model(ct_exam, model.value, roi_name)
            else:
                self.run_dls_model(ct_exam, model.value, roi_name)

    
    def run_fusion(self):
        try:
           
            # Set the window and level for all the CT and MRI series
            self.set_window_level()
            
            # Checking for default series and ROI data
            self.check_for_skipping_user_popup()
            
            # Check if roi name is none and perform user selection window if true
            if self.target_roi_name is None:
                self.fusion_popup()
            else:
                _logger.info("Fusion popup window step skipped.")
                self.run_dls_flag = False
            
            # Convert moving names to a list of strings
            if isinstance(self.moving_names, str):
                self.moving_names = [self.moving_names]
            
            # Set current progress bar
            set_progress('Checking inputs...', percentage = -1)
            
            # Get the fixed image name
            self.get_exam(self.fixed_name)
            
            # Set names for focus region for fusion
            self.create_unique_fusion_roi_name()
            
            # Create External contour if needed
            self.create_external(self.fixed_exam, self.fixed_name)
            
            # Run DLS on fixed exam
            self.process_fusion_structure(self.fixed_exam, self.target_roi_name)
            
            # Calcualte target center
            self.calculate_target_center()
            
            # Get box size for fusion box
            self.get_box_size()
            
            # Create fusion box ROI
            self.create_fusion_box()
            
            # Loop through each moving image
            for moving_name in self.moving_names:
                _logger.info(f"Current moving image name: {moving_name}")
                
                # Get the moving image name
                self.get_exam(moving_name, image_type="moving")
                
                # Create external and DLS structure for CT moving images only
                if self.moving_exam.EquipmentInfo.Modality == "CT":
                    self.create_external(self.moving_exam, moving_name)
                    self.process_fusion_structure(self.moving_exam, self.target_roi_name)
                
                # Set current progress bar
                set_progress(f'Performing registration of {moving_name} to {self.fixed_name}...', percentage = -1)
                
                # Calculate the translation vector to put the moving image center over the target center on the CT
                self.calculate_initial_translation()
                
                # Create the registration
                _logger.info(f"Creating registration for moving image named {moving_name}...")
                if self.registration_type == "Frame of Reference":
                    try:
                        self.create_for_registration(moving_name)
                        
                    except Exception as e:
                        message_1 = f"Frame of Reference registration of {moving_name} and {self.fixed_name} failed."
                        message_2 = "  Frame of Reference likely already exists."
                        message_3 = "  Switiching to Image Registration."
                        message = message_1 + message_2 + message_3
                        messagebox.showerror("Warning", message)
                        self.create_image_registration(moving_name)
                    
                else:
                    self.create_image_registration(moving_name)
            
            #----After For Loop ----
            
            # Set fusion display mode
            self.set_fusion_display_mode()
            
            # Set view for fusion with ROI tool panel displayed
            self.set_ui_to_image_registration()

        except Exception as e:
            _alert_physicist_error(e, message=__name__)
            _logger.error("[FAILED] in %s.  Email notification sent.  Exception: %s", __name__, str(e))
            set_progress("Waiting for user to hit play button...", percentage = -1)
            await_user_input(message=f"[FAILED] script.  Physicist alerted to address the issue: {str(e)}")
            set_progress("Sending physicist notification...", percentage = -1)
            time.sleep(3)
            self._abort_script_error(exc=e, message=str(e))
            
