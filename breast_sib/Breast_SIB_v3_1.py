'''This script will populate the Tangents and/or SIB fields.
Set the initial MU of the open fields in Tangents.
Mixed Energies of up to 50% from the 15MV is allowed.
Tangents and SIB plans are automatically optimized.

@author: clanco01  03/26/2025

version 3.1

'''

from connect import *
import tkinter as tk
from tkinter import MULTIPLE, SINGLE
from tkinter import messagebox
import sys
import os


# Set current progress bar
set_progress('User setting plan parameters', percentage = -1)

# Correct the script directory (use the folder, not the file)
script_dir = r"\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD\Breast_SIB"
sys.path.append(script_dir)



# Import classes
from MLCMarginProcessor import MLCMarginProcessor
from DoseCalculator import DoseCalculator
from BreastPlanOptimizer import BreastPlanOptimizer
from SelectionWindow import SelectionWindow
from MessageBox import MessageBox
from CopyBeamWithoutAperture import CopyBeamWithoutAperture
from SelectUIPlanOpt import SelectUIPlanOpt
from SelectUIPlanEvalClinicalGoals import SelectUIPlanEvalClinicalGoals
from SetBeamsetDrrSettings import SetBeamsetDrrSettings
from RenameSetupFields import RenameSetupFields
from SetMaxMLCAndJawPositions import SetMaxMLCAndJawPositions
from SelectPlanDesign import SelectPlanDesign


# Set Tangents beamset to the same treatment technique as the selected Sim plan  
def match_treatment_technique(beam_set_moving, beam_set_fixed):
    if beam_set_fixed.PlanGenerationTechnique == 'Conformal':
    	beam_set_moving.SetTreatmentTechnique(Technique="Conformal")
    elif beam_set_fixed.PlanGenerationTechnique == 'Imrt':
    	beam_set_moving.SetTreatmentTechnique(Technique="SMLC")
    else:
    	print("Only PlanGenerationTechnique of Conformal or Imrt is supported.  Check if the beams you are copying came from a plan or beamset that is not Conformal or Imrt.")
    	exit()
    return beam_set_moving

# Save and set the scripting tab visable to the user
def save_and_set_ui_scripting_tab():
    patient = get_current("Patient")
    patient.Save()
    ui = get_current('ui')
    ui.ToolPanel.TabItem['Scripting'].Select()
    
# Set beam set dose grid voxel size
def update_dose_grid(beam_set, selected_values, sbrt_dose=400):
    '''selected_values is a dictionary of values saved from the user ''' 
    dose_per_fraction = int(selected_values["PrescriptionDose"]) / int(selected_values["NumberOfFractions"])
    if dose_per_fraction < sbrt_dose:
        beam_set.SetDefaultDoseGrid(VoxelSize={ 'x': 0.25, 'y': 0.25, 'z': 0.25 })
    else:
        beam_set.SetDefaultDoseGrid(VoxelSize={ 'x': 0.12, 'y': 0.12, 'z': 0.12 })
    # Update dose grid structures
    beam_set.FractionDose.UpdateDoseGridStructures()

# Return true if a minimum objective function exists.  Otherwise False
def check_for_min_objective_function(po):
    """po: PlanOptimizations[i] ofin the list of PlanOptimizations in each TreatmentPlan"""
        
    valid_min_functions = ["MinDose", "MinDvh", "UniformDose", "MinEud", "UniformEud", "Tcp"]
    
    if po.Objective:
        print(po.Objective)
        for cf in po.Objective.ConstituentFunctions:
            try:
                if cf.DoseFunctionParameters.FunctionType in valid_min_functions:
                    return True
            except:
                print("No FunctionType for the evaluated objective constituent function.")
    return False

# Get case, database, and patient model for running the script
case = get_current("Case")
db = get_current("PatientDB")

# Set constant for percentage of dose from open fields
open_field_dose = 0.7

# Get user selections for plan setup
window = SelectionWindow()
window.mainloop()
selected_values = window.get_values()

# Set current progress bar
set_progress('Creating plan and tangents beamset', percentage = -1)

# Set beamset that contains the physician open beams
beam_set_open = case.TreatmentPlans[selected_values["PlanToCopy"]].BeamSets[selected_values["BeamSetToCopy"]]

# Create plan 
plan = case.AddNewPlan(PlanName=selected_values["PlanName"], PlannedBy="", Comment="", ExaminationName=selected_values["ExaminationName"], 
                       IsMedicalOncologyPlan=False, AllowDuplicateNames=False)

# Create Tangents beamset
beam_set_tangents = plan.AddNewBeamSet(Name=selected_values["PlanName"], ExaminationName=selected_values["ExaminationName"], MachineName=selected_values["MachineName"], 
                                       Modality="Photons", TreatmentTechnique="SMLC", PatientPosition=selected_values["PatientPosition"], 
                                       NumberOfFractions=selected_values["NumberOfFractions"], CreateSetupBeams=True, 
                                       UseLocalizationPointAsSetupIsocenter=False, UseUserSelectedIsocenterSetupIsocenter=False, Comment="", RbeModelName=None, 
                                       EnableDynamicTrackingForVero=False, NewDoseSpecificationPointNames=[], NewDoseSpecificationPoints=[], 
                                       MotionSynchronizationTechniqueSettings={ 'DisplayName': None, 'MotionSynchronizationSettings': None, 
                                                                               'RespiratoryIntervalTime': None, 'RespiratoryPhaseGatingDutyCycleTimePercentage': None, 
                                                                               'MotionSynchronizationTechniqueType': "Undefined" }, 
					                   Custom=None, ToleranceTableLabel="3D PLAN")

# Turn off jaw setback for tangents beam set
beam_set_tangents.SetJawSetback(JawSetback=False)

# Set Tangents prescription
beam_set_tangents.AddRoiPrescriptionDoseReference(
    RoiName=selected_values["PrescriptionRoiName"],
    DoseVolume=selected_values["PrescriptionDoseAtVolumePercentage"],  # Relative volume [%] that should receive at least the prescribed dose
    PrescriptionType="DoseAtVolume",
    DoseValue=selected_values["PrescriptionDose"],  # Prescribed dose in cGy
)

# Set tangents beam set dose grid voxel size
update_dose_grid(beam_set_tangents, selected_values)

# Set Tangents beamset to the same treatment technique as the selected Sim plan  
beam_set_tangents = match_treatment_technique(beam_set_tangents, beam_set_open)

# Copy and rename fields from physician open field beamset to Tangents beam set
for i in range(len(selected_values["BeamsToCopy"])):
    CopyBeamWithoutAperture(beam_set_tangents, beam_set_open, str(selected_values["BeamsToCopy"][i]), new_beam_name=str(i+1))

# Add opposed beam if needed 
if len(selected_values["BeamsToCopy"]) == 1:
	beam_set_tangents.AddOpposedBeam(BeamName="1")
	beam_set_tangents.Beams[1].Name = "2"

# Save and set the scripting tab visable to the user
save_and_set_ui_scripting_tab()

# Set view in UI
SelectPlanDesign(plan.Name, beam_set_tangents.DicomPlanLabel)

# Set current progress bar
set_progress('User verifiying fields copied correctly.  Hit Script execution play button when done.', percentage = -1)

# Await user interaction - verify fields copied correctly
await_user_input(message='Verify the selected open fields copied to your plan have the correct Jaws and conformed MLCs.  Then, hit the Script execution play button.')

# Set current progress bar
set_progress('Creating plan and tangents beamset', percentage = -1)

# Save and set the scripting tab visable to the user
save_and_set_ui_scripting_tab()

# Set view in UI
SelectPlanDesign(plan.Name, beam_set_tangents.DicomPlanLabel)
	
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
if selected_values["Percentage15MV"] > 0:
# Set beams to 15 MV and calc dose
    beam_set_tangents.Beams[0].BeamQualityId = "15"
    beam_set_tangents.Beams[1].BeamQualityId = "15" 
    
    # Calc dose
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
    beam_set_tangents.Beams['1_15MV'].BeamMU = selected_values["Percentage15MV"] * mu_15mv[0] / 100
    beam_set_tangents.Beams['2_15MV'].BeamMU = selected_values["Percentage15MV"] * mu_15mv[1] / 100

	# Set MU for 6 MV open fields
    beam_set_tangents.Beams['1'].BeamMU = (open_field_dose * 100 - selected_values["Percentage15MV"]) * mu_6mv[0] / 100
    beam_set_tangents.Beams['2'].BeamMU = (open_field_dose * 100 - selected_values["Percentage15MV"]) * mu_6mv[1] / 100

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

# Limit jaw motion for the modulated tangent fields 
machine_name = beam_set_tangents.MachineReference.MachineName
jaw_motion = []
if machine_name == "TrueBeamSN1106":
    jaw_motion = "UseLimitsAsMax"
elif machine_name == "21EX":
    jaw_motion = "LockToLimits"
else:
    jaw_motion = "Automatic"
plan.PlanOptimizations[0].OptimizationParameters.TreatmentSetupSettings[0].BeamSettings[mod_beam_num[0]].EditBeamOptimizationSettings(OptimizationTypes=["SegmentOpt", "SegmentMU"], SelectCollimatorAngle=False, AllowBeamSplit=False, JawMotion=jaw_motion, LeftJaw=jaws_1[0], RightJaw=jaws_1[1], TopJaw=jaws_1[2], BottomJaw=jaws_1[3])
plan.PlanOptimizations[0].OptimizationParameters.TreatmentSetupSettings[0].BeamSettings[mod_beam_num[1]].EditBeamOptimizationSettings(OptimizationTypes=["SegmentOpt", "SegmentMU"], SelectCollimatorAngle=False, AllowBeamSplit=False, JawMotion=jaw_motion, LeftJaw=jaws_2[0], RightJaw=jaws_2[1], TopJaw=jaws_2[2], BottomJaw=jaws_2[3])

# Set current progress bar
set_progress('Saving....', percentage = -1)

# Save and set the scripting tab visable to the user
save_and_set_ui_scripting_tab()

# Open Clinical Goals tab in Plan Optimization
SelectUIPlanOpt(plan.Name, beam_set_tangents.DicomPlanLabel, tab_item_dvh="Clinical goals")

# Set current progress bar
set_progress('User updating clinical goals', percentage = -1)

# Await user interaction - load SIB objectives
await_user_input(message='Load your clinical goals.  Then, hit Script execution play button when done.')

# Set current progress bar
set_progress('Loading default optimization objectives', percentage = -1)

# Load the optimization function template
try:
    template_name = "Breast_Tangents_Opt"  # Ensure this template name is correct
    opt_template = db.LoadTemplateOptimizationFunctions(templateName=template_name, lockMode="Read")
    plan.PlanOptimizations[0].ApplyOptimizationTemplate(Template=opt_template)
except:
    print("Default optimization template did not load correctly.")

# Set current progress bar
set_progress('Saving...', percentage = -1)

# Save and set the scripting tab visable to the user
save_and_set_ui_scripting_tab()

# Set current progress bar
set_progress('User updating tangents beamset Objectives/constraints.  Hit Script execution play button when done.', percentage = -1)

# Open tangent's Objectives/constraints tab
SelectUIPlanOpt(plan.Name, beam_set_tangents.DicomPlanLabel)

# Await user interaction - load breast tangents objectives
await_user_input(message=f'Review and/or change your tangents beamset Objectives/constraints.  Then, hit the Script execution play button.')

# Verify there is a minimum objective before proceeding
while not check_for_min_objective_function(plan.PlanOptimizations[0]):
    # Await user interaction - add at least one minimum objective function
    print(f"Min objective exist: {check_for_min_objective_function(plan.PlanOptimizations[0])}")
    await_user_input(message="Add at least one minimum objective function before optimization.")

# Set current progress bar
set_progress('Optimizing tangents beamset', percentage = -1)

# Optimize Tangents
BreastPlanOptimizer(plan, db)

# Set current progress bar
set_progress("Setting max MLC and Jaw positions in tangents beamset based upon the physician's open fields...", percentage = -1)

# Save beam MU for each beam
beam_mu = {}
for beam in beam_set_tangents.Beams:
    beam_mu[beam.Name] = beam.BeamMU

# Set modulated fields jaws and MLC to be no larger than the open fields
try:
    SetMaxMLCAndJawPositions(beam_set_tangents.Beams['1 Mod'], beam_set_tangents.Beams['1'])
    SetMaxMLCAndJawPositions(beam_set_tangents.Beams['2 Mod'], beam_set_tangents.Beams['2'])
    
    # Set current progress bar
    set_progress('Calculating dose...', percentage = -1)
    
    # Calc tangents dose
    dose_calc_tangents_with_mu = DoseCalculator(beam_set_tangents, beam_mu=beam_mu)
    beam_set_tangents = dose_calc_tangents_with_mu.compute_dose()
except:
    print("Setting MLC and Jaw positions to no larger than the open field failed upon dose calculation.  Reversrting back to original optimized segments.")


# Create SIB beamset if selected
if selected_values["PlanType"] == "Tangents + SIB":
    # Set current progress bar
    set_progress('Creating SIB beamset', percentage = -1)
    
    beam_set_sib = plan.AddNewBeamSet(Name="SIB", ExaminationName=selected_values["ExaminationName"], MachineName=selected_values["MachineName"], 
                                           Modality="Photons", TreatmentTechnique="SMLC", PatientPosition=selected_values["PatientPosition"], 
                                           NumberOfFractions=selected_values["NumberOfFractions"], CreateSetupBeams=True, 
                                           UseLocalizationPointAsSetupIsocenter=False, UseUserSelectedIsocenterSetupIsocenter=False, Comment="", RbeModelName=None, 
                                           EnableDynamicTrackingForVero=False, NewDoseSpecificationPointNames=[], NewDoseSpecificationPoints=[], 
                                           MotionSynchronizationTechniqueSettings={ 'DisplayName': None, 
                                                                    'MotionSynchronizationSettings': None, 
                                                                    'RespiratoryIntervalTime': None, 
                                                                    'RespiratoryPhaseGatingDutyCycleTimePercentage': None, 
                                                                    'MotionSynchronizationTechniqueType': "Undefined" }, 
    					                   Custom=None, ToleranceTableLabel="3D PLAN")

    # Set SIB beamsets to the same treatment technique as the selected Sim plan  
    beam_set_sib = match_treatment_technique(beam_set_sib, beam_set_tangents)
	
    # Copy and rename fields from Sim plan to SIB beam set
    beam_set_sib.CopyBeamsFromBeamSet(BeamSetToCopyFrom=beam_set_tangents, BeamsToCopy=["1", "2"])
    beam_set_sib.Beams['1'].Name = "1 SIB"
    beam_set_sib.Beams['2'].Name = "2 SIB"
    
    # Set SIB beamset MLC margins
    mlc_processor = MLCMarginProcessor(beam_set_sib, case.PatientModel.RegionsOfInterest, roi_name=selected_values["TargetSIB"])
    beam_set_sib = mlc_processor.apply_margins()
    
    # Update dependency: SIB depends on Tangents
    plan.UpdateDependency(
        DependentBeamSetName=beam_set_sib.DicomPlanLabel,
        BackgroundBeamSetName=beam_set_tangents.DicomPlanLabel,
        DependencyUpdate="CreateDependency"
    )
    
    # Turn off jaw setback for SIB beam set
    beam_set_sib.SetJawSetback(JawSetback=False)
    
    # Set current progress bar
    set_progress('Loading default optimization objectives', percentage = -1)

    # Set beam optimization settings for SIB beams
    plan.PlanOptimizations[1].OptimizationParameters.TreatmentSetupSettings[0].BeamSettings[0].EditBeamOptimizationSettings(OptimizationTypes=["SegmentOpt", "SegmentMU"],              
                                                                                                                            SelectCollimatorAngle=False, AllowBeamSplit=False)
    plan.PlanOptimizations[1].OptimizationParameters.TreatmentSetupSettings[0].BeamSettings[1].EditBeamOptimizationSettings(OptimizationTypes=["SegmentOpt", "SegmentMU"], 
                                                                                                                            SelectCollimatorAngle=False, AllowBeamSplit=False)
    
    # Load the optimization function template
    try: 
        template_name = "Breast_SIB_Opt"  # Ensure this template name is correct
        opt_template = db.LoadTemplateOptimizationFunctions(templateName=template_name, lockMode="Read")
        plan.PlanOptimizations[1].ApplyOptimizationTemplate(Template=opt_template)
    except:
        print("Default optimization template did not load correctly.")
    
    # Set current progress bar
    set_progress('Saving...', percentage = -1)

    # Save and set the scripting tab visable to the user
    save_and_set_ui_scripting_tab()

    # Open SIB Objectives/constraints tab with Plan Dose selected
    SelectUIPlanOpt(plan.Name, beam_set_sib.DicomPlanLabel)
    ui = get_current('ui')
    ui.Workspace.TabControl['DVH'].Dvh.DvhLegend[0].CheckBox.Click()
    
    # Set SIB beam set dose grid voxel size
    update_dose_grid(beam_set_sib, selected_values)
    
    # Set current progress bar
    set_progress('User updating SIB beamset Objectives/constraints.  Hit Script execution play button when done.', percentage = -1)    

    # Await user interaction - load SIB objectives
    await_user_input(message=f'Review and/or change your SIB beamset Objectives/constraints.  Add/change the beams in the SIB beamset if you want.  Then, hit the Script execution play button.')
    
    # Verify there is a minimum objective before proceeding
    while not check_for_min_objective_function(plan.PlanOptimizations[1]):
        # Await user interaction - add at least one minimum objective function
        print(f"Min objective exist: {check_for_min_objective_function(plan.PlanOptimizations[1])}")
        await_user_input(message="Add at least one minimum objective function before optimization.")

    
    # Set current progress bar
    set_progress('Optimizing SIB', percentage = -1)
    
    # Optimize SIB
    num_segs = len(beam_set_sib.Beams)
    BreastPlanOptimizer(plan, db, optimization_index=1, max_num_segments=num_segs)


# Set current progress bar
set_progress('Setting DRRs to Breast', percentage = -1)
for beam_set in plan.BeamSets:
    SetBeamsetDrrSettings(beam_set, drr_type='Breast')
    
# Rename setup fields for all beamsets
set_progress('Renaming setup fields', percentage = -1)
for beam_set in plan.BeamSets:
    RenameSetupFields(beam_set)

# Set current progress bar
set_progress('Saving and finished!', percentage = -1)

# Save and set UI window to plan evaluation clinical goals
patient = get_current("Patient")
patient.Save()
SelectUIPlanEvalClinicalGoals(plan.Name)

# Set current progress bar
set_progress('Final thoughts', percentage = -1)

# Exit message for user
top = "To finalize your plan:\n"

body = """
1. Change the Objectives/constraints of the Tangents and SIB beamsets.

2. Add a beam to the SIB beamset.  Make sure to increase the Max number of segments in Optimization and segmentation.

3. Adjust the MU of the open fields.

4. Re-run the script with 15 MV or increase 15 MV percentage dose constribution.

5. Adjust the optimization and segmentation settings.


"""

end = "Once you get a good plan, merge the modulated fields and copy the SIB fields into a single beamset.\n\n Happy Planning!"

msg_box_end = MessageBox(message_top=top, message_body=body, message_end=end, title="Final Thoughts", width=500, height=450)
msg_box_end.show_and_exit()

