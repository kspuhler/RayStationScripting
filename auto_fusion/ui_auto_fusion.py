""" 
AutoFusion user popup window.

version 3.0

Created on 10/01/2025

@author: clanco01
"""

from connect import *
import sys
import tkinter as tk
from tkinter import ttk, messagebox

script_dir = r"\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD"
sys.path.append(script_dir)

from auto_fusion.constants_auto_fusion import (
    ALLOWED_DLS_NAMES, 
    REGISTRATION_TYPES, 
    ALLOWED_IMAGE_TYPES,
    ALLOWED_PATIENT_POSITIONS,
)

class AutoFusionSelectionWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("User Selection for Fusion")
        self.geometry("500x600")  
        self.attributes('-topmost', True)  # Forces window to stay on top
        self.values = {}
        self.default_font = ("Arial", 12)
        self.button_font = ("Arial", 13)
        
        # Get current case
        self.case = get_current("Case")
        
        # Set registration type names
        self.reg_type_names = REGISTRATION_TYPES.copy()
        
        # Allowed image types
        self.allowed_images_types = ALLOWED_IMAGE_TYPES.copy()
        
        # Set auto-contour name
        self.roi_names = [roi.Name for roi in self.case.PatientModel.RegionsOfInterest]
        self.target_prefix = "Auto_Contour_"
        self.auto_target_names = [f"{self.target_prefix}{name}" for name in ALLOWED_DLS_NAMES]
        
        # Get all ROI names
        self.default_roi_name = next((target for target in ALLOWED_DLS_NAMES if target in self.roi_names), self.auto_target_names[0])

        # Get series names and defaults for dropdown values
        self.get_fixed_exam_names()
        self.get_moving_exam_names()
        
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
        self.fusion_button = ttk.Button(button_frame, text="Perform Fusion", style="Custom.TButton", command=lambda: self.submit("Perform Fusion"))
        self.fusion_button.pack(side=tk.LEFT, padx=10)
        self.cancel_button = ttk.Button(button_frame, text="Cancel", style="Custom.TButton", command=lambda: self.submit("Cancel"))
        self.cancel_button.pack(side=tk.LEFT, padx=10)
        
        # Attach protocol to detect window closure
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    # Define behavior when closing with "X"
    def on_closing(self):
        print("Exiting script...")
        self.destroy()
        sys.exit()  # Exit script safely

    def get_fixed_exam_names(self):
        # Get all CT exams
        ct_exams = [exam for exam in self.case.Examinations if exam.EquipmentInfo.Modality == "CT"]
        
        # Handle case when there are no CTs
        if not ct_exams:
            title = "Error"
            message = 'No CT exams detected in current case.  Script will exit.'
            messagebox.showinfo(title, message)
            self.on_closing()
            return []  
        
        # Set the default CT to the most recent CT exam
        try:
            most_recent_ct = max(ct_exams, key=lambda exam: exam.GetExaminationDateTime())
        except Exception:
            most_recent_ct = ct_exams[0]
        self.default_fixed_name = most_recent_ct.Name
        
        # Return all CT exam names (optional: you could return default_ct_name too if needed)
        self.fixed_names = [exam.Name for exam in ct_exams]
        
    def get_moving_exam_names(self):
        # Set default moving name to be empty
        self.default_moving_name = ""
        
        # Get all exams
        all_exams = [exam for exam in self.case.Examinations]
        
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
            title = "Error"
            message = 'Only a single exam exists.  No fusion is possible.  Script will exit.'
            messagebox.showinfo(title, message)
            self.on_closing()
            return []  
        
        # Return all exam names
        self.all_exam_names = [exam.Name for exam in all_exams]

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

    def show_custom_error(self, errors, title="Input Errors"):
        error_window = tk.Toplevel(self)
        error_window.title(title)
        error_window.transient(self)  # keep it on top of parent
        error_window.grab_set()       # block interaction with main window
    
        message = "\n".join(errors)
    
        label = tk.Label(error_window, text=message, font=self.default_font, justify="left", anchor="w")
        label.pack(padx=20, pady=20)
    
        ok_button = tk.Button(error_window, text="OK", command=error_window.destroy)
        ok_button.pack(pady=(0, 15))
    
        # Automatically size to fit the message
        error_window.update_idletasks()
        width = label.winfo_reqwidth() + 40
        height = label.winfo_reqheight() + 80
        error_window.geometry(f"{width}x{height}")
        
        # Center it on screen
        w = error_window.winfo_width()
        h = error_window.winfo_height()
        ws = error_window.winfo_screenwidth()
        hs = error_window.winfo_screenheight()
        x = (ws // 2) - (w // 2)
        y = (hs // 2) - (h // 2)
        error_window.geometry(f'{w}x{h}+{x}+{y}')

    def submit(self, button):
        errors = []
        
        # Close script if user hits cancel button
        if button == "Cancel":
            self.on_closing()
        
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
        
        if self.case.Examinations[fixed_image_name].PatientPosition not in ALLOWED_PATIENT_POSITIONS:
            errors.append(f"Patient position in {fixed_image_name} is not allowed.  Only {ALLOWED_PATIENT_POSITIONS} allowed.")
            errors.append("")
        
        for moving_name in selected_moving_names:
            if self.case.Examinations[moving_name].PatientPosition not in ALLOWED_PATIENT_POSITIONS:
                errors.append(f"Patient position in {moving_name} is not allowed.  Only {ALLOWED_PATIENT_POSITIONS} allowed.")
                errors.append("")
        
        for moving_name in selected_moving_names:
            moving_exam = self.case.Examinations[moving_name]
            if moving_exam.EquipmentInfo.Modality not in self.allowed_images_types:
               errors.append(f"At least one of the reference images is not in {self.allowed_images_types}.  Please select again.")
               errors.append("")
        
        # Set initial target name for output
        target_name = self.target_roi_dropdown.get()
        
        # Check for contours if no auto contour structure selected
        if target_name in self.auto_target_names:
            target_name = target_name.replace(self.target_prefix, "")
        else:
            if not self.case.PatientModel.StructureSets[self.fixed_scan_dropdown.get()].RoiGeometries[target_name].HasContours():
                errors.append(f"Select a structure with contours on the selected CT reference image or select one of the following:")                   
                errors.append(f"{self.auto_target_names}")
                errors.append("")
        
        if errors:
            self.show_custom_error(errors)
            return
        
        self.values = {
            "ReferenceImageName": fixed_image_name,
            "FusingImageName": selected_moving_names,
            "TargetName": target_name,
            "RegistrtaionType": self.registration_scan_dropdown.get()
        }
        
        self.destroy()
    
    def get_values(self):
        return self.values
 

