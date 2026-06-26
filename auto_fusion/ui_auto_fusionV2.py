r""" 
auto_fusion\ui_auto_fusion.py

AutoFusion user popup window.

Created on 10/01/2025
Modified 11/13/2025

@author: clanco01
"""

from __future__ import annotations

# === DEBUG SETTINGS ===
_DEBUG_THIS_MODULE = False

# === WORKING DIRECTORY ===
import sys
sys.path.append(r"\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
sys.path.append(r"F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")

# === Main library imports ===
import sys
import tkinter as tk
from tkinter import ttk, messagebox

# === Local imports ===
from RSutil.ErrorsUtil.rs_errors import report_error
from RSutil.ErrorsUtil.error_codes import PROMPT_USER
from auto_fusion.constants_auto_fusion import (
    ALLOWED_DLS_NAMES, 
    REGISTRATION_TYPES, 
    ALLOWED_IMAGE_TYPES,
    ALLOWED_PATIENT_POSITIONS,
)
from RSutil.patient_data_util import PatientDataUtil

class AutoFusionSelectionWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        
        # === Patient Data Util ===
        self.pdu = PatientDataUtil()
        
        # === UI confi ===
        self.title("User Selection for Fusion")
        self.geometry("500x600")  
        self.attributes('-topmost', True)  # Forces window to stay on top
        self.values = {}
        self.default_font = ("Arial", 12)
        self.button_font = ("Arial", 13)
        
        # Set registration type names
        self.reg_type_names = REGISTRATION_TYPES.copy()
        
        # Allowed image types
        self.allowed_images_types = ALLOWED_IMAGE_TYPES.copy()
        
        # Set auto-contour name
        self.roi_names = self.pdu.get_roi_names()
        self.target_prefix = "Auto_Contour_"
        self.auto_target_names = [f"{self.target_prefix}{name}" for name in ALLOWED_DLS_NAMES]
        
        # Get all ROI names
        self.default_roi_name = next((target for target in ALLOWED_DLS_NAMES if target in self.roi_names), self.auto_target_names[0])

        # Get series names and defaults for dropdown values
        self.fixed_names = self.pdu.get_ct_exam_names()
        self.default_fixed_name = self.pdu.get_ct_exam_name_newest()
        self._get_moving_exam_names()
        
        # Instructions label at the top
        instructions = tk.Label(self,
            text=f"The fusion will be centered around the structure selected.  You can select a structure already contoured or select a '{self.target_prefix}' structure to let the script automatically create a contour.  For CT-CT based fusions, selecting an auto-contoured structure improves performance.",
            font=self.default_font, wraplength=400, justify="center")
        instructions.pack(pady=(10, 20))  # Some vertical padding

        # Reference (Fixed) Image
        ttk.Label(self, text="Select Reference Image (CT):", font=self.default_font).pack(pady=5)
        self.fixed_scan_dropdown = ttk.Combobox(self, values=self.fixed_names, font=self.default_font)
        self.fixed_scan_dropdown.set(self.default_fixed_name)
        self.fixed_scan_dropdown.pack(pady=5)
        
        # Fusing Scan - Target (Moving) Image
        ttk.Label(self, text="Select Image(s) to Fuse (CT or MRI):", font=self.default_font).pack(pady=5)
        list_frame = tk.Frame(self)
        list_frame.pack(pady=5)
        self.moving_scan_listbox = tk.Listbox(list_frame, selectmode=tk.MULTIPLE, font=self.default_font, 
                                              height=6, width=20, exportselection=False)
        self.moving_scan_listbox.pack(side=tk.LEFT, fill=tk.BOTH)
        scrollbar = tk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.moving_scan_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.moving_scan_listbox.config(yscrollcommand=scrollbar.set)
        for exam_name in self.all_exam_names:
            self.moving_scan_listbox.insert(tk.END, exam_name)
        # Pre-select the default moving name if present
        if self.default_moving_name in self.all_exam_names:
            index = self.all_exam_names.index(self.default_moving_name)
            self.moving_scan_listbox.selection_set(index)
        self.moving_scan_listbox.pack(pady=5)

        # Target drop down menu
        ttk.Label(self, text="Select Target Structure:", font=self.default_font).pack(pady=5)
        structure_options = self.auto_target_names + self.roi_names 
        max_height = 40
        height = min(len(structure_options), max_height)
        self.target_roi_dropdown = ttk.Combobox(self, values=structure_options, font=self.default_font, height=height)
        self.target_roi_dropdown.set(self.default_roi_name)
        self.target_roi_dropdown.pack(pady=5)
        
        # Registration Type
        ttk.Label(self, text="Select Registration Type:", font=self.default_font).pack(pady=5)
        self.registration_scan_dropdown = ttk.Combobox(self, values=self.reg_type_names, font=self.default_font)
        self.registration_scan_dropdown.set(self.reg_type_names[0])
        self.registration_scan_dropdown.pack(pady=5)

        # Create a custom style
        style = ttk.Style()
        style.configure("Custom.TButton", font=self.button_font)

        # Acknowledgement button
        button_frame = tk.Frame(self)
        button_frame.pack(pady=20)
        self.fusion_button = ttk.Button(button_frame, text="Perform Fusion", style="Custom.TButton", command=lambda: self._submit("Perform Fusion"))
        self.fusion_button.pack(side=tk.LEFT, padx=10)
        self.cancel_button = ttk.Button(button_frame, text="Cancel", style="Custom.TButton", command=lambda: self._submit("Cancel"))
        self.cancel_button.pack(side=tk.LEFT, padx=10)
        
        # Attach protocol to detect window closure
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
    
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
                context={"module": "ui_auto_fusion.py"},
                metadata={},
                message=message,
            )
    
    # === Sub-methods ===
    def _on_closing(self):
        self.destroy()
        sys.exit()  # Exit script safely
        
    def _get_moving_exam_names(self):
        # Set default moving name to be empty
        self.default_moving_name = ""
        
        # Get all exams
        all_exams = self.pdu.get_exams()
        
        try:
            sorted_exams = sorted(
                all_exams, 
                key=lambda exam: exam.GetExaminationDateTime(), 
                reverse=True
            )
        except Exception:
            sorted_exams = all_exams
        if len(sorted_exams) == 2:
            self.default_moving_name = sorted_exams[1].Name
            if self.default_moving_name == self.default_fixed_name:
                self.default_moving_name = sorted_exams[0].Name
        elif len(sorted_exams) < 2:
            message = "One or zero exams.  Fusion is not possible.  Script aborting..."
            self._prompt_user_acknowledge(
                exc=RuntimeError(message),
                message=message
            )
            self._on_closing()
            return  
        
        # Return all exam names
        self.all_exam_names = self.pdu.get_exam_names()

    def _submit(self, button):
        errors = []
        
        # Close script if user hits cancel button
        if button == "Cancel":
            self._on_closing()
        
        # Get images names
        fixed_image_name = self.fixed_scan_dropdown.get()
        selected_moving_names = [
            self.moving_scan_listbox.get(i)
            for i in self.moving_scan_listbox.curselection()
        ]
        if fixed_image_name in selected_moving_names:
            errors.append("The reference image and target image can not be the same.  Please select again.")
            errors.append("")
        
        if not selected_moving_names :
            errors.append("Select a target image.")
            errors.append("")
        
        if self.pdu.case.Examinations[fixed_image_name].PatientPosition not in ALLOWED_PATIENT_POSITIONS:
            errors.append(f"Patient position in {fixed_image_name} is not allowed.  Only {ALLOWED_PATIENT_POSITIONS} allowed.")
            errors.append("")
        
        for moving_name in selected_moving_names:
            if self.pdu.case.Examinations[moving_name].PatientPosition not in ALLOWED_PATIENT_POSITIONS:
                errors.append(f"Patient position in {moving_name} is not allowed.  Only {ALLOWED_PATIENT_POSITIONS} allowed.")
                errors.append("")
        
        for moving_name in selected_moving_names:
            moving_exam = self.pdu.case.Examinations[moving_name]
            if moving_exam.EquipmentInfo.Modality not in self.allowed_images_types:
               errors.append(f"At least one of the reference images is not in {self.allowed_images_types}.  Please select again.")
               errors.append("")
        
        # Set initial target name for output
        target_name = self.target_roi_dropdown.get()
        
        # Check for contours if no auto contour structure selected
        if target_name in self.auto_target_names:
            target_name = target_name.replace(self.target_prefix, "")
        else:
            if not self.pdu.case.PatientModel.StructureSets[self.fixed_scan_dropdown.get()].RoiGeometries[target_name].HasContours():
                errors.append(
                    "Select a structure with contours on the selected CT reference image or select one of the following:"
                )                   
                errors.append(f"{self.auto_target_names}")
                errors.append("")
        
        if errors:
            self._prompt_user_acknowledge(
                exc=ValueError("User selection errors:"), 
                message="\n".join(errors)
            )
            return
        
        self.values = {
            "ReferenceImageName": fixed_image_name,
            "FusingImageName": selected_moving_names,
            "TargetName": target_name,
            "RegistrtaionType": self.registration_scan_dropdown.get()
        }
        
        self.destroy()
    
    # === Main fetch method ===
    def get_values(self):
        return self.values
 

