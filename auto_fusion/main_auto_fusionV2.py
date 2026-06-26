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
_ALERT_PHYSICIST_ON_ALL_USES = True

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
import sys
import clr
clr.AddReference('System.Windows.Forms')
from System.Windows.Forms import SendKeys
import time
from typing import Any

# === Local imports ===
from RSutil.LogUtil.rs_logging import LOGGERS, set_logger_mode
from auto_fusion.ui_auto_fusionV2 import AutoFusionSelectionWindow
from auto_fusion.constants_auto_fusion import dls_model_for, SKIP_POPUP_ROI_NAMES, ALIGNMENT_ROTATIONS
from RSutil.ErrorsUtil.error_dispatcher import DispatcherConfig
from RSutil.ErrorsUtil.rs_errors import report_error
from RSutil.ErrorsUtil.error_codes import PROMPT_USER, ALERT_PHYSICIST, ABORT_SCRIPT, SKIP_STEP
from RSutil.patient_data_util import PatientDataUtil

# === Setup Logger ===
_logger = LOGGERS["auto_fusion"]
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
        _logger.info("Intializaing AutoFusion...")
        
        # Patient Data Util
        self.pdu = PatientDataUtil()
        
        # Initialize all attributes
        self.box_size = {}
        self.fixed_exam: Any | None = None
        self.fixed_name: str | None = None
        self.fusion_roi_name: str | None = None
        self.moving_exam: Any | None = None
        self.moving_names: str | None = None
        self.registration_number = -1
        self.roi_names = self.pdu.get_roi_names()
        self.selected_values: dict[str, Any] | None = None
        self.target_center: dict[str, float] | None = None
        self.target_roi_name: str | None = None
        self.skip_popup_roi_names = SKIP_POPUP_ROI_NAMES
        self.translation: dict[str, float] | None = None
        self.run_dls_flag = True
        self.box_min_size = 10
        self.box_max_size = 30
        self.max_char_reg_name = 64
        self.allowed_exam_types = ["CT", "MR"]
        self.ct_window_level = {"x": 100, "y": 750}
        self.mri_window_level = {"x": 500, "y": 1000}

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
                context={"module": "main_auto_fusion.py"},
                metadata={},
                message=message,
            )
        
    def _skip_step_error(
            self, 
            exc: Exception, 
            metadata: dict | None = None, 
            message: str | None = None
    ):                                                  
        report_error(
                error_def=SKIP_STEP.UIUX_RSUI_FAILURE, 
                original_exception=exc, 
                context={"module": "main_auto_fusion.py"},
                metadata={},
                message=message,
            )
    
    def _abort_script_error(
            self, 
            exc: Exception, 
            metadata: dict | None = None, 
            message: str | None = None
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

    # === Helper methods ===    
    def _get_registration_number_from_name(self, registration_name: str) -> None:
        
        # Find the registration number
        for i, registration in enumerate(self.pdu.case.RigidRegistrations):
            if registration.Name == registration_name:
                self.registration_number = i
                break  # Stop searching after the first match
                
        if self.registration_number == -1:
            e = ValueError("No registration found.")
            self._prompt_user_acknowledge(
                exc=e, 
                message="No registration found.  Script will exit."
            )
            self._abort_script_error(exc=e)

    def _create_unique_registration_name(self, initial_registration_name: str) -> str:
        existing_registration_names = [registration.Name for registration in self.pdu.case.RigidRegistrations]
        
        # Initialize name
        registration_name = initial_registration_name
        suffix = 1
    
        # Keep modifying the name until it's unique
        while registration_name in existing_registration_names:
            registration_name = f"{initial_registration_name}_{suffix}"
            suffix += 1
            
        return registration_name[:self.max_char_reg_name]

    def _get_center_series_coord(self, series):
        
        # Get center x and y coordinates
        center = {}
        center["x"] = series.ImageStack.NrPixels.x/ 2 * series.ImageStack.PixelSize.x + series.ImageStack.Corner.x
        center["y"] = series.ImageStack.NrPixels.y/ 2 * series.ImageStack.PixelSize.y + series.ImageStack.Corner.y
        
        # Get center z coordinate
        center_slice = len(series.ImageStack.SlicePositions) / 2 - 0.5
        center_slice_floor = math.floor(center_slice)
        center_slice_ceil = math.ceil(center_slice)
        center_slice_position = (series.ImageStack.SlicePositions[center_slice_floor] + series.ImageStack.SlicePositions[center_slice_ceil]) / 2
        center["z"] = center_slice_position + series.ImageStack.Corner.z
        
        return center

    def _pause_for_manual_registration(self):
        
        # Set fusion display mode
        self._set_fusion_display_mode()
        
        # Set to manual tools
        try:
            ui = get_current("ui")
            time.sleep(0.2)
            ui.TabControl_ToolBar.TabItem["Manual tools"].Select()
        except Exception as e:
            self._skip_step_error(exc=e)
        
        # Await user interaction
        message = "Coarsely align images manually and then hit the Script execution play button."
        set_progress(message, percentage = -1)
        await_user_input(message=message)

    def _get_initial_alignment(self, moving_name):
        moving_image_pp = self.pdu.case.Examinations[moving_name].PatientPosition
        fixed_image_pp = self.pdu.case.Examinations[self.fixed_name].PatientPosition
        rotations = ALIGNMENT_ROTATIONS[f"{moving_image_pp}-{fixed_image_pp}"]
        trans_and_center = {
            "Translation": self.translation,
            "RotationCenter": { 'x': 0, 'y': 0, 'z': 0 }
        }
        initial_alignment = {**rotations, **trans_and_center}
        
        return initial_alignment

    def _run_dls_model(self, ct_exam, dls_model_name, roi_name):
        set_progress(f"Running DLS for {roi_name} on {ct_exam.Name}...", percentage = -1)
        ct_exam.RunDeepLearningSegmentationComposite(
            ExaminationsAndRegistrations={ ct_exam.Name: None }, 
            ModelNamesAndRoisToInclude={ dls_model_name: [roi_name] }
        )
    
    # === Sub-methods ===
    def _get_box_size(self):
        # Get the corners of the ROI bounding box and center of the ROI
        bounds = self.pdu.patient_model.StructureSets[self.fixed_name].RoiGeometries[self.target_roi_name].GetBoundingBox()
        center = self.pdu.get_roi_center_coord_on_ct(self.target_roi_name, self.fixed_name)
        # Get the maximum distance between the center and bounding box
        max_distance = max(
            abs(center[axis] - bounds[i][axis])
            for axis in ['x', 'y', 'z']
            for i in (0, 1)
        )
        
        # Set box size
        edge_length = min(self.box_max_size, max(self.box_min_size, 2 * max_distance))
        self.box_size = {"x": edge_length, "y": edge_length, "z": edge_length}
    
    def _create_unique_fusion_roi_name(self, base_name="FusionBox"):
        # Start with base name
        self.fusion_roi_name = base_name
        suffix = 1
    
        # Keep modifying the name until it's unique
        while self.fusion_roi_name in self.roi_names:
            self.fusion_roi_name = f"{base_name}_{suffix}"
            suffix += 1
    
    def _check_for_skipping_user_popup(self):
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
            if (
                name in self.roi_names
                and self.pdu.has_contours_on_ct(name, self.fixed_name)
            ):
                self.target_roi_name = name
                return
    
    def _create_external(self, exam, exam_name):
        # Create if no External exists in the ROI list of the Patient Model
        if not self.pdu.has_roi_external():
            # Set current progress bar
            set_progress('Creating External structure...', percentage = -1)
            try:
                self.pdu.patient_model.CreateRoi(
                    Name="External", 
                    Color="Green", 
                    Type="External", 
                    TissueName="", 
                    RbeCellTypeName=None, 
                    RoiMaterial=None
                )
            except Exception as e:
                print(f"Error: {e}")
        
        # Check if the exam has contours for external
        if not self.pdu.has_roi_external_contour_on_ct(exam_name):
            # Set current progress bar
            set_progress('Creating External contours...', percentage = -1)
            ext_name = self.pdu.get_roi_external_name()
            self.pdu.patient_model.RegionsOfInterest[ext_name].CreateExternalGeometry(
                Examination=exam, 
                ThresholdLevel=-250
                )
    
    def _calculate_initial_translation(self):
        # Calculate series center coordinate
        moving_center_coord = self._get_center_series_coord(self.moving_exam.Series[0])
        
        # Calculate the translation vector to put the moving image center over the target center on the CT
        self.translation = {
            "x": self.target_center["x"] - moving_center_coord["x"],
            "y": self.target_center["y"] - moving_center_coord["y"],
            "z": self.target_center["z"] - moving_center_coord["z"],
        }
        
    def _fusion_popup(self):
    
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
    
    def _get_exam(self, exam_name, image_type="fixed"):
        
        # Get exam
        exam = self.pdu._get_exam_with_exam_name(exam_name)
        
        # Check exam type and assign
        exam_type = exam.EquipmentInfo.Modality
        if exam_type not in self.allowed_exam_types:
            message = "Selected exam type not supported."
            e = ValueError(message)
            self._prompt_user_acknowledge(exc=e)
            self._abort_script_error(exc=e)
            
        if image_type == "fixed":
            self.fixed_exam = exam
            self.fixed_exam.SetPrimary()
        else:
            self.moving_exam = exam
            self.moving_exam.SetSecondary()
    
    def _create_fusion_box(self):
        
        # Create the fusion box
        fusion_box = self.pdu.case.PatientModel.CreateRoi(
            Name=self.fusion_roi_name, 
            Color="SaddleBrown", 
            Type="Control", 
            TissueName=None, 
            RbeCellTypeName=None, 
            RoiMaterial=None
        )

        # Create the box with user input properties and centered at the target center
        fusion_box.CreateBoxGeometry(
            Size=self.box_size, 
            Examination=self.fixed_exam, 
            Center=self.target_center, 
            Representation="TriangleMesh", 
            VoxelSize=None
        )

    def _set_window_level(self):
        for exam in self.pdu.get_exams() :
            if exam.EquipmentInfo.Modality == 'CT':
                exam.Series[0].LevelWindow = self.ct_window_level
            elif exam.EquipmentInfo.Modality == 'MR':
                exam.Series[0].LevelWindow = self.mri_window_level
        
    def _set_fusion_display_mode(self) -> None:
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
            self._skip_step_error(exc=e)
    
    def _set_ui_to_image_registration(self):
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
            self._skip_step_error(exc=e)
    
    def _create_for_registration(self, moving_name):
        
        # Set current progress bar
        set_progress(f'Performing registration of {moving_name} to {self.fixed_name}...', percentage = -1)
        
        # Update registration name to match Raystation nomenclature
        initial_registration_name = "Frame-of-reference " + moving_name + " -> " + self.fixed_name
        
        # Set uniue registration name
        registration_name = self._create_unique_registration_name(initial_registration_name)
        
        # Create FoR registration
        self.pdu.case.CreateNamedIdentityFrameOfReferenceRegistration(FromExaminationName=moving_name, 
                                                                  ToExaminationName=self.fixed_name, 
                                                                  RegistrationName=registration_name, 
                                                                  Description=None)
        
        # Set initial rigid rotation transformation
        self.pdu.case.SetFoRRegistrationRigidTransformation(FromExaminationName=moving_name, 
                                                        ToExaminationName=self.fixed_name,     
                                                        RigidTransformation=self._get_initial_alignment(moving_name))
        
        # Perform ROI based registration or user intereaction for CT registration
        if self.moving_exam.EquipmentInfo.Modality == "CT" or self.fixed_exam.PatientPosition != self.moving_exam.PatientPosition:
            try:
                self.pdu.case.ComputeROIBasedFoRRegistration(FloatingExaminationName=moving_name, ReferenceExaminationName=self.fixed_name, DiscardRotations=False, RoiNames=[self.target_roi_name])
            except:
                self._pause_for_manual_registration()
        
        # Perform gray level based image registration appended to the end of the list of registrations
        set_progress(f'Performing registration of {moving_name} to {self.fixed_name}...', percentage = -1)
        self.pdu.case.ComputeGrayLevelBasedRigidRegistration(FloatingExaminationName=moving_name,
                                                         ReferenceExaminationName=self.fixed_name,
                                                         RegistrationName=registration_name,
                                                         UseOnlyTranslations=False, 
                                                         HighWeightOnBones=False, 
                                                         InitializeImages=False, 
                                                         FocusRoisNames=[self.fusion_roi_name])
    
    def _create_image_registration(self, moving_name):
        # Set current progress bar
        set_progress(f'Performing registration of {moving_name} to {self.fixed_name}...', percentage = -1)
        
        # Update registration name to match Raystation nomenclature
        initial_registration_name = "Image registration " + moving_name + " -> " + self.fixed_name
        
        # Set uniue registration name
        registration_name = self._create_unique_registration_name(initial_registration_name)
        
        # Create image registration
        self.pdu.case.CreateNamedIdentityImageRegistration(FromExaminationName=moving_name, 
                                                       ToExaminationName=self.fixed_name, 
                                                       RegistrationName=registration_name, 
                                                       Description=None)
        
        # Find registration number
        self._get_registration_number_from_name(registration_name)
        
        # Set initial rigid rotation transformation
        self.pdu.case.RigidRegistrations[self.registration_number].SetImageRegistrationRigidTransformation(
            RigidTransformation=self._get_initial_alignment(moving_name)
        )
        
        # Perform ROI based registration or user intereaction for CT registration
        if self.moving_exam.EquipmentInfo.Modality == "CT" or self.fixed_exam.PatientPosition != self.moving_exam.PatientPosition:
            try:
                self.pdu.case.RigidRegistrations[self.registration_number].ComputeROIBasedImageRegistration(DiscardRotations=False, RoiNames=[self.target_roi_name])
            except:
                self._pause_for_manual_registration()
        
        # Perform gray level based image registration appended to the end of the list of registrations
        set_progress(f'Performing registration of {moving_name} to {self.fixed_name}...', percentage = -1)
        self.pdu.case.RigidRegistrations[self.registration_number].ComputeGrayLevelBasedImageRegistration(UseOnlyTranslations=False, 
                                                                                                      HighWeightOnBones=False, 
                                                                                                      InitializeImages=False, 
                                                                                                      FocusRoisNames=[self.fusion_roi_name]) 
    
    def _process_fusion_structure(self, ct_exam, roi_name):
        if self.run_dls_flag:
            model = dls_model_for(roi_name)
            if model is None:
                return
        
            if roi_name in self.roi_names:
                if not self.pdu.has_contours_on_ct(roi_name, self.pdu.get_exam_name_from_exam(ct_exam)): 
                    self._run_dls_model(ct_exam, model.value, roi_name)
            else:
                self._run_dls_model(ct_exam, model.value, roi_name)

    
    def run_fusion(self):
        try:
            # Set the window and level for all the CT and MRI series
            self._set_window_level()
            
            # Checking for default series and ROI data
            self._check_for_skipping_user_popup()
            
            # Check if roi name is none and perform user selection window if true
            if self.target_roi_name is None:
                self._fusion_popup()
            else:
                self.registration_type = "Image Registration"
                self.run_dls_flag = False
            
            # Convert moving names to a list of strings
            if isinstance(self.moving_names, str):
                self.moving_names = [self.moving_names]
            
            # Set current progress bar
            set_progress('Checking inputs...', percentage = -1)
            
            # Get the fixed image name
            self._get_exam(self.fixed_name)
            
            # Set names for focus region for fusion
            self._create_unique_fusion_roi_name()
            
            # Create External contour if needed
            self._create_external(self.fixed_exam, self.fixed_name)
            
            # Run DLS on fixed exam
            self._process_fusion_structure(self.fixed_exam, self.target_roi_name)
            
            # Calcualte target center
            self.target_center = self.pdu.get_roi_center_coord_on_ct(
                self.target_roi_name, 
                self.fixed_name
            )
            
            # Get box size for fusion box
            self._get_box_size()
            
            # Create fusion box ROI
            self._create_fusion_box()
            
            # Loop through each moving image
            for moving_name in self.moving_names:
                # Get the moving image name
                self._get_exam(moving_name, image_type="moving")
                
                # Create external and DLS structure for CT moving images only
                if self.moving_exam.EquipmentInfo.Modality == "CT":
                    self._create_external(self.moving_exam, moving_name)
                    self._process_fusion_structure(self.moving_exam, self.target_roi_name)
                
                # Set current progress bar
                set_progress(f'Performing registration of {moving_name} to {self.fixed_name}...', percentage = -1)
                
                # Calculate the translation vector to put the moving image center over the target center on the CT
                self._calculate_initial_translation()
                
                # Create the registration
                if self.registration_type == "Frame of Reference":
                    try:
                        self._create_for_registration(moving_name)
                        
                    except Exception as e:
                        message_1 = f"Frame of Reference registration of {moving_name} and {self.fixed_name} failed."
                        message_2 = "  Check if Frame of Reference already exists."
                        message_3 = "  Switiching to Image Registration."
                        message = message_1 + message_2 + message_3
                        self._prompt_user_acknowledge(exc=e, message=message)
                        self._create_image_registration(moving_name)
                    
                else:
                    self._create_image_registration(moving_name)
            
            #----After For Loop ----
            
            # Set fusion display mode
            self._set_fusion_display_mode()
            
            # Set view for fusion with ROI tool panel displayed
            self._set_ui_to_image_registration()

        except Exception as e:
            _alert_physicist_error(e, message=__name__)
            _logger.error("[FAILED] in %s.  Email notification sent.  Exception: %s", __name__, str(e))
            set_progress("Waiting for user to hit play button...", percentage = -1)
            await_user_input(message="[FAILED] script.  Physicist alerted to address the issue.")
            set_progress("Sending physicist notification...", percentage = -1)
            time.sleep(3)
            self._abort_script_error(exc=e, message=str(e))
            
