'''Run the Breast_Tangents_SIB Protocol first.  
This script will populate the Tangents and SIB fields.
Set the initial MU of the open fields in Tangents.
Mixed Energies of up to 50% from the 15MV is allowed.
Tangents and SIB plans are automatically optimized.

Created on Weds Feb 5 12:31 2024

@author: clanco01

'''

from connect import *
import tkinter as tk
from tkinter import MULTIPLE, SINGLE
from tkinter import messagebox


class PercentageInputPopup(tk.Toplevel):
    def __init__(self, parent, title='Set Percentage', label="Enter a percentage (0-50):"):
        super().__init__(parent)
        self.title(title)
        self.geometry("300x150")  # Set window size

        # Label
        self.label = tk.Label(self, text=label)
        self.label.pack(pady=10)

        # Entry Field for percentage
        self.entry = tk.Entry(self)
        self.entry.pack(pady=5)

        # Buttons
        self.ok_button = tk.Button(self, text="Mixed Energy Plan", command=self.validate_input)
        self.ok_button.pack(side=tk.LEFT, padx=20, pady=10)

        self.cancel_button = tk.Button(self, text="6 MV Only Plan", command=self.cancel)
        self.cancel_button.pack(side=tk.RIGHT, padx=20, pady=10)

        self.user_choice = None  # Store user's input

    def validate_input(self):
        """Validate if the input is a number between 0 and 50"""
        try:
            value = float(self.entry.get())  # Convert input to float
            if 0 <= value <= 50:
                self.user_choice = value
                self.destroy()  # Close window
            else:
                messagebox.showerror("Invalid Input", "Please enter a number between 0 and 50.")
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number.")

    def cancel(self):
        """Handle user canceling the input"""
        self.user_choice = 0
        self.destroy()

    def get_percentage(self):
        """Wait for user input and return the value"""
        self.wait_window()  # Wait for input
        return self.user_choice  # Return saved value
	

class DropdownMenuWindow(tk.Toplevel):
    def __init__(self, parent, items, allow_multiple=False, title = "Select the Treatment Plan with physician created open fields", label = "Select Items:"):
        super().__init__(parent)
        self.title = title
        self.parent = parent
        self.geometry("550x500")
        
        self.selection_mode = MULTIPLE if allow_multiple else SINGLE
        
        self.label = tk.Label(self, text=label, wraplength=500)
        self.label.pack(pady=10)
        
        self.listbox = tk.Listbox(self, selectmode=self.selection_mode, height=10)
        self.listbox.pack(padx=20, pady=10)
        
        # Insert items passed to the constructor
        for item in items:
            self.listbox.insert(tk.END, item)
        
        self.ok_button = tk.Button(self, text="OK", command=self.on_ok_button)
        self.ok_button.pack(pady=10)
        
        # Initialize variable to store selected items
        self.selected_items = None
        
    def on_ok_button(self):
        selected_indices = self.listbox.curselection()
        self.selected_items = [self.listbox.get(idx) for idx in selected_indices]
        
        if self.selection_mode == SINGLE:
            self.selected_items = self.selected_items[0] if self.selected_items else None
        
        self.destroy()  # Close the window after selection

        # Destroy the main root window after the dropdown window closes
        self.parent.destroy()
        
    def get_selected_items(self):
        return self.selected_items

def process_mlc_margins(beam_set, margin_value=0.7, roi_name="PTV_TB_Eval"):
	# Turn off jaw setback
	beam_set.SetJawSetback(JawSetback=False)
	
	# Select the ROI to be used for margins
	beam_set.SelectToUseROIasTreatOrProtectForAllBeams(RoiName=roi_name)
	
	# Apply margins to all treat and protect ROIs
	for beam in beam_set.Beams:
		beam.SetTreatAndProtectMarginsForBeam(
		    TopMargin=margin_value,
		    BottomMargin=margin_value,
		    LeftMargin=margin_value,
		    RightMargin=margin_value,
		    Roi=roi_name  # Apply to all selected Treat and Protect ROIs
		)
	
	# Conform all  MLCs
	return beam_set.TreatAndProtect(ShowProgress=True)

# Ability to calc dose for a 3D-CRT or SMLC copied field
def calc_dose_try_except(beam_set):
	try:
		beam_set.SetMUAndComputeDose(ForceRecompute=False)
	except:
		for beam in beam_set.Beams:
			beam.BeamMU = 1
		beam_set.ComputeDose(ComputeBeamDoses=True, DoseAlgorithm="CCDose", ForceRecompute=False, RunEntryValidation=True)

# Message and exit method	
def message_and_exit(message_top="", message_body="", message_end="", title="Error", width=500, height=300):
    # Initialize Tkinter
    root = tk.Tk()
    root.withdraw()  # Hide main Tkinter window

    # Create a custom Toplevel message box
    message_window = tk.Toplevel()
    message_window.title(title)
    message_window.geometry(f"{width}x{height}")  # Set window size

    # Centered Title Label
    title_label = tk.Label(message_window, text=message_top, wraplength=width-40, font=("Arial", 12, "bold"), justify="center")
    title_label.pack(pady=(10, 5))  # Extra padding to separate title from body

    # Left-Aligned Body Label
    body_label = tk.Label(message_window, text=message_body, wraplength=width-40, justify="left", anchor="w")
    body_label.pack(padx=20, pady=(0, 10), anchor="w")  # Anchor 'w' (west) aligns left

    # Centered End Message Label
    end_label = tk.Label(message_window, text=message_end, wraplength=width-40, font=("Arial", 10, "italic"), justify="center")
    end_label.pack(pady=(10, 5))  # Spacing before the OK button

    # OK Button to close the message box
    ok_button = tk.Button(message_window, text="OK", command=message_window.destroy)
    ok_button.pack(pady=10)

    # Wait for the user to close the window
    message_window.wait_window()

    # Destroy Tkinter instance
    root.destroy()

    # Exit script
    exit()


def check_required_rois(patient_model, required_rois):
    found_rois = {roi: False for roi in required_rois}

    # Iterate through all ROIs and check their types
    for roi in patient_model.RegionsOfInterest:
        if roi.Name in required_rois and roi.Type == required_rois[roi.Name]:
            found_rois[roi.Name] = True  # Mark as found if type matches

    # Check for missing or incorrect ROIs
    missing_rois = [roi for roi, found in found_rois.items() if not found]

    # If issues exist, show an error message and exit
    if missing_rois:
        root = tk.Tk()
        root.withdraw()  # Hide the main Tkinter window

        error_message = (
            "The following required ROIs are missing or have incorrect types:\n\n"
            + "\n".join(missing_rois) +
            "\n\nPlease correct this in RayStation before running the script again."
        )

        messagebox.showerror("ROI Error", error_message)
        root.destroy()
        exit()  # Stop script execution

    print("All required ROIs exist with correct types.")


# Get case, database, and patient model for running the script
case = get_current("Case")
db = get_current("PatientDB")
patient_model = get_current("Case").PatientModel

# Set constant for perentage of dose from open fields
open_field_dose = 0.7

# Check required ROIs and type
required_rois = {
    "PTV_TB_Eval": "Ptv"
}
check_required_rois(case.PatientModel, required_rois)



# User selects plan plan for breast script
plan_names = [plan.Name for plan in case.TreatmentPlans if hasattr(plan, "Name")]
root = tk.Tk()
root.withdraw()  # Hide the root window
breast_label = ("""Tangents (4050 cGy) and Beam Dependent SIB (4800 cGy) Beamsets:

The open fields created by the physician are copied into the Tangents and SIB beamsets.
The Tangents beamset is optimized with ~70% of the Rx dose from the open fields and up to 8 
modulated segments.  The SIB beamset uses the same two beam directions as the Tangents 
beamset and uses beam dependent optimization.  Breast_Tangents_Opt and Breast_SIB_Opt are
the Objectives/constraints templates used.  15 MV open fields can be used for up to 50%
of the estimated Tangents dose.  Prerequisites are:

1. Breast_Tangents_SIB_XXXXX protocol has been run.
2. PTV Tangents and PTV_TB_Eval are ROIs of type Ptv.
3. External is an ROI, and External's type is set to External.
4. No aperture shapes in the open fields.

Select the Breast Treatment Plan created from the protocol:""")
dropdown_window = DropdownMenuWindow(root, plan_names, allow_multiple=False, label=breast_label)#, title=plan_title)
dropdown_window.grab_set()  # Make sure the dropdown window grabs focus
root.wait_window(dropdown_window)  # Wait for the dropdown window to close
plan_name = dropdown_window.get_selected_items()


# Check if correct beamset names exist and assign beam_set in script
plan = case.TreatmentPlans[plan_name]
beam_set_names = [beam_set.DicomPlanLabel for beam_set in plan.BeamSets]
if 'Tangents' in beam_set_names and 'SIB' in beam_set_names:
	beam_set_tangents = plan.BeamSets['Tangents']
	beam_set_sib = plan.BeamSets['SIB']
else:
	message_and_exit(message_top="Make sure Tangents and SIB beamsets exists in your plan.\n\nRun Breast protocol first.")

# Get the plan that contains the open fields
root = tk.Tk()
root.withdraw()  # Hide the root window
plan_label = "Select the Treatment Plan with physician-created open fields:"
dropdown_window = DropdownMenuWindow(root, plan_names, allow_multiple=False, label=plan_label)#, title=plan_title)
dropdown_window.grab_set()  # Make sure the dropdown window grabs focus
root.wait_window(dropdown_window)  # Wait for the dropdown window to close
sim_plan = dropdown_window.get_selected_items()
open_field_plan = case.TreatmentPlans[sim_plan]


# Get available fields (beams) from the selected plan
field_names = [beam.Name for beam in open_field_plan.BeamSets[0].Beams]
root = tk.Tk()
root.withdraw()  # Hide the root window
field_label = "Select the medial and lateral open fields.  If only one is available, an opposed field will be created."
dropdown_window = DropdownMenuWindow(root, field_names, allow_multiple=True, label=field_label)#, title=plan_title)
dropdown_window.grab_set()  # Make sure the dropdown window grabs focus
root.wait_window(dropdown_window)  # Wait for the dropdown window to close
selected_fields = dropdown_window.get_selected_items()


# Percentage of 15 MV popup
root = tk.Tk()
root.withdraw()  # Hide the root window
title = "Set Percentage"
label = "Percentage of Dose from 15 MV open fields (0 - 50):"
popup = PercentageInputPopup(root, title=title, label=label)
percentage_15mv = popup.get_percentage()
root.destroy()  # Clean up Tkinter

# Set Tangents and SIB beamsets to the same treatment technique as the selected Sim plan  
if case.TreatmentPlans[sim_plan].BeamSets[0].PlanGenerationTechnique == 'Conformal':
	beam_set_tangents.SetTreatmentTechnique(Technique="Conformal")
	beam_set_sib.SetTreatmentTechnique(Technique="Conformal")
elif case.TreatmentPlans[sim_plan].BeamSets[0].PlanGenerationTechnique == 'Imrt':
	beam_set_tangents.SetTreatmentTechnique(Technique="SMLC")
	beam_set_sib.SetTreatmentTechnique(Technique="SMLC")
else:
	print(f"PlanGenerationTechnique of {case.TreatmentPlans[sim_plan].BeamSets[0].PlanGenerationTechnique} is not supported.")
	exit()

# Copy and rename fields from Sim plan to Tangents beam set
if len(selected_fields) == 1:
	beam_set_tangents.CopyBeamsFromBeamSet(BeamSetToCopyFrom=case.TreatmentPlans[sim_plan].BeamSets[0], BeamsToCopy=[selected_fields[0]])
	beam_set_tangents.Beams[selected_fields[0]].Name = "1"
	beam_set_tangents.AddOpposedBeam(BeamName="1")
	beam_set_tangents.Beams[1].Name = "2"
else:
	beam_set_tangents.CopyBeamsFromBeamSet(BeamSetToCopyFrom=case.TreatmentPlans[sim_plan].BeamSets[0], BeamsToCopy=[selected_fields[0], selected_fields[1]])
	beam_set_tangents.Beams[selected_fields[0]].Name = "1"
	beam_set_tangents.Beams[selected_fields[1]].Name = "2"
	
# Copy and rename fields from Sim plan to SIB beam set
beam_set_sib.CopyBeamsFromBeamSet(BeamSetToCopyFrom=plan.BeamSets['Tangents'], BeamsToCopy=["1", "2"])
beam_set_sib.Beams['1'].Name = "1 SIB"
beam_set_sib.Beams['2'].Name = "2 SIB"

# Set SIB beamset MLC margins
beam_set_sib.SetTreatmentTechnique(Technique="Conformal")
beam_set_sib = process_mlc_margins(beam_set_sib)
beam_set_sib.SetTreatmentTechnique(Technique="SMLC")

# Conform open segments MLCs for Tangents Beamset
beam_set_tangents.SetJawSetback(JawSetback=False)
if not beam_set_tangents.Beams[0].Segments:
	beam_set_tangents.Beams[0].ConformMlc()
if not beam_set_tangents.Beams[1].Segments:
	beam_set_tangents.Beams[1].ConformMlc()
	
# Set Tangents beamset to SMLC
beam_set_tangents.SetTreatmentTechnique(Technique="SMLC")

# Turn on auto scale in tangent plan
beam_set_tangents.SetAutoScaleToPrimaryPrescription(AutoScale=True)

# Calculate dose to 6 MV open fields in tangent plan
calc_dose_try_except(beam_set_tangents)

# Save beam MU for 6 MV open fields
mu_6mv = [beam_set_tangents.Beams[0].BeamMU, beam_set_tangents.Beams[1].BeamMU]

# Create 15 MV oen fields
if percentage_15mv > 0:

	# Set beams to 15 MV and calc dose
	beam_set_tangents.Beams[0].BeamQualityId = "15"
	beam_set_tangents.Beams[1].BeamQualityId = "15"
	calc_dose_try_except(beam_set_tangents)
	
	#Save beam MU for 15 MV open fields
	mu_15mv = [beam_set_tangents.Beams[0].BeamMU, beam_set_tangents.Beams[1].BeamMU]
	
	# Set beams to 6 MV
	beam_set_tangents.Beams[0].BeamQualityId = "6"
	beam_set_tangents.Beams[1].BeamQualityId = "6"
	
	# Copy 6 MV beams to 15 MV and rename
	beam_set_tangents.CopyBeam(BeamName="1")
	beam_set_tangents.Beams['3'].Name = "1_15MV"
	beam_set_tangents.Beams['1_15MV'].BeamQualityId = "15"
	beam_set_tangents.CopyBeam(BeamName="2")
	beam_set_tangents.Beams['3'].Name = "2_15MV"
	beam_set_tangents.Beams['2_15MV'].BeamQualityId = "15"
	
	# Turn off auto scale in tangent plan
	beam_set_tangents.SetAutoScaleToPrimaryPrescription(AutoScale=False)
	
	# Set MU of 15 MV open fields
	beam_set_tangents.Beams['1_15MV'].BeamMU = percentage_15mv * mu_15mv[0] / 100
	beam_set_tangents.Beams['2_15MV'].BeamMU = percentage_15mv * mu_15mv[1] / 100

	# Set MU for 6 MV open fields
	beam_set_tangents.Beams['1'].BeamMU = (open_field_dose * 100 - percentage_15mv) * mu_6mv[0] / 100
	beam_set_tangents.Beams['2'].BeamMU = (open_field_dose * 100 - percentage_15mv) * mu_6mv[1] / 100

else:

	# Turn off auto scale in tangent plan
	beam_set_tangents.SetAutoScaleToPrimaryPrescription(AutoScale=False)
	
	# Set MU for 6 MV open fields
	beam_set_tangents.Beams['1'].BeamMU = open_field_dose * mu_6mv[0] 
	beam_set_tangents.Beams['2'].BeamMU = open_field_dose * mu_6mv[1] 

# Copy open fields to create modulated fields
beam_set_tangents.CopyBeam(BeamName="1")
beam_set_tangents.Beams['3'].Name = "1 Mod"
beam_set_tangents.CopyBeam(BeamName="2")
beam_set_tangents.Beams['3'].Name = "2 Mod"

# Update dependency: SIB depends on Tangents
plan.UpdateDependency(
    DependentBeamSetName=beam_set_sib.DicomPlanLabel,
    BackgroundBeamSetName=beam_set_tangents.DicomPlanLabel,
    DependencyUpdate="CreateDependency"
)

# Set beam optimization settings for Tangents 6 MV open beams
plan.PlanOptimizations[0].OptimizationParameters.TreatmentSetupSettings[0].BeamSettings[0].EditBeamOptimizationSettings(OptimizationTypes=["None"], SelectCollimatorAngle=False, AllowBeamSplit=False, JawMotion="Automatic", LeftJaw=-5, RightJaw=5, TopJaw=-5, BottomJaw=5)
plan.PlanOptimizations[0].OptimizationParameters.TreatmentSetupSettings[0].BeamSettings[1].EditBeamOptimizationSettings(OptimizationTypes=["None"], SelectCollimatorAngle=False, AllowBeamSplit=False, JawMotion="Automatic", LeftJaw=-5, RightJaw=5, TopJaw=-5, BottomJaw=5)

# Get jaws from open fields
jaws_1 = beam_set_tangents.Beams['1'].Segments[0].JawPositions
jaws_2 = beam_set_tangents.Beams['2'].Segments[0].JawPositions

# For mixed energy plans
if len(beam_set_tangents.Beams) == 6:

	# Set beam optimization settigns for 15 MV open beams
	plan.PlanOptimizations[0].OptimizationParameters.TreatmentSetupSettings[0].BeamSettings[2].EditBeamOptimizationSettings(OptimizationTypes=["None"], SelectCollimatorAngle=False, AllowBeamSplit=False, JawMotion="Automatic", LeftJaw=-5, RightJaw=5, TopJaw=-5, BottomJaw=5)
	plan.PlanOptimizations[0].OptimizationParameters.TreatmentSetupSettings[0].BeamSettings[3].EditBeamOptimizationSettings(OptimizationTypes=["None"], SelectCollimatorAngle=False, AllowBeamSplit=False, JawMotion="Automatic", LeftJaw=-5, RightJaw=5, TopJaw=-5, BottomJaw=5)

	# Set field number for modulated field
	mod_beam_num = [4, 5]

# For 6 MV only plans
else: 
	# Set field number for modulated field
	mod_beam_num = [2, 3]

# Lock jaws to limits for the modulated tangent fields 
plan.PlanOptimizations[0].OptimizationParameters.TreatmentSetupSettings[0].BeamSettings[mod_beam_num[0]].EditBeamOptimizationSettings(OptimizationTypes=["SegmentOpt", "SegmentMU"], SelectCollimatorAngle=False, AllowBeamSplit=False, JawMotion="LockToLimits", LeftJaw=jaws_1[0], RightJaw=jaws_1[1], TopJaw=jaws_1[2], BottomJaw=jaws_1[3])
plan.PlanOptimizations[0].OptimizationParameters.TreatmentSetupSettings[0].BeamSettings[mod_beam_num[1]].EditBeamOptimizationSettings(OptimizationTypes=["SegmentOpt", "SegmentMU"], SelectCollimatorAngle=False, AllowBeamSplit=False, JawMotion="LockToLimits", LeftJaw=jaws_2[0], RightJaw=jaws_2[1], TopJaw=jaws_2[2], BottomJaw=jaws_2[3])

# Set beam optimization settings for SIB beams
plan.PlanOptimizations[1].OptimizationParameters.TreatmentSetupSettings[0].BeamSettings[0].EditBeamOptimizationSettings(OptimizationTypes=["SegmentOpt", "SegmentMU"], SelectCollimatorAngle=False, AllowBeamSplit=False)
plan.PlanOptimizations[1].OptimizationParameters.TreatmentSetupSettings[0].BeamSettings[1].EditBeamOptimizationSettings(OptimizationTypes=["SegmentOpt", "SegmentMU"], SelectCollimatorAngle=False, AllowBeamSplit=False)

# Reset optimization for Tangents and SIB beam set
plan.PlanOptimizations[0].ResetOptimization()
plan.PlanOptimizations[1].ResetOptimization()

# Optimization and Segmentation settings for Tangents
plan.PlanOptimizations[0].OptimizationParameters.Algorithm.MaxNumberOfIterations = 40
plan.PlanOptimizations[0].OptimizationParameters.Algorithm.OptimalityTolerance = 0
plan.PlanOptimizations[0].OptimizationParameters.DoseCalculation.ComputeFinalDose = True
plan.PlanOptimizations[0].OptimizationParameters.DoseCalculation.IterationsInPreparationsPhase = 20
plan.PlanOptimizations[0].OptimizationParameters.TreatmentSetupSettings[0].SegmentConversion.MaxNumberOfSegments = 8
plan.PlanOptimizations[0].OptimizationParameters.TreatmentSetupSettings[0].SegmentConversion.MinNumberOfOpenLeafPairs = 4
plan.PlanOptimizations[0].OptimizationParameters.TreatmentSetupSettings[0].SegmentConversion.MinSegmentArea = 5
plan.PlanOptimizations[0].OptimizationParameters.TreatmentSetupSettings[0].SegmentConversion.MinSegmentMUPerFraction = 5
plan.PlanOptimizations[0].OptimizationParameters.TreatmentSetupSettings[0].SegmentConversion.MinLeafEndSeparation = 2

# Run two iterations of optimization for Tangents
plan.PlanOptimizations[0].RunOptimization(ScalingOfSoftMachineConstraints=None)
plan.PlanOptimizations[0].RunOptimization(ScalingOfSoftMachineConstraints=None)

# Optimization and Segmentation settings for SIB
plan.PlanOptimizations[1].OptimizationParameters.Algorithm.MaxNumberOfIterations = 40
plan.PlanOptimizations[1].OptimizationParameters.Algorithm.OptimalityTolerance = 0
plan.PlanOptimizations[1].OptimizationParameters.DoseCalculation.ComputeFinalDose = True
plan.PlanOptimizations[1].OptimizationParameters.DoseCalculation.IterationsInPreparationsPhase = 20
plan.PlanOptimizations[1].OptimizationParameters.TreatmentSetupSettings[0].SegmentConversion.MaxNumberOfSegments = 2
plan.PlanOptimizations[1].OptimizationParameters.TreatmentSetupSettings[0].SegmentConversion.MinNumberOfOpenLeafPairs = 4
plan.PlanOptimizations[1].OptimizationParameters.TreatmentSetupSettings[0].SegmentConversion.MinSegmentArea = 5
plan.PlanOptimizations[1].OptimizationParameters.TreatmentSetupSettings[0].SegmentConversion.MinSegmentMUPerFraction = 5
plan.PlanOptimizations[1].OptimizationParameters.TreatmentSetupSettings[0].SegmentConversion.MinLeafEndSeparation = 2

# Load the optimization function template for SIB
template_name = "Breast_SIB_Opt"  
opt_template = db.LoadTemplateOptimizationFunctions(templateName=template_name, lockMode="Read")
plan.PlanOptimizations[1].ApplyOptimizationTemplate(Template=opt_template)

# Run optimization for SIB
plan.PlanOptimizations[1].RunOptimization(ScalingOfSoftMachineConstraints=None)
plan.PlanOptimizations[1].RunOptimization(ScalingOfSoftMachineConstraints=None)



# Exit message for user
top = "To improve your plan:\n"

body = """
1. Change the Objectives/Constraints of the Tangents and SIB beamsets.

2. Add a beam to the SIB beamset.  Make sure to increase the Max number of segments in Optimization and segmentation.

3. Adjust the MU of the open fields.

4. Re-run the protocol AND script with 15 MV or increase 15 MV percentage dose constribution.

5. Adjust the optimization and segmentstion settings


IMPORTANT: Verify the open field jaws match the physician's open field jaws.

"""

end = "Once you get a good plan, merge the modulated fields and copy the SIB fields into a single beamset.\n\n Happy Planning!"


message_and_exit(message_top=top, message_body=body, message_end=end, title="Final Thoughts", width=500, height=450)


