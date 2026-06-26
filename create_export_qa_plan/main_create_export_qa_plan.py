"""Creates a verification plan per beam set.  The QA plan and dose are exported to 
the IMRT QA folder.  If the verification plan is a Radixact plan, the QA plan is exported
to the iDMS via Raygateway.  User can apply shifts.

Created on 11/10/2025

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
from typing import Optional
import os
import json
import tkinter as tk
from tkinter import messagebox
import sys
from time import sleep
import math
from pathlib import Path
import copy

# === Local imports ===
from RSutil.LogUtil.rs_logging import LOGGERS, set_logger_mode
from RSutil.ErrorsUtil.error_dispatcher import DispatcherConfig
from RSutil.ErrorsUtil.rs_errors import report_error
from RSutil.ErrorsUtil.error_codes import PROMPT_USER, ALERT_PHYSICIST, ABORT_SCRIPT
from RSutil.patient_data_util import PatientDataUtil
from RSutil.variables import RADIXACTS, VARIAN_MACHINES, TRUEBEAMS, EX

# === Setup Logger ===
_logger = LOGGERS["create_export_qa_plan"]
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
                context={"module": __name__},
                metadata=metadata,
                message=message,
                dispatcher_config=cfg,
            )

if _ALERT_PHYSICIST_ON_ALL_USES:
    e = RuntimeError("INFO ONLY - Create and Export QA Plan script initialized.  Review patient data in logs.")
    _alert_physicist_error(e, message=__name__)

# ===== Constants ========
PHANTOMS = {
    "truebeam": {
        "name": "Octavius Phantom - Exact Couch Rails In",
        "id": "123456",
        "iso": {"x": -0.1172943, "y": 0.09004741, "z": -0.1},    
    },
    "ex": {
        "name": "QA Solid_Water",
        "id": "0000WaterQA",
        "iso": {"x": -0.15, "y": -30.56, "z": 0.05}, 
    },
    "radixact": {
        "name": "RadixactQA Jan162026",
        "id": "radixaxctQA01162026",
        "iso": {"x": -0.1, "y": 0.1, "z": -0.23}, 
    } ,
}

DOSE_GRID = { 'x': 0.25, 'y': 0.25, 'z': 0.25 }

MODALITY_NOT_SUPPORTED = ["Electrons"]
BASE_MAX_CHAR = 13
QA_PLAN_NAME_SUFFIX = "_QA"

# ====== MAIN CLASS =====

class CreateExportQAPlan:
    
    def __init__(
            self, 
            path: str = r"\\Client\F$\SHARING\Radiation Oncology Physics\IMRT QA",
            flag_for_user_questions: bool = True,
            field_size_limit: float = 14.0, # Size for the PTW 1500
            machines_zero_gantry: list = ["21EX"],
            check_delivery_technique: list = ["SMLC", "Conformal"],
            max_dose_in_iso_plane_to_max_dose: float = 0.9 # Ratio of dose in isocenter plane to max dose
        ):
        
        # Get patient data
        self.pdu = PatientDataUtil()
        self.patient = self.pdu.get_current_patient()
        self.plan = self.pdu.get_current_plan()
        
        # Create path data for saving the exported DICOM files
        directory = self.patient.PatientID + "_" + self.patient.Name
        self.full_path = os.path.join(path, directory)
        os.makedirs(self.full_path, exist_ok=True)
        
        # Set maximum field size in cm
        self.field_size_limit = field_size_limit
        
        # Set minimum ratio of dose in device center plane to max dose in plan
        self.max_dose_in_iso_plane_to_max_dose = max_dose_in_iso_plane_to_max_dose
        
        # Parameters where gantry angle is set to zero
        self.machines_zero_gantry = machines_zero_gantry
        
        # Delivery techinque config
        self.check_delivery_technique = check_delivery_technique
        self.flag_for_user_questions = flag_for_user_questions
              

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
                context={"module": __name__},
                metadata={},
                message=message,
            )
    
    def _abort_script_error(
            self, 
            exc: Exception, 
            metadata: Optional[dict] = None, 
            message: Optional[str] = None
    ):
        report_error(
                error_def=ABORT_SCRIPT.DATA_REQUIRED_MISSING, 
                original_exception=exc, 
                context={"module": __name__},
                metadata={},
                message=message,
            )
        raise RuntimeError(str(exc))

    def save_patient(self):
        # Save patient to update UI
        set_progress('Saving...', percentage = -1)
        self.patient.Save()
        
    def ask_user_for_shifts(self, beam_set):
        
        # Get verification plan
        verification_plans = self.get_verification_plans(beam_set)
        
        # Loop through each verification plan
        for verification_plan in verification_plans:
            # Ask the user to make any shifts
            ask_for_shifts = True
            initial_message_flag = True
            while ask_for_shifts:
                # Set progress bar
                set_progress('User making shifts if needed...when done, hit the Script play execution button', percentage = -1)
                
                # Ask user for isocenter shifts
                if initial_message_flag:
                    await_user_input('If needed, shift isocenter.  Then, hit the Scipt execution play button.')
                    initial_message_flag = False
                else:
                    await_user_input('Verify isocenter shifts.  If needed, shift isocenter again.  Then, hit the Scipt execution play button.')
                
                if verification_plan.BeamSet.FractionDose.DoseValues is not None: #Exit flag of while loop
                    _logger.info("No shifts made")
                    ask_for_shifts = False
                else: # Compute dose again
                    _logger.info("Shifts made and re-calculating dose")
                    set_progress('Calculating dose with updated isocenter...', percentage = -1)
                    self.calc_dose(verification_plan.BeamSet)

    def get_verification_plans(self, beam_set):
        """Returns all verification plans associated with the beam set.
        Currently, only a singhle verification plan can be handled per beam set."""
        # Get verification plans for current plan
        verification_plans = [v for v in self.plan.VerificationPlans if v.OfRadiationSet.DicomPlanLabel == beam_set.DicomPlanLabel]
    
        return verification_plans


    def dose_and_plan_export_to_file(self, beam_set):
        """ DICOM QA export to file
    
        The parameter ignore_precondition_warnings can be used to handle possible warnings. Setting to false will generate exceptions for precondition warnings."""
    
        # Set progress bar
        set_progress('Exporting QA plan and dose to file...', percentage = -1)
        
        # Get the verification plans. This gets all verification plans connected to the beam set.
        verification_plans = self.get_verification_plans(beam_set)
    
        for verification_plan in verification_plans:
            
            # Make sure there is dose calculated 
            if verification_plan.BeamSet.FractionDose.DoseValues is None:
                set_progress("Calculating dose...", percentage = -1)
                self.calc_dose(verification_plan.BeamSet)
                self.save_patient()
                set_progress('Exporting QA plan and dose to file...', percentage = -1)
            
            # It is not necessary to assign all of the parameters, you only need to assign the
            # desired export items.
            verification_plan.ScriptableQADicomExport(
                ExportFolderPath = self.full_path,
                QaPlanIdentity = 'Patient',
                ExportExamination = False,
                ExportExaminationStructureSet = False,
                ExportBeamSet = True,
                ExportRtRadiationSet  = False,
                ExportRtRadiations  = False,
                ExportBeamSetDose = True,
                ExportBeamSetBeamDose = False,
                IgnorePreConditionWarnings = True,
            )
        
    def create_qa_plan(self, beam_set):
        
        # Verify no verification plan already exists for the beam set before proceeding
        verification_plans = self.get_verification_plans(beam_set)
        
        if len(verification_plans) == 0:
            # Set progress bar
            set_progress('Creating QA plan...', percentage = -1)
            
            # Set parameters for QA plan based upon the machine
            machine = beam_set.MachineReference.MachineName
            phantom = {}
            if machine in TRUEBEAMS:
                phantom = copy.deepcopy(PHANTOMS["truebeam"])
            elif machine in RADIXACTS:
                phantom = copy.deepcopy(PHANTOMS["radixact"])
            elif machine in EX:
                phantom = copy.deepcopy(PHANTOMS["ex"])
            else:
                msg = "Machine not supported"
                _logger.error(msg)
                raise ValueError("Machine not supported")
            
            # Set gantry angle to zero for selected machines
            if machine in self.machines_zero_gantry:
                gantry_angle = 0
            else:
                gantry_angle = None
            
            # Set QA plan name
            base_name = str(beam_set.DicomPlanLabel)
            if len(base_name) > BASE_MAX_CHAR:
                base_name = base_name[:BASE_MAX_CHAR]
            qa_plan_name = base_name + QA_PLAN_NAME_SUFFIX
            
            # Create QA verification plan (vp)
            beam_set.CreateQAPlan(
                PhantomName=phantom["name"], 
                PhantomId=phantom["id"], 
                QAPlanName=qa_plan_name,
                IsoCenter=phantom["iso"],
                DoseGrid=DOSE_GRID,
                GantryAngle=gantry_angle, 
                CollimatorAngle=None, 
                CouchRotationAngle=0, 
                ComputeDoseWhenPlanIsCreated=True, 
                DesiredStatisticalUncertaintyForElectrons=None, 
                MotionSynchronizationTechniqueSettings={ 
                    'DisplayName': None, 
                    'MotionSynchronizationSettings': None, 
                    'RespiratoryIntervalTime': None, 
                    'RespiratoryPhaseGatingDutyCycleTimePercentage': None, 
                    'MotionSynchronizationTechniqueType': "Undefined" 
                }, 
                RemoveCompensators=False, 
                EnableDynamicTracking=False, 
                SetupBeamsSettings={ 'UseSetupBeams': False, 
                                    'UseLocalizationPointAsSetupIsocenter': False, 
                                    'UseUserSelectedIsocenterAsSetupIsocenter': False }
            )
    
    def export_qa_to_raygateway(self, beam_set):
        """DICOM export to Raygateway"""
    
        # Set progress bar
        set_progress('Exporting QA plan to iDMS...', percentage = -1)
    
        # Get the verification plans. This gets all verification plans for a beam set.
        verification_plans = self.get_verification_plans(beam_set)
        
        for verification_plan in verification_plans:
            verification_plan.ScriptableQADicomExport(
                RayGatewayTitle = 'Raygateway',
                QaPlanIdentity = 'Phantom',
                ExportExamination = True,
                ExportExaminationStructureSet = True,
                ExportBeamSet = True,
                ExportRtRadiationSet  = False,
                ExportRtRadiations= False,
                ExportBeamSetDose = True,
                ExportBeamSetBeamDose = False,
                IgnorePreConditionWarnings = True,
            )

    
    @staticmethod
    def calc_dose(beam_set):
        beam_set.ComputeDose(
            ComputeBeamDoses=True, 
            DoseAlgorithm="CCDose", 
            ForceRecompute=False, 
            RunEntryValidation=True,
        )

    @staticmethod
    def user_message(message):
        
        # Create a temporary Tkinter window (it won't be shown)
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        
        # Make the temporary window topmost
        root.attributes('-topmost', True)
        
        # Display an information message box with an OK button
        messagebox.showinfo("Information", message)
        
        # Destroy the hidden Tkinter window
        root.destroy()
        
    @staticmethod
    def message_create_qa_plan_yes_no(beam_set):
        # Create a temporary Tkinter window
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        
        # Make the temporary window topmost
        root.attributes('-topmost', True)
        
        # Display Yes/No message box
        response = messagebox.askyesno(
            "Confirm QA Plan Creation",
            f"Do you want to create a QA plan for {beam_set.DicomPlanLabel} "
            "beam set even though it has a delivery technique of {beam_set.DeliveryTechnique}?"
        )
        
        # Destroy the hidden Tkinter window
        root.destroy()
        
        return response
    
    @staticmethod
    def user_no_verification_plan(beam_set):
        set_progress(f'User selected not to create a QA plan on {beam_set.DicomPlanLabel} beam set...')
        sleep(3)
    
    @staticmethod
    def calc_max_field_dist_from_iso(beam_set):
        '''Checks if the field is inside the QA device for a beam set.
            The max_field_size is the distance from the isocenter to the field edge
            in the sup-inf direction.'''
            
        # Store the maximum field size as measured in the sup-inf direction
        max_field_size = 0
        
        # Store the jaws to use for calculation
        inf = [0, 2]
        sup = [1, 3]
        
        # Check fields based upon machine type
        machine = beam_set.MachineReference.MachineName
    
        # Loop through all segments in each beam to find largest jaw position
        for beam in beam_set.Beams:
            if machine in VARIAN_MACHINES:
    
                # Get the colimator angle
                coll_angle_degree = beam.InitialCollimatorAngle
                if (coll_angle_degree >=0 and coll_angle_degree <= 90) or (coll_angle_degree >=180 and coll_angle_degree <=270):
                    inf = [0, 2]
                    sup = [1, 3]
                else:
                    inf = [0, 3]
                    sup = [1, 2]
                
                # Calculate collimator angle in radians
                coll_angle_rad = 2 * math.pi * beam.InitialCollimatorAngle / 360
                
                for segment in beam.Segments:
                    dist_sup = math.sqrt( ( segment.JawPositions[sup[0]] * math.cos(coll_angle_rad) )**2 + ( segment.JawPositions[sup[1]] * math.cos(coll_angle_rad) )**2 )
                    dist_inf = math.sqrt( ( segment.JawPositions[inf[0]] * math.cos(coll_angle_rad) )**2 + ( segment.JawPositions[inf[1]] * math.cos(coll_angle_rad) )**2 )
                    
                    # Set printing for debugging only
                    _logger.debug(f"Sup distance: {dist_sup}       Inf distance: {dist_inf}")
                    
                    # Set max field size to largest sup-inf distance
                    if dist_sup > max_field_size:
                        max_field_size = dist_sup
                    if dist_inf > max_field_size:
                        max_field_size = dist_inf
            
    
            elif machine in RADIXACTS:
                
                # Printing for debugging only
                _logger.debug(f"Sup distance: {abs(beam.Segments[0].CouchYOffset)}    Inf distance: {abs(beam.Segments[len(beam.Segments)-1].CouchYOffset)}")
                
                # Use couch positions for sup and inf dimensions
                if abs(beam.Segments[0].CouchYOffset) > max_field_size:
                    max_field_size = abs(beam.Segments[0].CouchYOffset)
                if abs(beam.Segments[len(beam.Segments)-1].CouchYOffset) > max_field_size:
                    max_field_size = abs(beam.Segments[len(beam.Segments)-1].CouchYOffset)
                
            else:
                msg = "Machine not supported"
                _logger.error(msg)
                raise ValueError(msg)
        
        return max_field_size

    def rename_latest_rs_exports(self, new_name: str = "qa_plan") -> None:
        """
        Find the most recently exported RP (plan) and RD (dose) files in a directory
        and rename them to the given new names.
    
        Args:
            new_name (str): New file name for the plan and dose (without extension).
        """
        export_path = Path(self.full_path)
        files = list(export_path.glob("*"))
        if not files:
            _logger.debug("No files found in directory.")
            return
    
        # Find the newest RP and RD files
        rp_files = [f for f in files if f.name.startswith("RP")]
        rd_files = [f for f in files if f.name.startswith("RD")]
        if not rp_files or not rd_files:
            _logger.debug("Missing RP or RD file.")
            return
    
        latest_rp = max(rp_files, key=lambda f: f.stat().st_mtime)
        latest_rd = max(rd_files, key=lambda f: f.stat().st_mtime)
    
        # Preserve extensions (e.g., .dcm)
        new_rp_path = export_path / f"RP_{new_name}{latest_rp.suffix}"
        new_rd_path = export_path / f"RD_{new_name}{latest_rd.suffix}"
    
        latest_rp.rename(new_rp_path)
        latest_rd.rename(new_rd_path)

    def check_for_high_dose_at_iso_plane(self, bs):
        
        try:
            
            _logger.info("Checking for High Dose at plane of measurement...")
            
            machine = bs.MachineReference.MachineName
            if machine in RADIXACTS:
                machine_name = "radixact"
            elif machine in TRUEBEAMS:
                machine_name = "truebeam"
            elif machine in EX:
                machine_name = "ex"
            else:
                _logger.warning(f"Machine not supported: {machine}")
                return False
            
            device_center_y_coord = PHANTOMS[machine_name]["iso"]["x"]
            
            verification_plans = self.get_verification_plans(bs)
            
            for vp in verification_plans:
                dose_data_3d = vp.BeamSet.FractionDose.DoseValues.DoseData
                corner = vp.BeamSet.FractionDose.InDoseGrid.Corner
                voxel_size = vp.BeamSet.FractionDose.InDoseGrid.VoxelSize
                y_dose_data_index = round( (device_center_y_coord - corner.y) / voxel_size.y )
                dose_data_iso_plane = dose_data_3d[:, y_dose_data_index, :]
                _logger.info(f"Max dose of {dose_data_3d.max()} compared to dose max in measurement plane of {dose_data_iso_plane.max()}")
                if dose_data_3d.max() * self.max_dose_in_iso_plane_to_max_dose > dose_data_iso_plane.max():
                    _logger.info("Low dose identified in measurement plan compared to max dose.  Asking user for shifts.")
                    return True
            
        except Exception as e:
            _logger.error("[FAILED] to check for high dose at plane of measurement.")
            _alert_physicist_error(e, message=__name__)
            return False

    def main(self):
        try:
            # Loop through each beam set in the plan
            for bs in self.plan.BeamSets:
                bs_name = bs.DicomPlanLabel
                # Check on allowed modalities
                if bs.Modality in MODALITY_NOT_SUPPORTED:
                    msg = f"The modality {bs.Modality} of your {bs_name} beam set is not supported and will be skipped."
                    self.user_message(msg)
                    _logger.info(msg)
                    continue
                
                # Check plan for delivery techinque before proceeding with QA plan creation and export
                response = True # Default
                if (
                    bs.DeliveryTechnique in self.check_delivery_technique
                    and self.flag_for_user_questions
                ):
                    # Display Yes/No message box
                    response = self.message_create_qa_plan_yes_no(bs)
                
                if response: # Create and export QA plan
                    # Create QA plan
                    _logger.info("Creating verification for beamset: %s", bs)
                    self.create_qa_plan(bs)
                                
                    # Check if the fields are inside the QA device
                    if (
                            (
                            self.calc_max_field_dist_from_iso(bs) > self.field_size_limit
                            or self.check_for_high_dose_at_iso_plane(bs)
                            )
                        and self.flag_for_user_questions
                    ):
                        # Ask user for QA plan shifts
                        _logger.info("Asking user for shifts, if needed...")
                        self.ask_user_for_shifts(bs)
                    
                    
                    # Save patient needed to be performed prior to export
                    _logger.info("Saving...")
                    self.save_patient()
                    
                    # Export QA dose and plan to file
                    _logger.info("Exporting dose and plan to file...")
                    self.dose_and_plan_export_to_file(bs)
                    
                    # Rename files
                    try:
                        new_name = self.plan.Name + "_" + bs_name
                        self.rename_latest_rs_exports(new_name=new_name)
                        _logger.info("Renamed exported dose and plan files...")
                    except Exception as e:
                        _logger.info("Failed to rename files: %s", str(e))
                        pass
                    
                    # Check for Radixact machine to export QA plan to iDMS
                    if bs.MachineReference['MachineName'] in RADIXACTS:
                        _logger.info("Exporting QA plan to iDMS...")
                        try:
                            self.export_qa_to_raygateway(bs)
                        except Exception as e:
                            raise RuntimeError("Failed to export QA plan to iDMS: {}".format(e)) from e

                        
                else: # User does not want a verification plan for current beam set
                    _logger.info("User opted to not have a verifcaiton plan for beamset: %s", bs)
                    self.user_no_verification_plan(bs)

        except Exception as e:
            
            # Trimmed error message
            error_str = str(e)
            trimmed_error = error_str[:1000]
            
            # Standard error output
            _alert_physicist_error(e, message=__name__)
            _logger.error("[FAILED] in %s.  Email notification sent." , __name__)
            set_progress("Waiting for user to hit play button...", percentage = -1)
            await_user_input(message=f"[FAILED] script.  Physicist alerted to address the issue: {trimmed_error}")
            set_progress("Sending physicist notification...", percentage = -1)
            sleep(3)
            self._abort_script_error(exc=e, message=str(e))
            


        