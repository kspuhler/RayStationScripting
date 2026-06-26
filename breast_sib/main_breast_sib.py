'''This script will populate the Tangents and/or SIB fields.
Set the initial MU of the open fields in Tangents.
Mixed Energies of up to 50% from the 15MV is allowed.
Tangents and SIB plans are automatically optimized.

@author: clanco01  11/10/2025

version 5.0

'''
from __future__ import annotations

# === DEBUG SETTINGS ===
_DEBUG_THIS_MODULE = False
_ALERT_PHYSICIST_ON_ALL_USES = False

# === Raystation import ===
try:
    from connect import get_current, set_progress, await_user_input
except Exception:
    pass

# === WORKING DIRECTORY ===
import sys
sys.path.append(r"\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
sys.path.append(r"F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")

# === Main library imports ===
from typing import Optional
import tkinter as tk
from tkinter import messagebox
import sys
import time

# === Local imports ===
from RSutil.LogUtil.rs_logging import LOGGERS, set_logger_mode
from RSutil.ErrorsUtil.error_dispatcher import DispatcherConfig
from RSutil.ErrorsUtil.rs_errors import report_error
from RSutil.ErrorsUtil.error_codes import PROMPT_USER, ALERT_PHYSICIST, ABORT_SCRIPT
from RSutil.patient_data_util import PatientDataUtil
from breast_sib.MLCMarginProcessor import MLCMarginProcessor
from breast_sib.DoseCalculator import DoseCalculator
from breast_sib.BreastPlanOptimizer import BreastPlanOptimizer
from breast_sib.SelectionWindow import SelectionWindow
from breast_sib.MessageBox import MessageBox
from breast_sib.CopyBeamWithoutAperture import CopyBeamWithoutAperture
from breast_sib.SelectUIPlanOpt import SelectUIPlanOpt
from breast_sib.SelectUIPlanEvalClinicalGoals import SelectUIPlanEvalClinicalGoals
from breast_sib.SetBeamsetDrrSettings import SetBeamsetDrrSettings
from breast_sib.RenameSetupFields import RenameSetupFields
from breast_sib.SetMaxMLCAndJawPositions import SetMaxMLCAndJawPositions
from breast_sib.SelectPlanDesign import SelectPlanDesign

# === Setup Logger ===
_logger = LOGGERS["breast_sib"]
if _DEBUG_THIS_MODULE:
    set_logger_mode(_logger, "debug")

def _alert_physicist_error(
        exc: Exception, 
        metadata: Optional[dict] = None, 
        message: Optional[str] = None
):  
    if not _DEBUG_THIS_MODULE:                                            
        cfg = DispatcherConfig()
        cfg.alert_recipients = ["owen.clancey@nyulangone.org"]
        report_error(
                error_def=ALERT_PHYSICIST.SYSF_UNHANDLED_EXCEPTION, 
                original_exception=exc, 
                context={"module": "main_breast_sib.py"},
                metadata=metadata,
                message=message,
                dispatcher_config=cfg,
            )

if _ALERT_PHYSICIST_ON_ALL_USES:
    e = RuntimeError("INFO ONLY - Breast_SIB script initialized.  Review patient data in logs.")
    _alert_physicist_error(e, message=__name__)

class BreastSIB:
    
    def __init__(self):
        
        # Get data from patient in Raystation
        self.case = get_current("Case")
        self.db = get_current("PatientDB")
        self.patient = get_current("Patient")
        
        # Initialize empty plans and beam sets
        self. beam_set_open= None
        self.beam_set_tangents = None
        self.beam_set_sib = None
        self.plan = None
        
        # DIctionary for beam set names
        self.beam_set_names = {
            "Tangents": "Tangents",
            "SIB": "SIB"}
        
        # Dictionary for beam names
        '''Changing these names will have an impact on copying beams.  Use caution'''
        self.beam_names = {
            "tangent_1_6MV": "1",
            "tangent_1_6MV_mod": "1 Mod",
            "tangent_2_6MV": "2",
            "tangent_2_6MV_mod": "2 Mod",
            "tangent_1_15MV": "1_15MV",
            "tangent_2_15MV": "2_15MV",
            "sib_1": "1 SIB",
            "sib_2": "2 SIB"
        }
        
        # Create list of valid minimum objective functions 
        self.valid_min_functions = ["MinDose", "MinDvh", "UniformDose", "MinEud", "UniformEud", "Tcp"]
        
        # Set constant for percentage of dose from open fields
        self.open_field_dose = 0.7
        
        # Optimization index in Plan Optimization list
        self.tangents_opt_number = 0
        self.sib_opt_number = 1
        
        # Optimization objective template names
        self.tangents_opt_template_name = "Breast_Tangents_Opt"
        self.sib_opt_template_name = "Breast_SIB_Opt"
        


    # === Error handling ===
    def _prompt_user_acknowledge(
            self, 
            exc: Exception, 
            metadata: Optional[dict] = None, 
            message: Optional[str] = None
    ):                                                  
        report_error(
                error_def=PROMPT_USER.UIUX_USER_ACKNOWLEDGE, 
                original_exception=exc, 
                context={"module": "main_eqd2.py"},
                metadata={},
                message=message,
            )
    
    def _abort_script_error(
            self, 
            exc: Exception, 
            metadata: Optional[dict] = None, 
            message: Optional[str] = None
    ):
        _logger.debug("Inside _abort_script_error()")                                            
        report_error(
                error_def=ABORT_SCRIPT.DATA_REQUIRED_MISSING, 
                original_exception=exc, 
                context={"module": "main_eqd2.py"},
                metadata={},
                message=message,
            )
        raise RuntimeError(str(exc))

    # Save and set the scripting tab visable to the user
    def save_and_set_ui_scripting_tab(self):
        self.patient.Save()
        ui = get_current('ui')
        ui.ToolPanel.TabItem['Scripting'].Select()

    # Return true if a minimum objective function exists.  Otherwise False
    def check_for_min_objective_function(self, po):
        """po: PlanOptimizations[i] in the list of PlanOptimizations in each TreatmentPlan"""
        if po.Objective:
            print(po.Objective)
            for cf in po.Objective.ConstituentFunctions:
                try:
                    if cf.DoseFunctionParameters.FunctionType in self.valid_min_functions:
                        return True
                except:
                    print("No FunctionType for the evaluated objective constituent function.")
        return False

    # Set beam set dose grid voxel size
    def update_dose_grid(self, beam_set, sbrt_dose=400):
        '''self.selected_values is a dictionary of values saved from the user ''' 
        dose_per_fraction = int(self.selected_values["PrescriptionDose"]) / int(self.selected_values["NumberOfFractions"])
        if dose_per_fraction < sbrt_dose:
            beam_set.SetDefaultDoseGrid(VoxelSize={ 'x': 0.25, 'y': 0.25, 'z': 0.25 })
        else:
            beam_set.SetDefaultDoseGrid(VoxelSize={ 'x': 0.12, 'y': 0.12, 'z': 0.12 })
        # Update dose grid structures
        beam_set.FractionDose.UpdateDoseGridStructures()

    def create_plan(self):
        self.plan = self.case.AddNewPlan(PlanName=self.selected_values["PlanName"], PlannedBy="", Comment="", ExaminationName=self.selected_values["ExaminationName"], 
                               IsMedicalOncologyPlan=False, AllowDuplicateNames=False)
    
    def create_tangents_beam_set(self):
        # Create Tangents beamset
        self.beam_set_tangents = self.plan.AddNewBeamSet(Name=self.selected_values["PlanName"], ExaminationName=self.selected_values["ExaminationName"], MachineName=self.selected_values["MachineName"], 
                                               Modality="Photons", TreatmentTechnique="SMLC", PatientPosition=self.selected_values["PatientPosition"], 
                                               NumberOfFractions=self.selected_values["NumberOfFractions"], CreateSetupBeams=True, 
                                               UseLocalizationPointAsSetupIsocenter=False, UseUserSelectedIsocenterSetupIsocenter=False, Comment="", RbeModelName=None, 
                                               EnableDynamicTrackingForVero=False, NewDoseSpecificationPointNames=[], NewDoseSpecificationPoints=[], 
                                               MotionSynchronizationTechniqueSettings={ 'DisplayName': None, 'MotionSynchronizationSettings': None, 
                                                                                       'RespiratoryIntervalTime': None, 'RespiratoryPhaseGatingDutyCycleTimePercentage': None, 
                                                                                       'MotionSynchronizationTechniqueType': "Undefined" }, 
        					                   Custom=None, ToleranceTableLabel="3D PLAN")
    
        # Turn off jaw setback for tangents beam set
        self.beam_set_tangents.SetJawSetback(JawSetback=False)
    
        # Set Tangents prescription
        self.beam_set_tangents.AddRoiPrescriptionDoseReference(
            RoiName=self.selected_values["PrescriptionRoiName"],
            DoseVolume=self.selected_values["PrescriptionDoseAtVolumePercentage"],  # Relative volume [%] that should receive at least the prescribed dose
            PrescriptionType="DoseAtVolume",
            DoseValue=self.selected_values["PrescriptionDose"],  # Prescribed dose in cGy
        )
    
        # Set tangents beam set dose grid voxel size
        self.update_dose_grid(self.beam_set_tangents)
    
        # Set Tangents beamset to the same treatment technique as the selected Sim plan  
        self.beam_set_tangents = self.match_treatment_technique(self.beam_set_tangents, self.beam_set_open)
    
        # Copy and rename fields from physician open field beamset to Tangents beam set
        for i in range(len(self.selected_values["BeamsToCopy"])):
            beam_key = f"tangent_{i+1}_6MV"
            CopyBeamWithoutAperture(self.beam_set_tangents, self.beam_set_open, str(self.selected_values["BeamsToCopy"][i]), new_beam_name=self.beam_names[beam_key])
    
        # Add opposed beam if needed 
        if len(self.selected_values["BeamsToCopy"]) == 1:
        	self.beam_set_tangents.AddOpposedBeam(BeamName=self.beam_names["tangent_1_6MV"])
        	self.beam_set_tangents.Beams[1].Name = self.beam_names["tangent_2_6MV"]
    
    def create_tangent_beams_and_mu(self):
        
        # Set Tangents beamset to SMLC
        self.beam_set_tangents.SetTreatmentTechnique(Technique="SMLC")

        # Turn on auto scale in tangent plan
        self.beam_set_tangents.SetAutoScaleToPrimaryPrescription(AutoScale=True)

        # Calculate dose to 6 MV open fields in tangent plan
        dose_calc_tangents = DoseCalculator(self.beam_set_tangents)
        self.beam_set_tangents = dose_calc_tangents.compute_dose()

        # Save beam MU for 6 MV open fields
        mu_6mv = [self.beam_set_tangents.Beams[0].BeamMU, self.beam_set_tangents.Beams[1].BeamMU]

        # Create 15 MV oen fields
        if self.selected_values["Percentage15MV"] > 0:
        # Set beams to 15 MV and calc dose
            self.beam_set_tangents.Beams[0].BeamQualityId = "15"
            self.beam_set_tangents.Beams[1].BeamQualityId = "15" 
            
            # Calc dose
            self.beam_set_tangents = dose_calc_tangents.compute_dose()
        	
        	#Save beam MU for 15 MV open fields
            mu_15mv = [self.beam_set_tangents.Beams[0].BeamMU, self.beam_set_tangents.Beams[1].BeamMU]
        	
        	# Set beams to 6 MV
            self.beam_set_tangents.Beams[0].BeamQualityId = "6"
            self.beam_set_tangents.Beams[1].BeamQualityId = "6"
        	
        	# Copy 6 MV beams to 15 MV and rename
            self.beam_set_tangents.CopyBeam(BeamName=self.beam_names["tangent_1_6MV"])
            self.beam_set_tangents.Beams['3'].Name = self.beam_names["tangent_1_15MV"]
            self.beam_set_tangents.Beams[self.beam_names["tangent_1_15MV"]].BeamQualityId = "15"
            self.beam_set_tangents.CopyBeam(BeamName=self.beam_names["tangent_2_6MV"])
            self.beam_set_tangents.Beams['3'].Name = self.beam_names["tangent_2_15MV"]
            self.beam_set_tangents.Beams[self.beam_names["tangent_2_15MV"]].BeamQualityId = "15"
        	
        	# Turn off auto scale in tangent plan
            self.beam_set_tangents.SetAutoScaleToPrimaryPrescription(AutoScale=False)
        	
        	# Set MU of 15 MV open fields
            self.beam_set_tangents.Beams[self.beam_names["tangent_1_15MV"]].BeamMU = self.selected_values["Percentage15MV"] * mu_15mv[0] / 100
            self.beam_set_tangents.Beams[self.beam_names["tangent_2_15MV"]].BeamMU = self.selected_values["Percentage15MV"] * mu_15mv[1] / 100

        	# Set MU for 6 MV open fields
            self.beam_set_tangents.Beams[self.beam_names["tangent_1_6MV"]].BeamMU = (self.open_field_dose * 100 - self.selected_values["Percentage15MV"]) * mu_6mv[0] / 100
            self.beam_set_tangents.Beams[self.beam_names["tangent_2_6MV"]].BeamMU = (self.open_field_dose * 100 - self.selected_values["Percentage15MV"]) * mu_6mv[1] / 100

        else:

        	# Turn off auto scale in tangent plan
        	self.beam_set_tangents.SetAutoScaleToPrimaryPrescription(AutoScale=False)
        	
        	# Set MU for 6 MV open fields
        	self.beam_set_tangents.Beams[self.beam_names["tangent_1_6MV"]].BeamMU = self.open_field_dose * mu_6mv[0] 
        	self.beam_set_tangents.Beams[self.beam_names["tangent_2_6MV"]].BeamMU = self.open_field_dose * mu_6mv[1] 

        # Copy open fields to create modulated fields
        self.beam_set_tangents.CopyBeam(BeamName=self.beam_names["tangent_1_6MV"])
        self.beam_set_tangents.Beams['3'].Name = self.beam_names["tangent_1_6MV_mod"]
        self.beam_set_tangents.CopyBeam(BeamName=self.beam_names["tangent_2_6MV"])
        self.beam_set_tangents.Beams['3'].Name = self.beam_names["tangent_2_6MV_mod"]
        
    def set_tangents_optimization_settings(self):
        
        # Set beam optimization settings for Tangents 6 MV open beams
        self.plan.PlanOptimizations[self.tangents_opt_number].OptimizationParameters.TreatmentSetupSettings[0].BeamSettings[0].EditBeamOptimizationSettings(OptimizationTypes=["None"], SelectCollimatorAngle=False, AllowBeamSplit=False, JawMotion="Automatic", LeftJaw=-5, RightJaw=5, TopJaw=-5, BottomJaw=5)
        self.plan.PlanOptimizations[self.tangents_opt_number].OptimizationParameters.TreatmentSetupSettings[0].BeamSettings[1].EditBeamOptimizationSettings(OptimizationTypes=["None"], SelectCollimatorAngle=False, AllowBeamSplit=False, JawMotion="Automatic", LeftJaw=-5, RightJaw=5, TopJaw=-5, BottomJaw=5)

        # Get jaws from open fields
        jaws_1 = self.beam_set_tangents.Beams['1'].Segments[0].JawPositions
        jaws_2 = self.beam_set_tangents.Beams['2'].Segments[0].JawPositions

        # For mixed energy plans
        if len(self.beam_set_tangents.Beams) == 6:

            # Set beam optimization settigns for 15 MV open beams
            self.plan.PlanOptimizations[self.tangents_opt_number].OptimizationParameters.TreatmentSetupSettings[0].BeamSettings[2].EditBeamOptimizationSettings(OptimizationTypes=["None"], SelectCollimatorAngle=False, AllowBeamSplit=False, JawMotion="Automatic", LeftJaw=-5, RightJaw=5, TopJaw=-5, BottomJaw=5)
            self.plan.PlanOptimizations[self.tangents_opt_number].OptimizationParameters.TreatmentSetupSettings[0].BeamSettings[3].EditBeamOptimizationSettings(OptimizationTypes=["None"], SelectCollimatorAngle=False, AllowBeamSplit=False, JawMotion="Automatic", LeftJaw=-5, RightJaw=5, TopJaw=-5, BottomJaw=5)

            # Set field number for modulated field
            mod_beam_num = [4, 5]

        # For 6 MV only plans
        else: 
            # Set field number for modulated field
            mod_beam_num = [2, 3]

        # Limit jaw motion for the modulated tangent fields 
        machine_name = self.beam_set_tangents.MachineReference.MachineName
        jaw_motion = []
        if machine_name == "TrueBeamSN1106":
            jaw_motion = "UseLimitsAsMax"
        elif machine_name == "21EX":
            jaw_motion = "LockToLimits"
        else:
            jaw_motion = "Automatic"
        self.plan.PlanOptimizations[self.tangents_opt_number].OptimizationParameters.TreatmentSetupSettings[0].BeamSettings[mod_beam_num[0]].EditBeamOptimizationSettings(OptimizationTypes=["SegmentOpt", "SegmentMU"], SelectCollimatorAngle=False, AllowBeamSplit=False, JawMotion=jaw_motion, LeftJaw=jaws_1[0], RightJaw=jaws_1[1], TopJaw=jaws_1[2], BottomJaw=jaws_1[3])
        self.plan.PlanOptimizations[self.tangents_opt_number].OptimizationParameters.TreatmentSetupSettings[0].BeamSettings[mod_beam_num[1]].EditBeamOptimizationSettings(OptimizationTypes=["SegmentOpt", "SegmentMU"], SelectCollimatorAngle=False, AllowBeamSplit=False, JawMotion=jaw_motion, LeftJaw=jaws_2[0], RightJaw=jaws_2[1], TopJaw=jaws_2[2], BottomJaw=jaws_2[3])

    def load_optimization_template(self, opt_num, template_name):
        try:
            opt_template = self.db.LoadTemplateOptimizationFunctions(templateName=template_name, lockMode="Read")
            self.plan.PlanOptimizations[opt_num].ApplyOptimizationTemplate(Template=opt_template)
        except:
            print("Default optimization template did not load correctly.")

    def set_modulated_beam_max_mlc_jaw_position(self):
        # Save beam MU for each beam
        beam_mu = {}
        for beam in self.beam_set_tangents.Beams:
            beam_mu[beam.Name] = beam.BeamMU

        # Set modulated fields jaws and MLC to be no larger than the open fields
        try:
            SetMaxMLCAndJawPositions(self.beam_set_tangents.Beams[self.beam_names["tangent_1_6MV_mod"]], self.beam_set_tangents.Beams[self.beam_names["tangent_1_6MV"]])
            SetMaxMLCAndJawPositions(self.beam_set_tangents.Beams[self.beam_names["tangent_2_6MV_mod"]], self.beam_set_tangents.Beams[self.beam_names["tangent_2_6MV"]])
            
            # Set current progress bar
            set_progress('Calculating dose...', percentage = -1)
            
            # Calc tangents dose
            dose_calc_tangents_with_mu = DoseCalculator(self.beam_set_tangents, beam_mu=beam_mu)
            self.beam_set_tangents = dose_calc_tangents_with_mu.compute_dose()
        except:
            print("Setting MLC and Jaw positions failed.  Using segments directly from optimizer.")
            root = tk.Tk()
            root.withdraw()  # Hide the root window
            root.attributes('-topmost', True)
            messagebox.showerror("Error", "Setting MLC and Jaw positions od modulated fields to open field MLC and Jaw positions failed.  Using segments directly from optimizer.")
            root.destroy()  # Cleanly destroy the root window

    def create_sib_beam_set(self):
        self.beam_set_sib = self.plan.AddNewBeamSet(Name=self.beam_set_names["SIB"], ExaminationName=self.selected_values["ExaminationName"], 
                                               MachineName=self.selected_values["MachineName"], 
                                               Modality="Photons", TreatmentTechnique="SMLC", PatientPosition=self.selected_values["PatientPosition"], 
                                               NumberOfFractions=self.selected_values["NumberOfFractions"], CreateSetupBeams=True, 
                                               UseLocalizationPointAsSetupIsocenter=False, UseUserSelectedIsocenterSetupIsocenter=False, Comment="", RbeModelName=None, 
                                               EnableDynamicTrackingForVero=False, NewDoseSpecificationPointNames=[], NewDoseSpecificationPoints=[], 
                                               MotionSynchronizationTechniqueSettings={ 'DisplayName': None, 
                                                                        'MotionSynchronizationSettings': None, 
                                                                        'RespiratoryIntervalTime': None, 
                                                                        'RespiratoryPhaseGatingDutyCycleTimePercentage': None, 
                                                                        'MotionSynchronizationTechniqueType': "Undefined" }, 
        					                   Custom=None, ToleranceTableLabel="3D PLAN")

        # Set SIB beamsets to the same treatment technique as the selected Sim plan  
        self.beam_set_sib = self.match_treatment_technique(self.beam_set_sib, self.beam_set_tangents)
    	
        # Copy and rename fields from Sim plan to SIB beam set
        self.beam_set_sib.CopyBeamsFromBeamSet(BeamSetToCopyFrom=self.beam_set_tangents, BeamsToCopy=[self.beam_names["tangent_1_6MV"], self.beam_names["tangent_2_6MV"]])
        self.beam_set_sib.Beams['1'].Name = self.beam_names["sib_1"]
        self.beam_set_sib.Beams['2'].Name = self.beam_names["sib_2"]
        
        # Set SIB beamset MLC margins
        mlc_processor = MLCMarginProcessor(self.beam_set_sib, self.case.PatientModel.RegionsOfInterest, roi_name=self.selected_values["TargetSIB"])
        self.beam_set_sib = mlc_processor.apply_margins()
        
        # Update dependency: SIB depends on Tangents
        self.plan.UpdateDependency(
            DependentBeamSetName=self.beam_set_sib.DicomPlanLabel,
            BackgroundBeamSetName=self.beam_set_tangents.DicomPlanLabel,
            DependencyUpdate="CreateDependency"
        )
        
        # Turn off jaw setback for SIB beam set
        self.beam_set_sib.SetJawSetback(JawSetback=False)
        
    def set_sib_optimization_settings(self):
        # Set beam optimization settings for SIB beams
        self.plan.PlanOptimizations[self.sib_opt_number].OptimizationParameters.TreatmentSetupSettings[0].BeamSettings[0].EditBeamOptimizationSettings(OptimizationTypes=["SegmentOpt", "SegmentMU"], SelectCollimatorAngle=False, AllowBeamSplit=False)
        self.plan.PlanOptimizations[self.sib_opt_number].OptimizationParameters.TreatmentSetupSettings[0].BeamSettings[1].EditBeamOptimizationSettings(OptimizationTypes=["SegmentOpt", "SegmentMU"], SelectCollimatorAngle=False, AllowBeamSplit=False)

    # Set moving beam set to match the treatment technique of the fixed beam set
    def match_treatment_technique(self, beam_set_moving, beam_set_fixed):
        if beam_set_fixed.PlanGenerationTechnique == 'Conformal':
        	beam_set_moving.SetTreatmentTechnique(Technique="Conformal")
        elif beam_set_fixed.PlanGenerationTechnique == 'Imrt':
        	beam_set_moving.SetTreatmentTechnique(Technique="SMLC")
        else:
        	print("Only PlanGenerationTechnique of Conformal or Imrt is supported.  Check if the beams you are copying came from a plan or beamset that is not Conformal or Imrt.")
        	exit()
        return beam_set_moving

    def end_message(self):
        # Exit message for user
        top = "To finalize your plan:\n"

        body = """
        1. Change the Objectives/constraints of the Tangents and SIB beamsets.

        2. Add a beam to the SIB beamset.  Make sure to increase the Max number of segments in Optimization and segmentation.

        3. Adjust the MU of the open fields.

        4. Re-run the script with 15 MV or increase 15 MV percentage dose contribution.

        5. Adjust the optimization and segmentation settings.


        """

        end = "Once you get a good plan, merge the modulated fields and copy the SIB fields into a single beamset.\n\n Happy Planning!"

        msg_box_end = MessageBox(message_top=top, message_body=body, message_end=end, title="Final Thoughts", width=500, height=450)
        msg_box_end.show_message()

    def main(self):
        try:
            # Open input window to get user selected values for plan
            set_progress('User setting plan parameters...', percentage = -1)
            window = SelectionWindow()
            window.mainloop()
            self.selected_values = window.get_values()
            
            # Set beamset that contains the physician open beams
            self.beam_set_open = self.case.TreatmentPlans[self.selected_values["PlanToCopy"]].BeamSets[self.selected_values["BeamSetToCopy"]]
            
            # Create plan and tangents beam set
            set_progress('Creating plan and tangents beamset...', percentage = -1)
            self.create_plan()
            self.create_tangents_beam_set()
            
            
            # Save and set view for user - Plan design with tangents beam set
            set_progress('Saving....', percentage = -1)
            self.save_and_set_ui_scripting_tab()
            SelectPlanDesign(self.plan.Name, self.beam_set_tangents.DicomPlanLabel)
            
            # Await user interaction - verify fields copied correctly
            set_progress('User verifiying fields copied correctly.  Hit Script execution play button when done.', percentage = -1)
            await_user_input(message='Verify the selected open fields copied to your plan have the correct Jaws and conformed MLCs.  Then, hit the Script execution play button.')
            
            # Create tangent beams and mu
            set_progress('Creating tangent beams and open field MU values...', percentage = -1)
            self.create_tangent_beams_and_mu()
            
            # Set optimization settings
            set_progress('Updating optimization settings....', percentage = -1)
            self.set_tangents_optimization_settings()
            
            # Save and set view for user - Plan optimization with clinical goals tab
            set_progress('Saving....', percentage = -1)
            self.save_and_set_ui_scripting_tab()
            SelectUIPlanOpt(self.plan.Name, self.beam_set_tangents.DicomPlanLabel, tab_item_dvh="Clinical goals")
    
            # Await user interaction - load clinical goals
            set_progress('User updating clinical goals...', percentage = -1)
            await_user_input(message='Load your clinical goals.  Then, hit Script execution play button when done.')
            
            # Load the optimization function template
            set_progress('Loading default optimization objectives...', percentage = -1)
            self.load_optimization_template(self.tangents_opt_number, self.tangents_opt_template_name)
            
            # Save and set view for user - Plan optimization with objectives tab
            set_progress('Saving...', percentage = -1)
            self.save_and_set_ui_scripting_tab()
            SelectUIPlanOpt(self.plan.Name, self.beam_set_tangents.DicomPlanLabel)
    
            # Await user interaction - finalizing breast tangents objectives
            set_progress('User updating tangents beamset Objectives/constraints.  Hit Script execution play button when done.', percentage = -1)
            await_user_input(message='Review and/or change your tangents beamset Objectives/constraints.  Then, hit the Script execution play button.')
            
            # Verify there is a minimum objective before proceeding
            while not self.check_for_min_objective_function(self.plan.PlanOptimizations[self.tangents_opt_number]):
                await_user_input(message="Add at least one minimum objective function before optimization.")
    
            # Optimize Tangents
            set_progress('Optimizing tangents beamset...', percentage = -1)
            BreastPlanOptimizer(self.plan, self.db)
            
            # Await user interaction - finalizing breast tangents optimization
            set_progress('User finalizing tangents optimization.  Hit Script execution play button when done.', percentage = -1)
            await_user_input(message='Continue making adjustments and optimizing until satistfied.  Then, hit the Script execution play button to proceed.')
            
            # Set modulated beams in tangent beam set to no larger than the open field MLC and jaw positions
            set_progress("Setting max MLC and Jaw positions in tangents beamset based upon the physician's open fields...", percentage = -1)
            self.set_modulated_beam_max_mlc_jaw_position()
            
            # Create SIB beamset if selected
            if self.selected_values["PlanType"] == "Tangents + SIB":
                # Create SIB beam set
                set_progress('Creating SIB beamset...', percentage = -1)
                self.create_sib_beam_set()
                
                # Set optimization settings for the SIB beam set
                self.set_sib_optimization_settings()
                
                # Load default SIB optimzation objectives template
                set_progress('Loading default optimization objectives...', percentage = -1)
                self.load_optimization_template(self.sib_opt_number, self.sib_opt_template_name)
                
                # Save and open SIB Objectives/constraints tab with Plan Dose selected
                set_progress('Saving...', percentage = -1)
                self.save_and_set_ui_scripting_tab()
                SelectUIPlanOpt(self.plan.Name, self.beam_set_sib.DicomPlanLabel)
                ui = get_current('ui')
                ui.Workspace.TabControl['DVH'].Dvh.DvhLegend[0].CheckBox.Click()
                
                # Set SIB beam set dose grid voxel size
                self.update_dose_grid(self.beam_set_sib)
                
                # Await user interaction - finalizing SIB objectives
                set_progress('User updating SIB beamset Objectives/constraints.  Hit Script execution play button when done.', percentage = -1)    
                await_user_input(message='Review and/or change your SIB beamset Objectives/constraints.  Add/change the beams in the SIB beamset if you want.  Then, hit the Script execution play button.')
                
                # Verify there is a minimum objective before proceeding
                while not self.check_for_min_objective_function(self.plan.PlanOptimizations[self.sib_opt_number]):
                    await_user_input(message="Add at least one minimum objective function before optimization.")
                
                # Optimize SIB beam set
                set_progress('Optimizing SIB', percentage = -1)
                BreastPlanOptimizer(self.plan, self.db, optimization_index=self.sib_opt_number, max_num_segments=len(self.beam_set_sib.Beams))
                
                # Await user interaction - finalizing SIB optimization
                set_progress('User finalizing SIB optimization.  Hit Script execution play button when done.', percentage = -1)
                await_user_input(message='Continue making adjustments and optimizing until satistfied.  Then, hit the Script execution play button to proceed.')
                
            # Set DRRs
            set_progress('Setting DRRs to Breast', percentage = -1)
            for beam_set in self.plan.BeamSets:
                SetBeamsetDrrSettings(beam_set, drr_type='Breast')
                
            # Rename setup fields for all beamsets
            set_progress('Renaming setup fields', percentage = -1)
            for beam_set in self.plan.BeamSets:
                RenameSetupFields(beam_set)
    
            # Save and set view for user - Plan evaluation with clinical goals tab
            set_progress('Saving and finished!', percentage = -1)
            self.patient.Save()
            SelectUIPlanEvalClinicalGoals(self.plan.Name)
            
            # End message and exit
            set_progress('Final thoughts', percentage = -1)
            self.end_message()

        except Exception as e:
            _alert_physicist_error(e, message=__name__)
            _logger.error("[FAILED] in %s.  Email notification sent.  Exception: %s", __name__, str(e))
            set_progress("Waiting for user to hit play button...", percentage = -1)
            await_user_input(message="[FAILED] script.  Physicist alerted to address the issue.")
            set_progress("Sending physicist notification...", percentage = -1)
            time.sleep(3)
            self._abort_script_error(exc=e, message=str(e))

