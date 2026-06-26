'''This script will populate the Tangents and/or SIB fields.
Set the initial MU of the open fields in Tangents.
Mixed Energies of up to 50% from the 15MV is allowed.
Tangents and SIB plans are automatically optimized.

@author: clanco01  02/12/2025

version 1.0

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
from BreastPlanOptimizer import BreastPlanOptimizer
from SelectionWindow import SelectionWindow
from MessageBox import MessageBox


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

# Send the user a message to check for aperture shapes
await_user_input(message="Physician open fields must not contain aperture shapes.  If needed, create a copy of the plan, go to Plan design → 3D-CRT beam design, conform the beams, and remove the aperture shape.  Then, press Play to continue.")
# Get case, database, and patient model for running the script
case = get_current("Case")
db = get_current("PatientDB")

# Set constant for percentage of dose from open fields
open_field_dose = 0.7

# Get user selections for plan setup
window = SelectionWindow()
window.mainloop()
selected_values = window.get_values()

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

# Set Tangents prescription
beam_set_tangents.AddRoiPrescriptionDoseReference(
    RoiName=selected_values["PrescriptionRoiName"],
    DoseVolume=selected_values["PrescriptionDoseAtVolumePercentage"],  # Relative volume [%] that should receive at least the prescribed dose
    PrescriptionType="DoseAtVolume",
    DoseValue=selected_values["PrescriptionDose"],  # Prescribed dose in cGy
)

# Set Tangents beamset to the same treatment technique as the selected Sim plan  
beam_set_tangents = match_treatment_technique(beam_set_tangents, beam_set_open)

# Copy and rename fields from physician open field beamset to Tangents beam set
if len(selected_values["BeamsToCopy"]) == 1:
	beam_set_tangents.CopyBeamsFromBeamSet(BeamSetToCopyFrom=case.TreatmentPlans[selected_values["PlanToCopy"]].BeamSets[selected_values["BeamSetToCopy"]], 
                                        BeamsToCopy=[selected_values["BeamsToCopy"][0]])
	beam_set_tangents.Beams[selected_values["BeamsToCopy"][0]].Name = "1"
	beam_set_tangents.AddOpposedBeam(BeamName="1")
	beam_set_tangents.Beams[1].Name = "2"
else:
	beam_set_tangents.CopyBeamsFromBeamSet(BeamSetToCopyFrom=case.TreatmentPlans[selected_values["PlanToCopy"]].BeamSets[selected_values["BeamSetToCopy"]], 
                                        BeamsToCopy=[selected_values["BeamsToCopy"][0], selected_values["BeamsToCopy"][1]])
	beam_set_tangents.Beams[selected_values["BeamsToCopy"][0]].Name = "1"
	beam_set_tangents.Beams[selected_values["BeamsToCopy"][1]].Name = "2"

# Conform open segments MLCs for Tangents Beamset to the open beam segments
beam_set_tangents.SetTreatmentTechnique(Technique="Conformal")
beam_set_tangents.SetJawSetback(JawSetback=False)
[beam_set_tangents.ClearROIFromTreatOrProtectUsageForAllBeams(RoiName=roi.Name) for roi in case.PatientModel.RegionsOfInterest]
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
if selected_values["Percentage15MV"] > 0:
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

# Load the optimization function template
template_name = "Breast_Tangents_Opt"  # Ensure this template name is correct
opt_template = db.LoadTemplateOptimizationFunctions(templateName=template_name, lockMode="Read")
plan.PlanOptimizations[0].ApplyOptimizationTemplate(Template=opt_template)

# Await user interaction - load breast tangents objectives
await_user_input(message=f'Default optimization objectives added to your plan named {plan.Name} and beamset named {beam_set_tangents.DicomPlanLabel}.  Change, if needed.  Then, hit the play button.')

# Optimize Tangents
BreastPlanOptimizer(plan, db)


# Create SIB beamset if selected
if selected_values["PlanType"] == "Tangents + SIB":
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

    # Set beam optimization settings for SIB beams
    plan.PlanOptimizations[1].OptimizationParameters.TreatmentSetupSettings[0].BeamSettings[0].EditBeamOptimizationSettings(OptimizationTypes=["SegmentOpt", "SegmentMU"], SelectCollimatorAngle=False, AllowBeamSplit=False)
    plan.PlanOptimizations[1].OptimizationParameters.TreatmentSetupSettings[0].BeamSettings[1].EditBeamOptimizationSettings(OptimizationTypes=["SegmentOpt", "SegmentMU"], SelectCollimatorAngle=False, AllowBeamSplit=False)
    
    # Load the optimization function template
    template_name = "Breast_SIB_Opt"  # Ensure this template name is correct
    opt_template = db.LoadTemplateOptimizationFunctions(templateName=template_name, lockMode="Read")
    plan.PlanOptimizations[1].ApplyOptimizationTemplate(Template=opt_template)
    
    # Await user interaction - load SIB objectives
    await_user_input(message=f'Default optimization objectives added to your plan named {plan.Name} and beamset named {beam_set_sib.DicomPlanLabel}.  Change, if needed.  Add more beams to the SIB beamset if you want.  Then, hit the play button.')
    
    # Optimize SIB
    num_segs = len(beam_set_sib.Beams)
    BreastPlanOptimizer(plan, db, optimization_index=1, max_num_segments=num_segs)


# Await user interaction - load SIB objectives
await_user_input(message='Load your clinical goals.  Then, hit the play button.')


# Exit message for user
top = "To finalize your plan:\n"

body = """
1. Change the Objectives/Constraints of the Tangents and SIB beamsets.

2. Add a beam to the SIB beamset.  Make sure to increase the Max number of segments in Optimization and segmentation.

3. Adjust the MU of the open fields.

4. Re-run the script with 15 MV or increase 15 MV percentage dose constribution.

5. Adjust the optimization and segmentation settings.


IMPORTANT: Verify the open field jaws match the physician's open field jaws.

"""

end = "Once you get a good plan, merge the modulated fields and copy the SIB fields into a single beamset.\n\n Happy Planning!"

msg_box_end = MessageBox(message_top=top, message_body=body, message_end=end, title="Final Thoughts", width=500, height=450)
msg_box_end.show_and_exit()


