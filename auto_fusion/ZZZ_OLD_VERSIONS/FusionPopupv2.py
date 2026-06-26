from connect import *
import sys
import tkinter as tk
from tkinter import ttk, messagebox

class FusionPopup(tk.Tk):
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
        
        # Set auto-contour name
        self.target_prefix = "Auto_Contour_"
        self.dsl_male_pelvic_names = ["Prostate"]
        self.dsl_hn_names = ["Brain"]
        self.target_bases = self.dsl_male_pelvic_names + self.dsl_hn_names
        self.auto_target_names = [f"{self.target_prefix}{name}" for name in self.target_bases]
        
        # Set registration type names
        self.reg_type_names = ["Image Registration", "Frame of Reference"]
        
        # Allowed image types
        self.allowed_images_types = ["CT", "MR"]
        
        # Get all ROI names
        self.get_default_roi_name()
        
        # Get series names and defaults for dropdown values
        self.get_fixed_exam_names()
        self.get_moving_exam_names()
        
        # Instructions label at the top
        instructions = tk.Label(self,
            text=f"The fusion will be centered around the structure selected.  You can select a structure already contoured or select a '{self.target_prefix}' structure to let the script automatically create a contour.",
            font=self.default_font, wraplength=400, justify="center")
        instructions.pack(pady=(10, 20))  # Some vertical padding

        # Reference (Fixed) Image
        ttk.Label(self, text="Select Reference Image (CT):", font=self.default_font).pack(pady=5)
        self.fixed_scan_dropdown = ttk.Combobox(self, values=self.fixed_names, font=self.default_font)
        self.fixed_scan_dropdown.set(self.default_fixed_name)
        self.fixed_scan_dropdown.pack(pady=5)
        
        # Fusing Scan - Target (Moving) Image
        ttk.Label(self, text="Select Image(s) to Fuse (CT or MRI):", font=self.default_font).pack(pady=5)
        self.moving_scan_listbox = tk.Listbox(self, selectmode=tk.MULTIPLE, font=self.default_font, 
                                              height=6, width=20, exportselection=False)
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
        self.target_roi_dropdown = ttk.Combobox(self, values=structure_options, font=self.default_font)
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
        most_recent_ct = max(ct_exams, key=lambda exam: exam.GetExaminationDateTime())
        self.default_fixed_name = most_recent_ct.Name
        
        # Return all CT exam names (optional: you could return default_ct_name too if needed)
        self.fixed_names = [exam.Name for exam in ct_exams]
        
    def get_moving_exam_names(self):
        # Set default moving name to be empty
        self.default_moving_name = ""
        
        # Get all exams
        all_exams = [exam for exam in self.case.Examinations]
        
        sorted_exams = sorted(all_exams, key=lambda exam: exam.GetExaminationDateTime(), reverse=True)
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

    def get_default_roi_name(self): 
        # Get ROI names
        self.roi_names = [roi.Name for roi in self.case.PatientModel.RegionsOfInterest]
        
        # Set default_roi to the first matching target name, or to an empty string
        self.default_roi_name = next((target for target in self.target_bases if target in self.roi_names), self.auto_target_names[0])

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
            messagebox.showerror("Error", "The reference image and target image can not be the same.  Please select again.")
            return
        
        if not selected_moving_names :
            messagebox.showerror("Error", "Select a target image.")
            return
        
        for moving_name in selected_moving_names:
            moving_exam = self.case.Examinations[moving_name]
            if moving_exam.EquipmentInfo.Modality not in self.allowed_images_types:
               messagebox.showerror("Error", f"At least one of the reference images is not in {self.allowed_images_types}.  Please select again.")
               return 
        
        # Set flag for DLS auto contouring of target
        auto_contour_created = False
        
        # Set initial target name for output
        target_name = self.target_roi_dropdown.get()
        
        # Auto contour using DSL if user selected auto contouring
        if target_name in self.auto_target_names:
            # Set current progress bar
            set_progress('Auto-contouring ...', percentage = -1)
            
            # Run DSL for 
            ct_name = self.fixed_scan_dropdown.get()
            ct_exam = self.case.Examinations[ct_name]
            target_base = target_name.replace(self.target_prefix, "")
            dls_model_name = ""
            if target_base in self.dsl_male_pelvic_names: 
                dls_model_name = "RSL DLS Male Pelvic CT"
            elif target_base in self.dsl_hn_names:
                dls_model_name = "RSL DLS Head and Neck CT"
            else:
                messagebox.showerror("Error", f"Select a structure with contours on the selected CT reference image or select {self.auto_target_names}.")
                return
            
            ct_exam.RunDeepLearningSegmentationComposite(ExaminationsAndRegistrations={ ct_name: None }, ModelNamesAndRoisToInclude={ dls_model_name: [target_base] })
            
            # set auto contour flag to true
            auto_contour_created = True
            
            # Set the name of the target
            roi_names_post_dsl = [roi.Name for roi in self.case.PatientModel.RegionsOfInterest]
            roi_dsl_name = [roi for roi in roi_names_post_dsl if roi not in self.roi_names]
            if not roi_dsl_name:
                roi_dsl_name.append("")
            target_name = roi_dsl_name[0]
            
        # Check selected ROI has contours
        elif not self.case.PatientModel.StructureSets[self.fixed_scan_dropdown.get()].RoiGeometries[target_name].HasContours():
            messagebox.showerror("Error", f"Select a structure with contours on the selected CT reference image or select {self.auto_target_names}.")
            return
        
        # User selected a structure with contours to base the fusion upon
        else:
            print("User selected a target structure with contours.")
        
        self.values = {
            "ReferenceImageName": fixed_image_name,
            "FusingImageName": selected_moving_names,
            "TargetName": target_name,
            "RegistrtaionType": self.registration_scan_dropdown.get(),
            "AutoTargetCreated": auto_contour_created
        }
        
        self.destroy()
    
    def get_values(self):
        return self.values
 

