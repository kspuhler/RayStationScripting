# -*- coding: utf-8 -*-
"""Prostate fusion performed automatically if a single CT and single MRI exist 
and known target structure with contours.  Otherwise, user selects CT and MRI.
The user selected target structure can be another structure with contours or a
DSL-created prostate structure.  The fusion is centered around the target structure
using a fusion box focus region and rigid body registration.

Created on Wed Mar 25 16:03:31 2025

@author: clanco01
"""

from connect import *
import math
import sys
import clr
clr.AddReference('System.Windows.Forms')
from System.Windows.Forms import SendKeys
import time

# Correct the script directory (use the folder, not the file)
script_dir = r"\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD\Fusion_Prostate"
sys.path.append(script_dir)

# Import classes
from FusionPopup import FusionPopup

class CreateProstateFusion:
    def __init__(self):
        
        # Initialize all attributes
        self.box_size = {}
        self.case = get_current("Case")
        self.ct_exam = None
        self.ct_name = None
        self.fusion_roi_name = None
        self.mri_center_coord = {}
        self.mri_exam = None
        self.mri_name = None
        self.patient_model = get_current("Case").PatientModel
        self.registration_number = -1
        self.registration_name = None
        self.roi_names = None
        self.selected_values = {}
        self.target_center = {}
        self.target_roi_name = None
        self.target_names = ["GTVp", "MDGTV", "Prostate"]
        self.translation = {}
    
    def get_roi_names(self):
        self.roi_names = [roi.Name for roi in self.patient_model.RegionsOfInterest]
        
    def get_registration_number_from_name(self):
        
        # Find the registration number
        for i, registration in enumerate(self.case.RigidRegistrations):
            if registration.Name == self.registration_name:
                self.registration_number = i
                break  # Stop searching after the first match
                
        if self.registration_number == -1:
            print("Registration name not found")
            exit()
    
    def get_box_size(self):
        # Get the corners of the ROI bounding box and center of the ROI
        bounds = self.patient_model.StructureSets[self.ct_name].RoiGeometries[self.target_roi_name].GetBoundingBox()
        center = self.patient_model.StructureSets[self.ct_name].RoiGeometries[self.target_roi_name].GetCenterOfRoi()
        
        # Get the maximum distance between the center and bounding box
        max_distance = max(
            abs(center[axis] - bounds[i][axis])
            for axis in ['x', 'y', 'z']
            for i in (0, 1)
        )
        
        # Set box size
        edge_length = max(10, 2 * max_distance)
        self.box_size = {"x": edge_length, "y": edge_length, "z": edge_length}
    
    def create_unique_fusion_roi_name(self, base_name="FusionBox"):
        # Start with base name
        self.fusion_roi_name = base_name
        suffix = 1
    
        # Keep modifying the name until it's unique
        while self.fusion_roi_name in self.roi_names:
            self.fusion_roi_name = f"{base_name}_{suffix}"
            suffix += 1
    
    def create_unique_registration_name(self):
        existing_registration_names = [registration.Name for registration in self.case.RigidRegistrations]
        
        # Initialize name
        base_name = self.mri_name + " to " + self.ct_name
        self.registration_name = base_name
        suffix = 1
    
        # Keep modifying the name until it's unique
        while self.registration_name in existing_registration_names:
            print("Passing through while loop...")
            self.registration_name = f"{base_name}_{suffix}"
            suffix += 1
    
    def check_default_series_roi_data(self):
        # Find CT and MR Examinations
        ct_exams = [exam for exam in self.case.Examinations.values() if exam.EquipmentInfo.Modality == 'CT']
        mr_exams = [exam for exam in self.case.Examinations.values() if exam.EquipmentInfo.Modality == 'MR']
    
        if len(ct_exams) != 1 or len(mr_exams) != 1:
            return None, None, None
    
        self.ct_name = ct_exams[0].Name
        self.ct_exam = ct_exams[0]
        self.mri_name = mr_exams[0].Name
        self.mri_exam = mr_exams[0]
    
        # Find the first target ROI that exists and has a PrimaryShape
        for name in self.target_names:
            if name in self.roi_names:
                roi_geom = self.patient_model.StructureSets[self.ct_name].RoiGeometries[name]
                if roi_geom.HasContours():
                    self.target_roi_name = name
                    return
    
    def delete_auto_contour_roi(self):
        # Delete auto contoured prostate if exists
        if "AutoTargetCreated" in self.selected_values.keys():
            if self.selected_values["AutoTargetCreated"]:
                self.patient_model.RegionsOfInterest[self.selected_values["TargetName"]].DeleteRoi()
   
    def create_external(self):
        # Create if no External exists in the ROI list of the Patient Model
        if "External" not in self.roi_names:
            # Set current progress bar
            set_progress('Creating External structure...', percentage = -1)
            self.patient_model.CreateRoi(Name="External", Color="Green", Type="External", TissueName="", RbeCellTypeName=None, RoiMaterial=None)
        
        # Check if the exam has contours for external
        if not self.patient_model.StructureSets[self.ct_name].RoiGeometries["External"].HasContours():
            # Set current progress bar
            set_progress('Creating External contours...', percentage = -1)
            self.patient_model.RegionsOfInterest["External"].CreateExternalGeometry(Examination=self.ct_exam, ThresholdLevel=-250)
            
    def calculate_initial_translation(self):
        # Calculate target center
        self.target_center = self.patient_model.StructureSets[self.ct_name].RoiGeometries[self.target_roi_name].GetCenterOfRoi()
        
        # Calculate MIR series center coordinate
        self.mri_center_coord = self.get_center_series_coord(self.mri_exam.Series[0])
        
        # Calculate the translation vector to put the MRI center over the target center on the CT
        self.translation = {"x": self.target_center["x"] - self.mri_center_coord["x"],
                            "y": self.target_center["y"] - self.mri_center_coord["y"],
                            "z": self.target_center["z"] - self.mri_center_coord["z"]}
        
    def fusion_popup(self):
    
        # Set current progress bar
        set_progress('User window open and user selecting inputs...', percentage = -1)
        
        # Use slection window to get selected values for fusion
        window = FusionPopup()
        window.mainloop()
        
        # Assign output
        self.selected_values = window.get_values()
        self.ct_name = self.selected_values["ReferenceImageName"]
        self.mri_name = self.selected_values["FusingImageName"]
        self.target_roi_name = self.selected_values["TargetName"]
    
    def get_exam(self,exam_name):
        
        # Get exam
        exam = self.case.Examinations[exam_name]
        
        # Verify exam patient position
        if exam.PatientPosition != "HFS":
            await_user_input(message="{exam.EquipmentInfo.Modality} series is not HFS patient position.  Not currently supported.")
            exit()
        
        # Check exam type and assign
        exam_type = exam.EquipmentInfo.Modality
        if exam_type == "CT":
            self.ct_exam = exam
            self.ct_exam.SetPrimary()
        elif exam_type == "MR":
            self.mri_exam = exam
            self.mri_exam.SetSecondary()
        else:
            await_user_input(message="{exam.Name} series type is not a CT or MRI.  Not currently supported.")
            exit()
    
    def create_fusion_box(self):
        
        # Create the fusion box
        fusion_box = self.case.PatientModel.CreateRoi(Name=self.fusion_roi_name, Color="SaddleBrown", Type="Control", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)

        # Create the box with user input properties and centered at the target center
        fusion_box.CreateBoxGeometry(Size=self.box_size, Examination=self.ct_exam, Center=self.target_center, Representation="TriangleMesh", VoxelSize=None)

    def set_window_level(self):
        ct_window_level = {"x": 100, "y": 750}
        mri_window_level = {"x": 500, "y": 1000}
        
        for exam in self.case.Examinations:
            if exam.EquipmentInfo.Modality == 'CT':
                exam.Series[0].LevelWindow = ct_window_level
            elif exam.EquipmentInfo.Modality == 'MR':
                exam.Series[0].LevelWindow = mri_window_level

    def get_center_series_coord(self, series):
        
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
        
    @staticmethod
    def set_fusion_display_mode():
        # Select the drop down mean for fusion type display
        ui = get_current("ui")
        ui.TitleBar.Navigation.MenuItem["Patient modeling"].Button.Click()
        ui.TabControl_Modules.TabItem["Image registration"].Select()
        ui.TabControl_ToolBar.TabItem["Fusion"].Select()
        ui.TabControl_ToolBar.ToolBarGroup[0].DisplayModeToolPanel.ComboBox.ToggleButton.Click()
        
        # Send key presses to move to "Checkers" 
        for _ in range(5):
            SendKeys.SendWait("{UP}")
            time.sleep(0.2)
        SendKeys.SendWait("{DOWN}")  # Move from default to next item
        time.sleep(0.2)
        SendKeys.SendWait("{ENTER}")  # Select it
    
    @staticmethod
    def set_ui_to_image_registration():
        ui = get_current("ui")
        ui.ToolPanel.TabItem['ROIs'].Select()
        ui.TitleBar.Navigation.MenuItem["Patient modeling"].Button.Click()
        ui.TabControl_Modules.TabItem["Image registration"].Select()
        ui.TabControl_ToolBar.TabItem["Automatic tools"].Select()


    def run_fusion(self):
        # Get initial list of ROI names
        self.get_roi_names()
        
        # Set view for fusion with ROI tool panel displayed
        self.set_ui_to_image_registration()
        
        # Set the window and level for all the CT and MRI series
        self.set_window_level()
        
        # Checking for default series and ROI data
        self.check_default_series_roi_data()
        
        # Check if roi name is none and perform user selection window if true
        if self.target_roi_name is None:
            self.fusion_popup()
            
        # Set current progress bar
        set_progress('Checking inputs...', percentage = -1)
        
        # Get the reference CT exam
        self.get_exam(self.ct_name)
        self.get_exam(self.mri_name)
        
        # Create External contour if needed
        self.create_external()
        
        # Set current progress bar
        set_progress('Initial rigid registration...', percentage = -1)
        
        # Set names for focus region for fusion and registration name
        self.create_unique_fusion_roi_name()
        self.create_unique_registration_name()
        
        # Calculate the translation vector to put the MRI center over the target center on the CT
        self.calculate_initial_translation()
        
        # Get box size for fusion box
        self.get_box_size()
        
        # Create fusion box ROI
        self.create_fusion_box()
        
        # Create the registration
        self.case.CreateNamedIdentityImageRegistration(FromExaminationName=self.mri_name, ToExaminationName=self.ct_name, RegistrationName=self.registration_name, Description=None)
        
        # Set fusion display mode
        self.set_fusion_display_mode()
        
        # Set view for fusion with ROI tool panel displayed
        self.set_ui_to_image_registration()
        
        # Find registration number
        self.get_registration_number_from_name()
        
        # Perform a rigid registration with translations to align center of MRI with center of target on the CT
        self.case.RigidRegistrations[self.registration_number].SetImageRegistrationRigidTransformation(RigidTransformation={ 'YawDegrees': 0, 'PitchDegrees': 0, 'RollDegrees': 0, 'Translation': self.translation, 'RotationCenter': { 'x': 0, 'y': 0, 'z': 0 } })
        
        # Set current progress bar
        set_progress('Performing rigid registration...', percentage = -1)
        
        # Perform gray level based image registration appended to the end of the list of registrations
        self.case.RigidRegistrations[self.registration_number].ComputeGrayLevelBasedImageRegistration(UseOnlyTranslations=False, HighWeightOnBones=False, InitializeImages=False, FocusRoisNames=[self.fusion_roi_name])
        
        # Delete prostate ROI if created
        self.delete_auto_contour_roi()


# Run main function
if __name__ == "__main__":
    fusion = CreateProstateFusion()
    fusion.run_fusion()
