# -*- coding: utf-8 -*-
"""Automate generating the TPS Monthly QA PDF document.

Created on Thu Mar 27 07:46:24 2025

@author: clanco01
"""
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
from datetime import datetime
from tkinter import messagebox, Tk

# === Local imports ===
from RSutil.LogUtil.rs_logging import LOGGERS, set_logger_mode
from RSutil.ErrorsUtil.error_dispatcher import DispatcherConfig
from RSutil.ErrorsUtil.rs_errors import report_error
from RSutil.ErrorsUtil.error_codes import PROMPT_USER, ALERT_PHYSICIST, ABORT_SCRIPT

# === Setup Logger ===
_logger = LOGGERS["eqd2_summation"]
if _DEBUG_THIS_MODULE:
    set_logger_mode(_logger, "debug")

def _alert_physicist_error(
        exc: Exception, 
        metadata: dict | None = None, 
        message: str | None = None
):                                              
    if not _DEBUG_THIS_MODULE:
        cfg = DispatcherConfig()
        cfg.alert_recipients = ["owen.clancey@nyulangone.org"]
        report_error(
                error_def=ALERT_PHYSICIST.SYSF_UNHANDLED_EXCEPTION, 
                original_exception=exc, 
                context={"module": "main_tps_monthly_qa.py"},
                metadata=metadata,
                message=message,
                dispatcher_config=cfg,
            )

if _ALERT_PHYSICIST_ON_ALL_USES:
    message = "Running main_tps_monthly_qa.py...."
    e = RuntimeError("INFO ONLY - TPS Monthly QA initialized.  Review patient data in logs and summation in Raystation.")
    _alert_physicist_error(e, message=message)


class TPSMonthlyQA:
    
    def __init__(self):
        
        self.base_plan_name = "TPS Monthly QA"
        self.case = None
        self.case_name = "Case 1"
        self.default_voxel_size = { 'x': 0.25, 'y': 0.25, 'z': 0.25 }
        self.directory = None
        self.exam = None
        self.full_path = None
        self.mc_algorithm = "ElectronMonteCarlo"
        self.mc_uncertainty = 0.005
        self.mts_settings_non_ck={ 'DisplayName': None, 'MotionSynchronizationSettings': None, 
                                                'RespiratoryIntervalTime': None, 'RespiratoryPhaseGatingDutyCycleTimePercentage': None, 
                                                'MotionSynchronizationTechniqueType': "Undefined" }
        self.mts_settings_ck={ 'DisplayName': "Fiducial", 'MotionSynchronizationSettings': None, 
                                                'RespiratoryIntervalTime': None, 'RespiratoryPhaseGatingDutyCycleTimePercentage': None, 
                                                'MotionSynchronizationTechniqueType': "Fiducial" }
        self.path = r"\\Client\F$\SHARING\Radiation Oncology Physics\TPS Monthly QA\Raystation TPS Monthly QA"
        self.path_for_progress_bar = 'F\SHARING\Radiation Oncology Physics\TPS Monthly QA\Raystation TPS Monthly QA'
        self.patient = None
        self.patient_db = get_current('PatientDB')
        self.patient_id = '02134657'
        self.plan = None
        self.template_name = "TPS Monthly"

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
                context={"module": "main_tps_monthly_qa.py"},
                metadata={},
                message=message,
            )
    
    def _abort_script_error(
            self, 
            exc: Exception, 
            metadata: dict | None = None, 
            message: str | None = None
    ):
        _logger.debug("Inside _abort_script_error()")                                            
        report_error(
                error_def=ABORT_SCRIPT.DATA_REQUIRED_MISSING, 
                original_exception=exc, 
                context={"module": "main_tps_monthly_qa.py"},
                metadata={},
                message=message,
            )
        raise RuntimeError(str(exc))

    def show_messagebox(self, message, title="Information"):
        root = Tk()
        root.withdraw()  # Hide the root window
        root.attributes("-topmost", True)  # Bring messagebox to the front
        messagebox.showinfo(title=title, message=message)
        root.destroy()  # Clean up the hidden root window

    def set_ui_view(self, beam_set_name, menu_item="Plan design", tab_module="Plan setup", tab_control="Plan", tab_item="Plan"):

        # Get current UI data
        ui = get_current('ui')
        
        try:
            # Load the plan's beam set
            infos = self.case.TreatmentPlans[self.plan.Name].QueryBeamSetInfo(Filter = {'Name': beam_set_name})
            self.case.TreatmentPlans[self.plan.Name].LoadBeamSet(BeamSetInfo = infos[0])

            # Select menu item
            ui.TitleBar.Navigation.MenuItem[menu_item].Button.Click()
            
            # Select tab control module
            ui.TabControl_Modules.TabItem[tab_module].Select()
            
            # Select Plan tab
            ui.Workspace.TabControl[tab_control].TabItem[tab_item].Select()
            

        except KeyError as e:
            print(f"Error: Unable to find UI element - {str(e)}")
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            
        # Set the scripting tab visable to the user
        ui.ToolPanel.TabItem['Scripting'].Select()
        
    def get_current_plan(self):
        self.plan = get_current("Plan")
    
    # Save and set the scripting tab visable to the user
    def save_and_set_ui_scripting_tab(self):
        patient = get_current("Patient")
        patient.Save()
        ui = get_current('ui')
        ui.ToolPanel.TabItem['Scripting'].Select()
        
    def open_qa_patient(self):
        # Query data base
        info = self.patient_db.QueryPatientInfo(Filter = {'PatientID': self.patient_id})
        
        # Verify uniqueness
        if len(info) != 1:
          raise Exception("No patient or more than one patient with last name '{0}' in the database".format(len(info)))
        
        # Check to see if patient is already loaded
        try:
            current_patient = get_current("Patient")
            if current_patient.PatientID == self.patient_id:
                self.patient = current_patient
            else:
                self.patient = self.patient_db.LoadPatient(PatientInfo = info[0])
        except:
            self.patient = self.patient_db.LoadPatient(PatientInfo = info[0])
        
        # Set current case to case with index 0
        self.save_and_set_ui_scripting_tab()
        self.case = self.patient.Cases[self.case_name]
        self.case.SetCurrent()
        
    def check_for_deprecated_machines(self):
        
        plan = self.case.TreatmentPlans[self.base_plan_name]
        plan.SetCurrent()
        for beam_set in plan.BeamSets:
            
            machine_name = beam_set.MachineReference.MachineName
            comm_time = beam_set.MachineReference.CommissioningTime
            
            machine_db = get_current("MachineDB")
            machine = machine_db.QueryCommissionedMachineInfo(Filter={'Name': machine_name})
            
            if comm_time == machine[0]["CommissionTime"]:
                print(f'{machine_name} is commissioned')
            else:
                self.show_messagebox(f"At least one machine is not commissioned.  Consider making a copy of the {self.base_plan_name} for good house keeping.  Then, set all the machines in {self.base_plan_name} to commissioned machines.  Re-run the script.")
                exit()
    
        print("All machines are commissioned.  Moving forward with script...")
        
    def create_tps_monthly_qa_plan(self):
        
        # Get all existing plan names
        existing_plan_names = [plan.Name for plan in self.case.TreatmentPlans]
        
        # Get current year and month
        now = datetime.now()
        base_name = f"TPS Monthly QA {str(now.year)[-2:]}{now.month:02d}"
        
        # Start with the base name
        new_plan_name = base_name
        suffix = 1
        
        # Alert user that plan name already exists
        if new_plan_name in existing_plan_names:
            print("Plan name already exists...")
            self.save_and_set_ui_scripting_tab()
            await_user_input(message="Current monthly QA plan looks like it may already have been done.  Check!  Hit script play button to continue or script stop button to cancel.")
        
        # Add _1, _2, etc. until the name is unique
        while new_plan_name in existing_plan_names:
            new_plan_name = f"{base_name}_{suffix}"
            suffix += 1

        # Create new plan
        self.case.CopyPlan(PlanName=self.base_plan_name, NewPlanName=new_plan_name, KeepBeamSetNames=True)
        
        # Set new plan
        self.plan = self.case.TreatmentPlans[new_plan_name]
        
        # Set plan to current
        self.save_and_set_ui_scripting_tab()
        self.plan.SetCurrent()
    
    # DOES NOT WORK FOR RADIXACT MACHINES BUT KEEP FOR POTENTIAL FUTURE USE
    def update_deprecated_machine(self, beam_set):
        beam_set_name = beam_set.DicomPlanLabel
        beam_set.DicomPlanLabel = "TO_BE_DELETED"
        machine_name = beam_set.MachineReference.MachineName
        modality = beam_set.Modality
        technique = beam_set.GetTreatmentTechniqueType()
        position = beam_set.PatientPosition
        try:
            tolerance = beam_set.PatientSetup.ToleranceTable.ToleranceTableLabel
        except:
            tolerance = None
        num_fractions = 1
        print(technique)
        
        self.exam = get_current("Examination")
        exam_name = self.exam.Name
        
        beam_set_new = self.plan.AddNewBeamSet(Name=beam_set_name, 
                                ExaminationName=exam_name, 
                                MachineName=machine_name, 
                                Modality=modality, 
                                TreatmentTechnique=technique, 
                                PatientPosition=position, 
                                NumberOfFractions=num_fractions, 
                                CreateSetupBeams=False, 
                                UseLocalizationPointAsSetupIsocenter=False, 
                                UseUserSelectedIsocenterSetupIsocenter=False, 
                                Comment="", 
                                RbeModelName=None, 
                                EnableDynamicTrackingForVero=False, 
                                NewDoseSpecificationPointNames=[], 
                                NewDoseSpecificationPoints=[], 
                                MotionSynchronizationTechniqueSettings=self.mts_settings_non_ck, 
                                Custom=None, 
                                ToleranceTableLabel=tolerance)
        
        # Copy each beam to new beam set
        for beam in beam_set.Beams:
            beam_set_new.CopyBeamsFromBeamSet(BeamSetToCopyFrom=beam_set, BeamsToCopy=[beam.Name])
        
        # Delete beam set
        self.save_and_set_ui_scripting_tab()
        beam_set.DeleteBeamSet()
    
    
    def delete_dose_to_all_beamsets(self):
        # Get the current corner of the dose grid
        print("Getting dose grid...")
        try:
            dose_grid = self.plan.BeamSets[0].GetDoseGrid()
        except:
            self.plan = get_current("Plan")
            dose_grid = self.plan.BeamSets[0].GetDoseGrid()
        
        # Change the dose grid corner
        corner = dose_grid.Corner
        print(corner.x)
        corner["x"] -= 0.25
        print(corner.x)
        
        # Use updated dose grid corner to delete the dose distributions for the plan
        self.plan.BeamSets[0].UpdateDoseGrid(Corner=corner, VoxelSize=dose_grid.VoxelSize, NumberOfVoxels=dose_grid.NrVoxels)
        
        # Set default dose grid
        self.plan.BeamSets[0].SetDefaultDoseGrid(VoxelSize=self.default_voxel_size)
        self.plan.BeamSets[0].FractionDose.UpdateDoseGridStructures()
        
    def calculate_dose_to_all_beamsets(self):
        
        # Calculate dose to all beam sets
        for beam_set in self.plan.BeamSets:
            set_progress(f'Calculating dose to beam set: {beam_set.DicomPlanLabel}')
            dose_algorithim = beam_set.AccurateDoseAlgorithm.DoseAlgorithm
            if dose_algorithim == self.mc_algorithm:
                beam_set.AccurateDoseAlgorithm.MCStatisticalUncertaintyForFinalDose = self.mc_uncertainty
            
            try:
                beam_set.ComputeDose(ComputeBeamDoses=True, DoseAlgorithm=dose_algorithim, ForceRecompute=False, RunEntryValidation=True)
            except:
                await_user_input(message="Check the plan.  Initial dose calculation failed.  There may already be dose.  Clear dose by adjusting the dose grid.  Hit the play button when done.")
                beam_set.ComputeDose(ComputeBeamDoses=True, DoseAlgorithm=dose_algorithim, ForceRecompute=False, RunEntryValidation=True)
        
        # Save
        self.save_and_set_ui_scripting_tab()
    
    def print_report(self):
        # Save
        self.save_and_set_ui_scripting_tab()
        
        # Get patient name
        name = self.patient.GetAlphabeticPatientName()
        
        # Get full file name
        self.file_name = self.path + "\Treatment plan report, " + name["FirstName"] +" " + name["LastName"] + ", " + self.plan.Name + ".pdf"
        print(f"File name is: {self.file_name}")
        
        # Print report
        self.plan.BeamSets[0].CreateReport(templateName=self.template_name, filename=self.file_name, ignoreWarnings=True)
    
    def main(self):
        try:
            # Opening patient
            set_progress(f'Opening {self.base_plan_name} and creating monthly QA plan...')
            self.open_qa_patient()
            
            # Check for deprecated machines
            self.check_for_deprecated_machines()
            
            # Copying base plan with new name
            set_progress('Copying base monthly QA plan...')
            self.create_tps_monthly_qa_plan()
            
            # Set UI view to Plan design to plan setup with Plan tab selected
            self.set_ui_view(self.plan.BeamSets[0].DicomPlanLabel)
            # Clearing dose by adjusting dose grid
            set_progress('Clearing dose by adjusting dose grid...')
            self.delete_dose_to_all_beamsets()
            
            # Calculating dose
            set_progress('Calculating dose to all beam sets...')
            self.calculate_dose_to_all_beamsets()
            
            # Printing the report
            set_progress(f'Printing report to {self.path_for_progress_bar}')
            self.print_report()
            
            # Complete message
            set_progress("Finished!")
            self.show_messagebox(f"Monthly TPS report saved to: {self.path_for_progress_bar}")

        except Exception as e:
            _logger.error("[FAILED] in main_tps_monthly_qa.py.  Email notification sent.  Exception: %s", str(e))
            self._prompt_user_acknowledge(exc=e, message=str(e))
            _alert_physicist_error(e)
            self._abort_script_error(exc=e, message=str(e))
