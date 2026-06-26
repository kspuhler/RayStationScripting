'''Run the Breast_Tangents_SIB Protocol first.  
This script will populate the Tangents and SIB fields.
Set the initial MU of the open fields in Tangents.
Mixed Energies of up to 50% from the 15MV is allowed.
Tangents and SIB plans are automatically optimized.

@author: clanco01

'''

from connect import *
import tkinter as tk
from tkinter import MULTIPLE, SINGLE
from tkinter import messagebox
import sys
import os


# Correct the script directory (use the folder, not the file)
script_dir = r"\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingDEVEL\GenericScripts"
sys.path.append(script_dir)


# Import classes
from MLCMarginProcessor import MLCMarginProcessor
from DoseCalculator import DoseCalculator
from MessageBox import MessageBox
from ROIValidator import ROIValidator
from PercentageInputPopup import PercentageInputPopup
from DropdownMenuWindow import DropdownMenuWindow
from BreastPlanOptimizer import BreastPlanOptimizer
from PlanBeamsetChecker import PlanBeamsetChecker
from SIBBeamsetPrompt import SIBBeamsetPrompt


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
roi_validator = ROIValidator(patient_model, required_rois)
roi_validator.check_rois()

# Await user interaction - run breast protocol
await_user_input(message='Run a Breast Protocol to create a plan template.  Wait for it to complete.  Then, hit the play button.')

# Await user interaction - Set the Rx
await_user_input(message='The current prescription is 4050 cGy.  Change that if needed, and then hit the play button.')

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
dropdown_window = DropdownMenuWindow(root, plan_names, allow_multiple=False, label=breast_label)
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
    msg_box = MessageBox(message_top="Make sure Tangents and SIB beamsets exists in your plan.\n\nRun Breast protocol first.")
    msg_box.show_and_exit()


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
mlc_processor = MLCMarginProcessor(beam_set_sib)
beam_set_sib = mlc_processor.apply_margins()

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
dose_calc_tangents = DoseCalculator(beam_set_tangents)
beam_set_tangents = dose_calc_tangents.compute_dose()

# Save beam MU for 6 MV open fields
mu_6mv = [beam_set_tangents.Beams[0].BeamMU, beam_set_tangents.Beams[1].BeamMU]

# Create 15 MV oen fields
if percentage_15mv > 0:
# Set beams to 15 MV and calc dose
    beam_set_tangents.Beams[0].BeamQualityId = "15"
    beam_set_tangents.Beams[1].BeamQualityId = "15" 
    # Calc dose
    dose_calc_tangents = DoseCalculator(beam_set_tangents)
    beam_set_tangents = dose_calc_tangents.compute_dose()
	
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

# Await user interaction - load breast tangents objectives
await_user_input(message='Load or Add the Tangents beamset optimization objectives.  Then, hit the play button.')

# Optimize Tangents
BreastPlanOptimizer(plan, db)

# Ask user if they want an SIB beamset
sib_prompt = SIBBeamsetPrompt()
sib_selected = sib_prompt.ask_user_sib()

# Now you can use `sib_selected` in further logic
if sib_selected:

    # Set beam optimization settings for SIB beams
    plan.PlanOptimizations[1].OptimizationParameters.TreatmentSetupSettings[0].BeamSettings[0].EditBeamOptimizationSettings(OptimizationTypes=["SegmentOpt", "SegmentMU"], SelectCollimatorAngle=False, AllowBeamSplit=False)
    plan.PlanOptimizations[1].OptimizationParameters.TreatmentSetupSettings[0].BeamSettings[1].EditBeamOptimizationSettings(OptimizationTypes=["SegmentOpt", "SegmentMU"], SelectCollimatorAngle=False, AllowBeamSplit=False)
    
    # Await user interaction - load SIB objectives
    await_user_input(message='Load or Add the SIB beamset optimization objectives.  Add more beams to the SIB beamset if you want.  Then, hit the play button.')
    
    # Optimize SIB
    num_segs = len(beam_set_sib.Beams)
    BreastPlanOptimizer(plan, db, optimization_index=1, max_num_segments=num_segs)

# Delete SIB beamset
else:
    beam_set_sib.DeleteBeamSet()

# Exit message for user
top = "To improve your plan:\n"

body = """
1. Change the Objectives/Constraints of the Tangents and SIB beamsets.

2. Add a beam to the SIB beamset.  Make sure to increase the Max number of segments in Optimization and segmentation.

3. Adjust the MU of the open fields.

4. Re-run the protocol AND script with 15 MV or increase 15 MV percentage dose constribution.

5. Adjust the optimization and segmentation settings


IMPORTANT: Verify the open field jaws match the physician's open field jaws.

"""

end = "Once you get a good plan, merge the modulated fields and copy the SIB fields into a single beamset.\n\n Happy Planning!"

msg_box_end = MessageBox(message_top=top, message_body=body, message_end=end, title="Final Thoughts", width=500, height=450)
msg_box_end.show_and_exit()


