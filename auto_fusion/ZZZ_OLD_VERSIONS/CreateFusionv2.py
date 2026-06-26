# -*- coding: utf-8 -*-
""" 
The user selects the fixed (refernce) and moving (target) images for fusion.  
More than one moving image can be selected.
The user selected target structure can be another structure with contours or a
DSL-created  structure.  The fusion is centered around the target structure
using a fusion box focus region and rigid body registration.
Either a frame of reference or image registration fusion can be performed.
CT and MRIs are the only image types allowed.

version 2.0

Created on 09/09/2025

@author: clanco01
"""

from connect import *
import math
import sys
import clr
clr.AddReference('System.Windows.Forms')
from System.Windows.Forms import SendKeys
import time
import tkinter as tk
from tkinter import messagebox

# Correct the script directory (use the folder, not the file)
script_dir = r"\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD\AutoFusion"
sys.path.append(script_dir)

# Import classes
from FusionPopup import FusionPopup

class CreateFusion:
    def __init__(self):
        
        # Initialize all attributes
        self.box_size = {}
        self.case = get_current("Case")
        self.fixed_exam = None
        self.fixed_name = None
        self.fusion_roi_name = None
        self.moving_center_coord = {}
        self.moving_exam = None
        self.moving_names = None
        self.patient_model = get_current("Case").PatientModel
        self.registration_number = -1
        self.registration_name = None
        self.roi_names = None
        self.selected_values = {}
        self.target_center = {}
        self.target_roi_name = None
        self.target_names = ["GTVp", "Prostate", "Brain"]
        self.auto_contour_delete = ["Prostate"]
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
        bounds = self.patient_model.StructureSets[self.fixed_name].RoiGeometries[self.target_roi_name].GetBoundingBox()
        center = self.patient_model.StructureSets[self.fixed_name].RoiGeometries[self.target_roi_name].GetCenterOfRoi()
        
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
    
    def create_unique_registration_name(self, moving_name):
        existing_registration_names = [registration.Name for registration in self.case.RigidRegistrations]
        
        # Initialize name
        base_name = moving_name + " to " + self.fixed_name
        self.registration_name = base_name
        suffix = 1
    
        # Keep modifying the name until it's unique
        while self.registration_name in existing_registration_names:
            self.registration_name = f"{base_name}_{suffix}"
            suffix += 1
    
    def check_default_series_roi_data(self):
        # Find CT and MR Examinations
        ct_exams = [exam for exam in self.case.Examinations.values() if exam.EquipmentInfo.Modality == 'CT']
        mr_exams = [exam for exam in self.case.Examinations.values() if exam.EquipmentInfo.Modality == 'MR']
    
        if len(ct_exams) != 1 or len(mr_exams) != 1:
            return None, None, None
    
        self.fixed_name = ct_exams[0].Name
        self.fixed_exam = ct_exams[0]
        self.moving_names = mr_exams[0].Name
        self.moving_exam = mr_exams[0]
    
        # Find the first target ROI that exists and has a PrimaryShape
        for name in self.target_names:
            if name in self.roi_names:
                roi_geom = self.patient_model.StructureSets[self.fixed_name].RoiGeometries[name]
                if roi_geom.HasContours():
                    self.target_roi_name = name
                    return
    
    def delete_auto_contour_roi(self):
        # Delete auto contoured  if exists
        if ("AutoTargetCreated" in self.selected_values.keys()
            and self.selected_values["AutoTargetCreated"]
            and any(s in self.selected_values["TargetName"] for s in self.auto_contour_delete)
        ):
                self.patient_model.RegionsOfInterest[self.selected_values["TargetName"]].DeleteRoi()
   
    def create_external(self, exam, exam_name):
        # Create if no External exists in the ROI list of the Patient Model
        if "External" not in self.roi_names:
            # Set current progress bar
            set_progress('Creating External structure...', percentage = -1)
            try:
                self.patient_model.CreateRoi(Name="External", Color="Green", Type="External", TissueName="", RbeCellTypeName=None, RoiMaterial=None)
            except Exception as e:
                print(f"Error: {e}")
        
        # Check if the exam has contours for external
        if not self.patient_model.StructureSets[exam_name].RoiGeometries["External"].HasContours():
            # Set current progress bar
            set_progress('Creating External contours...', percentage = -1)
            self.patient_model.RegionsOfInterest["External"].CreateExternalGeometry(Examination=exam, ThresholdLevel=-250)
    
    def calculate_target_center(self):
        self.target_center = self.patient_model.StructureSets[self.fixed_name].RoiGeometries[self.target_roi_name].GetCenterOfRoi()
    
    def calculate_initial_translation(self):
        # Calculate moving series center coordinate
        self.moving_center_coord = self.get_center_series_coord(self.moving_exam.Series[0])
        
        # Calculate the translation vector to put the moving image center over the target center on the CT
        self.translation = {"x": self.target_center["x"] - self.moving_center_coord["x"],
                            "y": self.target_center["y"] - self.moving_center_coord["y"],
                            "z": self.target_center["z"] - self.moving_center_coord["z"]}
        
    def fusion_popup(self):
    
        # Set current progress bar
        set_progress('User window open and user selecting inputs...', percentage = -1)
        
        # Use slection window to get selected values for fusion
        window = FusionPopup()
        window.mainloop()
        
        # Assign output
        self.selected_values = window.get_values()
        self.fixed_name = self.selected_values["ReferenceImageName"]
        self.moving_names = self.selected_values["FusingImageName"]
        self.target_roi_name = self.selected_values["TargetName"]
        self.registration_type = self.selected_values["RegistrtaionType"]
    
    def get_exam(self, exam_name, image_type="fixed"):
        
        # Get exam
        exam = self.case.Examinations[exam_name]
        
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
            print(f"User likely clicking during automated UI adjustments: {e}")
    
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
            print(f"User likely clicking during automated UI adjustments: {e}")

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
        
    def run_fusion(self):
        
        # Get initial list of ROI names
        self.get_roi_names()
        
        # Set the window and level for all the CT and MRI series
        self.set_window_level()
        
        # Checking for default series and ROI data
        self.check_default_series_roi_data()
        
        # Check if roi name is none and perform user selection window if true
        if self.target_roi_name is None:
            self.fusion_popup()
        else:
            self.registration_type = "Image Registration"
        
        # Convert moving names to a list of strings
        if isinstance(self.moving_names, str):
            self.moving_names = [self.moving_names]
        
        # Set current progress bar
        set_progress('Checking inputs...', percentage = -1)
        
        # Get the fixed image name
        self.get_exam(self.fixed_name)
        
        # Set names for focus region for fusion
        self.create_unique_fusion_roi_name()
        
        # Calcualte target center
        self.calculate_target_center()
        
        # Get box size for fusion box
        self.get_box_size()
        
        # Create fusion box ROI
        self.create_fusion_box()
        
        # Create External contour if needed
        self.create_external(self.fixed_exam, self.fixed_name)
          
        # Loop through each moving image
        for moving_name in self.moving_names:
            # Get the moving image name
            self.get_exam(moving_name, image_type="moving")
            
            # Create external for CT moving images only
            if self.moving_exam.EquipmentInfo.Modality == "CT":
                self.create_external(self.moving_exam, moving_name)
            
            # Set current progress bar
            set_progress(f'Initial rigid registration on {moving_name}...', percentage = -1)
            
            # Set uniue registration name
            self.create_unique_registration_name(moving_name)
            
            # Calculate the translation vector to put the moving image center over the target center on the CT
            self.calculate_initial_translation()
            
            # Set current progress bar
            set_progress(f'Performing registration of {moving_name} to {self.fixed_name}...', percentage = -1)
            
            # Create the registration
            if self.registration_type == "Frame of Reference":
                try:
                    # Create FoR registration
                    self.case.CreateNamedIdentityFrameOfReferenceRegistration(FromExaminationName=moving_name, 
                                                                              ToExaminationName=self.fixed_name, 
                                                                              RegistrationName=self.registration_name, 
                                                                              Description=None)
                    
                    # Perform a rigid registration with translations to align center of moving image with center of target on the CT
                    if self.moving_exam.EquipmentInfo.Modality == "MR":
                        self.case.SetFoRRegistrationRigidTransformation(
                            FromExaminationName=moving_name,
                            ToExaminationName=self.fixed_name,
                            RigidTransformation={ 'YawDegrees': 0, 'PitchDegrees': 0, 'RollDegrees': 0, 'Translation': self.translation, 'RotationCenter': { 'x': 0, 'y': 0, 'z': 0 } })
                    
                    # Wait for user intereaction for CT registration
                    if self.moving_exam.EquipmentInfo.Modality == "CT" or self.fixed_exam.PatientPosition != self.moving_exam.PatientPosition:
                        self.pause_for_manual_registration()
                    
                    # Set current progress bar
                    set_progress(f'Performing registration of {moving_name} to {self.fixed_name}...', percentage = -1)    
                    
                    # Perform gray level based image registration appended to the end of the list of registrations
                    self.case.ComputeGrayLevelBasedRigidRegistration(FloatingExaminationName=moving_name,
                                                                     ReferenceExaminationName=self.fixed_name,
                                                                     RegistrationName=self.registration_name,
                                                                     UseOnlyTranslations=False, 
                                                                     HighWeightOnBones=False, 
                                                                     InitializeImages=False, 
                                                                     FocusRoisNames=[self.fusion_roi_name])
                    
                except Exception as e:
                    message_1 = f"Frame of Reference registration of {moving_name} to {self.fixed_name} failed."
                    message_2 = "  Check if Frame of Reference already exists."
                    message = message_1 + message_2
                    messagebox.showerror("Error", message)
                
            else:
                # Create image registration
                self.case.CreateNamedIdentityImageRegistration(FromExaminationName=moving_name, 
                                                               ToExaminationName=self.fixed_name, 
                                                               RegistrationName=self.registration_name, 
                                                               Description=None)
            
                # Find registration number
                self.get_registration_number_from_name()
                
                # Perform a rigid registration with translations to align center of moving image with center of target on the CT
                if self.moving_exam.EquipmentInfo.Modality == "MR":
                    self.case.RigidRegistrations[self.registration_number].SetImageRegistrationRigidTransformation(
                        RigidTransformation={ 'YawDegrees': 0, 'PitchDegrees': 0, 'RollDegrees': 0, 'Translation': self.translation, 'RotationCenter': { 'x': 0, 'y': 0, 'z': 0 } })
                
                # Wait for user intereaction for CT registration
                if self.moving_exam.EquipmentInfo.Modality == "CT" or self.fixed_exam.PatientPosition != self.moving_exam.PatientPosition:
                    self.pause_for_manual_registration()
                
                # Set current progress bar
                set_progress(f'Performing registration of {moving_name} to {self.fixed_name}...', percentage = -1)
                
                # Perform gray level based image registration appended to the end of the list of registrations
                self.case.RigidRegistrations[self.registration_number].ComputeGrayLevelBasedImageRegistration(UseOnlyTranslations=False, 
                                                                                                              HighWeightOnBones=False, 
                                                                                                              InitializeImages=False, 
                                                                                                              FocusRoisNames=[self.fusion_roi_name])    
        
        #----After For Loop ----
        
        # Set fusion display mode
        self.set_fusion_display_mode()
        
        # Set view for fusion with ROI tool panel displayed
        self.set_ui_to_image_registration()
        
        # Delete ROI if created
        self.delete_auto_contour_roi()


