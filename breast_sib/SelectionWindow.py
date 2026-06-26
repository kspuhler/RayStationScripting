from connect import *
import sys
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

class SelectionWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Treatment Plan Setup")
        self.geometry("800x1000")  
        self.attributes('-topmost', True)  # Forces window to stay on top
        self.values = {}
        self.default_font = ("Arial", 12)
        self.patient_model = get_current("Case").PatientModel
        self.case = get_current("Case")
        self.machines_names = ["21EX", "TrueBeamSN1106"]
        self.patient_positions = ["HeadFirstSupine", "FeetFirstSupine", "HeadFirstProne", "FeetFirstProne"]
        self.ct_patient_positions = ["HFS", "FFS", "HFP", "FFP"]
        self.tangents_treatment_type = "Tangents Only"
        self.tangents_and_sib_treatment_type = "Tangents + SIB"
        
        # Load beamsets and fields
        self.get_current_plan_beamset_and_beam_names()
        self.structure_names = self.get_current_structure_names()
        
        # Plan Name
        ttk.Label(self, text="Enter Plan Name:", font=self.default_font).pack(pady=5)
        self.plan_name_input = tk.Entry(self, font=self.default_font)
        self.plan_name_input.pack(pady=5)
        
        # CT Planning Scan
        ttk.Label(self, text="Select Planning Image Set:", font=self.default_font).pack(pady=5)
        self.ct_scan_dropdown = ttk.Combobox(self, values=self.get_ct_exam_names(), font=self.default_font)
        self.ct_scan_dropdown.pack(pady=5)
        
        # Patient treatment position
        ttk.Label(self, text="Select Patient Treatment Position:", font=self.default_font).pack(pady=5)
        self.patient_position_dropdown = ttk.Combobox(self, values=self.patient_positions, font=self.default_font)
        self.patient_position_dropdown.current(0)
        self.patient_position_dropdown.pack(pady=5)
        
        # Machine Selection
        ttk.Label(self, text="Select Machine:", font=self.default_font).pack(pady=5)
        self.machine_dropdown = ttk.Combobox(self, values=self.machines_names, font=self.default_font)
        self.machine_dropdown.current(0)
        self.machine_dropdown.pack(pady=5)

        # Percentage of 15 MV Dose
        ttk.Label(self, text="Percentage of 15 MV Dose (0 - 50%):", font=self.default_font).pack(pady=5)
        self.percentage_spinbox = tk.Spinbox(self, from_=0, to=50, font=self.default_font)
        self.percentage_spinbox.pack(pady=5)

        # Prescription
        ttk.Label(self, text="Enter Prescription (cGy):", font=self.default_font).pack(pady=5)
        self.prescription_input = tk.Entry(self, font=self.default_font)
        self.prescription_input.pack(pady=5)

        # Prescription ROI Name
        ttk.Label(self, text="Select Prescription ROI Name:", font=self.default_font).pack(pady=5)
        default_roi = "PTV_Tangents" if "PTV_Tangents" in self.structure_names else ("PTV Tangents" if "PTV Tangents" in self.structure_names else "")
        self.prescription_roi_dropdown = ttk.Combobox(self, values=self.structure_names, font=self.default_font)
        if default_roi:
            self.prescription_roi_dropdown.set(default_roi)
        self.prescription_roi_dropdown.pack(pady=5)

        # Prescription Dose at Volume (%)
        ttk.Label(self, text="Enter Prescription Dose at Volume (0 - 100%):", font=self.default_font).pack(pady=5)
        self.prescription_dose_volume_input = tk.Entry(self, font=self.default_font)
        self.prescription_dose_volume_input.insert(0, "95")
        self.prescription_dose_volume_input.pack(pady=5)

        # Fractionation
        ttk.Label(self, text="Enter the Number of Fractions:", font=self.default_font).pack(pady=5)
        self.fractionation_input = tk.Entry(self, font=self.default_font)
        self.fractionation_input.pack(pady=5)

        # Plan that contains the beams to copy
        ttk.Label(self, text="Select Physician Open Field Plan:", font=self.default_font).pack(pady=5)
        self.plan_dropdown = ttk.Combobox(self, values=list(self.plan_beamsets.keys()), font=self.default_font)
        self.plan_dropdown.pack(pady=5)

        # Beamset that contatins the beams to copy
        ttk.Label(self, text="Select Physician Open Field Beamset:", font=self.default_font).pack(pady=5)
        self.beamset_dropdown = ttk.Combobox(self, font=self.default_font)
        self.beamset_dropdown.pack(pady=5)
        
        # Beams to copy
        ttk.Label(self, text="Select Beam(s) from Physician Open Field Beamset:", font=self.default_font).pack(pady=5)
        frame = tk.Frame(self)
        frame.pack(pady=5)
        self.beam_listbox = tk.Listbox(frame, selectmode=tk.MULTIPLE, exportselection=0, font=self.default_font, height=6, width=30)
        scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL, command=self.beam_listbox.yview)
        self.beam_listbox.config(yscrollcommand=scrollbar.set)
        self.beam_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Updates drop down menus
        self.plan_dropdown.bind("<<ComboboxSelected>>", self.update_beamsets)
        self.beamset_dropdown.bind("<<ComboboxSelected>>", self.update_beams)
        self.update_beams(None)  # Initialize with default plan fields

        # SIB Target Structure
        ttk.Label(self, text="Select SIB Target Structure:", font=self.default_font).pack(pady=5)
        default_sib = "PTV TB Eval" if "PTV TB Eval" in self.structure_names else "NA"
        self.sib_target_dropdown = ttk.Combobox(self, values=self.structure_names + (["NA"] if "PTV TB Eval" not in self.structure_names else []), font=self.default_font)
        self.sib_target_dropdown.set(default_sib)
        self.sib_target_dropdown.pack(pady=5)

        # Treatment Type Buttons
        button_frame = tk.Frame(self)
        button_frame.pack(pady=10)
        self.tangents_button = ttk.Button(button_frame, text=self.tangents_treatment_type, command=lambda: self.submit(self.tangents_treatment_type))
        self.tangents_button.pack(side=tk.LEFT, padx=10)
        self.tangents_sib_button = ttk.Button(button_frame, text=self.tangents_and_sib_treatment_type, command=lambda: self.submit(self.tangents_and_sib_treatment_type))
        self.tangents_sib_button.pack(side=tk.LEFT, padx=10)
        
        # Attach protocol to detect window closure
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    # Define behavior when closing with "X"
    def on_closing(self):
        print("User closed the window. Exiting script...")
        self.destroy()
        sys.exit()  # Exit script safely

    def update_beams(self, event):
        selected_plan = self.plan_dropdown.get()
        self.beam_listbox.delete(0, tk.END)
        for field in self.beamsets.get(selected_plan, []):
            self.beam_listbox.insert(tk.END, field)
        
    def get_current_plan_beamset_and_beam_names(self):
        self.plan_beamsets = {}
        for plan in self.case.TreatmentPlans:
            beamsets = {}
            for beamset in plan.BeamSets:
                beamsets[beamset.DicomPlanLabel] = [beam.Name for beam in beamset.Beams]
            self.plan_beamsets[plan.Name] = beamsets
 
    def update_beamsets(self, event):
        selected_plan = self.plan_dropdown.get()
        if selected_plan in self.plan_beamsets:
            beamset_options = list(self.plan_beamsets[selected_plan].keys())  # Extract beamset names
            self.beamset_dropdown["values"] = beamset_options  # Populate dropdown
            if beamset_options:
                self.beamset_dropdown.current(0)  # Select the first beamset by default
                self.update_beams(None)  # Update beams list based on the first beamset
            else:
                self.beamset_dropdown["values"] = []
                self.beamset_dropdown.set("")
                self.beam_listbox.delete(0, tk.END)
    
    def update_beams(self, event):
        selected_plan = self.plan_dropdown.get()
        selected_beamset = self.beamset_dropdown.get()
        self.beam_listbox.delete(0, tk.END)
        if selected_plan in self.plan_beamsets and selected_beamset in self.plan_beamsets[selected_plan]:
            for beam in self.plan_beamsets[selected_plan][selected_beamset]:
                self.beam_listbox.insert(tk.END, beam)    

    def get_ct_exam_names(self):
        return [exam.Name for exam in self.case.Examinations if exam.EquipmentInfo.Modality == "CT"]
    
    def get_current_structure_names(self):
        return [roi.Name for roi in self.case.PatientModel.RegionsOfInterest]
    
    def get_physician_beamset_machine(self):
        machine = "No Machine can be selected yet.  Waiting on user input."
        if self.plan_dropdown.get() in list(self.plan_beamsets.keys()):
            if self.beamset_dropdown.get() in list(self.plan_beamsets[self.plan_dropdown.get()]):
                machine = self.case.TreatmentPlans[self.plan_dropdown.get()].BeamSets[self.beamset_dropdown.get()].MachineReference.MachineName
        return machine

    def error_float_input(self, entry_widget, min_val=0, max_val=100):
    	try:
    		value = float(entry_widget.get())
    		return value < min_val or value > max_val
    	except ValueError:
    		return True
    
    def check_structure_for_contours(self, selected_roi_name):
        # Selected ROI in structure set and has contours
        name = str(selected_roi_name)
        if name in self.structure_names:
            if self.ct_scan_dropdown.get() in self.get_ct_exam_names():
                if self.patient_model.StructureSets[self.ct_scan_dropdown.get()].RoiGeometries[name].HasContours():
                    return True
        else:
            return False
    
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

    
    def submit(self, treatment_type):
        plan_name = self.plan_name_input.get().strip()
        selected_beams = [self.beam_listbox.get(i) for i in self.beam_listbox.curselection()]
        errors = []
        
        if plan_name in list(self.plan_beamsets.keys()):
            errors.append("The entered Plan Name is already in use. Please choose a different name.")
            
        if len(plan_name) < 1 or len(plan_name) > 16:
            errors.append("Enter a plan name of up to 16 characters.")
            
        if self.ct_scan_dropdown.get() not in self.get_ct_exam_names():
            errors.append("Select a CT examination.")

        if self.patient_position_dropdown.get() not in self.patient_positions:
            errors.append("Select a supported patient position.")
        
        # Check patient position and CT patient position are both supine
        if self.patient_position_dropdown.get() in self.patient_positions[:2]:
            try:
                print(self.ct_patient_positions[:2])
                if self.case.Examinations[self.ct_scan_dropdown.get()].PatientPosition not in self.ct_patient_positions[:2]:
                    errors.append("Select a prone position that matches the CT scan.")
            except:
                print("CT scan selection failed.")
        # Check patient position and CT patient position are both prone
        if self.patient_position_dropdown.get() in self.patient_positions[2:]:
            try:
                if self.case.Examinations[self.ct_scan_dropdown.get()].PatientPosition not in self.ct_patient_positions[2:]:
                    errors.append("Select a supine position that matches the CT scan.")
            except:
                print("CT scan selection failed.")
        
        if self.machine_dropdown.get() not in self.machines_names:
            errors.append("Select a treatment machine")
            
        if self.error_float_input(self.percentage_spinbox, min_val=0, max_val=50):
            errors.append("The percentage of 15 MV dose must be 0 - 50 %")
        
        if self.error_float_input(self.prescription_input, min_val=100, max_val=8000):
            errors.append("Check your prescription dose.")
            
        if not self.check_structure_for_contours(self.prescription_roi_dropdown.get()):
            errors.append("Select an Prescription ROI structure with contours on your selected CT.")
        
        if self.error_float_input(self.prescription_dose_volume_input, min_val=0, max_val=100):
            errors.append("Check your prescription dose at volume.")
            
        if self.error_float_input(self.fractionation_input, min_val=1, max_val=50):
            errors.append("Check your fractionation.")
        
        if self.plan_dropdown.get() not in self.plan_beamsets.keys():
            errors.append("Select a supported Physician Open Field Plan")
        
        if self.plan_dropdown.get() in self.plan_beamsets.keys():
            if self.beamset_dropdown.get() not in self.plan_beamsets[self.plan_dropdown.get()]:
                errors.append("Select a supported Physician Open Field Beamset")
        
        if len(selected_beams) > 2 or len(selected_beams) < 1 :
            errors.append("Select 1-2 beams from the physician open field beamset.")
        
        physician_machine = self.get_physician_beamset_machine()
        selected_machine = self.machine_dropdown.get()
        if physician_machine != selected_machine:
            errors.append("Selected machine must match the physician open field beamset machine.")
            
        if not self.check_structure_for_contours(self.sib_target_dropdown.get()) and treatment_type == self.tangents_and_sib_treatment_type:
            errors.append("Select an SIB structure with contours on your selected CT.")
        
        if errors:
            self.show_custom_error(errors)
            
            # # Re-apply selection after error
            # self.beam_listbox.selection_clear(0, tk.END)
            # for i in range(self.beam_listbox.size()):
            #     if self.beam_listbox.get(i) in selected_beams:
            #         self.beam_listbox.selection_set(i)
            return
        
        self.values = {
            "PlanName": plan_name,
            "ExaminationName": self.ct_scan_dropdown.get(),
            "PatientPosition": self.patient_position_dropdown.get(),
            "MachineName": self.machine_dropdown.get(),
            "Percentage15MV": float(self.percentage_spinbox.get()),
            "PrescriptionDose": self.prescription_input.get(),
            "PrescriptionRoiName": self.prescription_roi_dropdown.get(),
            "PrescriptionDoseAtVolumePercentage": float(self.prescription_dose_volume_input.get()),
            "NumberOfFractions": self.fractionation_input.get(),
            "PlanToCopy": self.plan_dropdown.get(),
            "BeamSetToCopy": self.beamset_dropdown.get(),
            "BeamsToCopy": selected_beams,
            "TargetSIB": self.sib_target_dropdown.get(),
            "PlanType": treatment_type
        }
        self.destroy()
    
    def get_values(self):
        return self.values
 
# # # Example usage
# if __name__ == "__main__":
#     window = SelectionWindow()
#     window.mainloop()
#     selected_values = window.get_values()
#     print(selected_values)
