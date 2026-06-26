from connect import *
import sys
import tkinter as tk
from tkinter import ttk, messagebox

class FusionPopupProstate(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("User Selection for Fusion")
        self.geometry("500x400")  
        self.attributes('-topmost', True)  # Forces window to stay on top
        self.values = {}
        self.default_font = ("Arial", 12)
        self.button_font = ("Arial", 13)
        
        # Set expected target names to search for
        self.target_names = ["GTVp", "MDGTV", "Prostate"]
        
        # Get current case
        self.case = get_current("Case")
        
        # Set auto-contour name
        self.auto_target_name = "Auto_Contour_Prostate"
        
        # Get series names and defaults for dropdown values
        self.get_ct_exam_names()
        self.get_mri_exam_names()
        
        # Get default ROI name to fill in the dropdown menu
        self.get_default_roi_name()
        
        # Instructions label at the top
        instructions = tk.Label(self,
            text=f"The fusion will be centered around the structure selected.  You can select a structure already contoured or select {self.auto_target_name} to let the script automatically create a prostate contour.",
            font=self.default_font, wraplength=400, justify="center")
        instructions.pack(pady=(10, 20))  # Some vertical padding

        # CT Planning Scan - Reference (Fixed) Image
        ttk.Label(self, text="Select Reference Image (CT):", font=self.default_font).pack(pady=5)
        self.ct_scan_dropdown = ttk.Combobox(self, values=self.ct_names, font=self.default_font)
        self.ct_scan_dropdown.set(self.default_ct_name)
        self.ct_scan_dropdown.pack(pady=5)
        
        # Fusing Scan - Target (Moving) Image
        ttk.Label(self, text="Select Image to Fuse (MRI):", font=self.default_font).pack(pady=5)
        self.mri_scan_dropdown = ttk.Combobox(self, values=self.mri_names, font=self.default_font)
        self.mri_scan_dropdown.set(self.default_mri_name)
        self.mri_scan_dropdown.pack(pady=5)

        # Target drop down menu
        ttk.Label(self, text="Select Target Structure:", font=self.default_font).pack(pady=5)
        if not self.default_roi_name:
            self.default_roi_name = self.auto_target_name
        structure_options = [self.auto_target_name] + self.roi_names 
        self.target_roi_dropdown = ttk.Combobox(self, values=structure_options, font=self.default_font)
        self.target_roi_dropdown.set(self.default_roi_name)
        self.target_roi_dropdown.pack(pady=5)

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

    def get_ct_exam_names(self):
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
        most_recent_ct = max(ct_exams, key=lambda exam: exam.GetExaminationDateTime())
        self.default_ct_name = most_recent_ct.Name
        
        # Return all CT exam names (optional: you could return default_ct_name too if needed)
        self.ct_names = [exam.Name for exam in ct_exams]
        
    def get_mri_exam_names(self):
        # Get all mri exams
        mri_exams = [exam for exam in self.case.Examinations if exam.EquipmentInfo.Modality == "MR"]
        
        # Handle case when there are no mris
        if not mri_exams:
            title = "Error"
            message = 'No MRI exams detected in current case.  Script will exit.'
            messagebox.showinfo(title, message)
            self.on_closing()
            return []  
        
        # Set the default mri to the most recent mri exam
        most_recent_mri = max(mri_exams, key=lambda exam: exam.GetExaminationDateTime())
        self.default_mri_name = most_recent_mri.Name
        
        # Return all mri exam names (optional: you could return default_mri_name too if needed)
        self.mri_names = [exam.Name for exam in mri_exams]
        
    def get_default_roi_name(self): 
        # Get ROI names
        self.roi_names = [roi.Name for roi in self.case.PatientModel.RegionsOfInterest]
        
        # Set default_roi to the first matching target name, or to an empty string
        self.default_roi_name = next((target for target in self.target_names if target in self.roi_names), "")

    def create_unique_roi_name(self, current_roi_name):
        # Keep modifying the name until it's unique
        unique_name = self.auto_target_name
        suffix = 1
        while unique_name in self.roi_names:
            unique_name = f"{self.auto_target_name}_{suffix}"
            suffix += 1
        
        self.case.PatientModel.RegionsOfInterest[current_roi_name].Name = unique_name

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

    def submit(self, button):
        
        # Set flag for DSl auto contouring of target
        auto_contour_created = False
        
        # Set initial target name for output
        target_name = self.target_roi_dropdown.get()
        
        # Close script if user hits cancel button
        if button == "Cancel":
            self.on_closing()
        
        # Auto contour using DSL if user selected auto contouring of the prostate
        if self.target_roi_dropdown.get() == self.auto_target_name:
            # Set current progress bar
            set_progress('Auto-contouring prostate...', percentage = -1)
            
            # Run DSL for prostate
            ct_name = self.ct_scan_dropdown.get()
            ct_exam = self.case.Examinations[ct_name]
            ct_exam.RunDeepLearningSegmentationComposite(ExaminationsAndRegistrations={ ct_name: None }, ModelNamesAndRoisToInclude={ 'RSL DLS Male Pelvic CT': ["Prostate"] })
            
            # set auto contour flag to true
            auto_contour_created = True
            
            # Set the name of the Prostate
            roi_names_post_dsl = [roi.Name for roi in self.case.PatientModel.RegionsOfInterest]
            roi_dsl_name = [roi for roi in roi_names_post_dsl if roi not in self.roi_names]
            if not roi_dsl_name:
                roi_dsl_name.append("Prostate")
            
            # Set the name of the auto-contoured target for output
            target_name = roi_dsl_name[0]
        
        # Check selected ROI has contours
        elif not self.case.PatientModel.StructureSets[self.ct_scan_dropdown.get()].RoiGeometries[self.target_roi_dropdown.get()].HasContours():
            messagebox.showerror("Error", f"Select a structure with contours on the selected CT reference image or select {self.auto_target_name}.")
            return
        
        # User selected a structure with contours to base the fusion upon
        else:
            print("User selected a target structure with contours.")
        
        self.values = {
            "ReferenceImageName": self.ct_scan_dropdown.get(),
            "FusingImageName": self.mri_scan_dropdown.get(),
            "TargetName": target_name,
            "AutoTargetCreated": auto_contour_created
        }
        self.destroy()
    
    def get_values(self):
        return self.values
 
# # Example usage
# if __name__ == "__main__":
#     window = FusionPopup()
#     window.mainloop()
#     selected_values = window.get_values()
#     print(selected_values)
