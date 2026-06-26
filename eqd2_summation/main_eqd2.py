"""
RaystationScriptingPROD\eqd2_summation\main_eqd2.py

Created on Thu Oct  2 15:17:42 2025

Automates an EQD2 dose summation


@author: clanco01
"""
from __future__ import annotations

# === DEBUG SETTINGS ===
_DEBUG_THIS_MODULE = False
_ALERT_PHYSICIST_ON_ALL_USES = False

# === Raystation import ===
try:
    from connect import set_progress, await_user_input
except Exception:
    pass

# === WORKING DIRECTORY ===
import sys
sys.path.append(r"\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
sys.path.append(r"F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")

# === Main library imports ===
from dataclasses import dataclass
from typing import Optional
import time

# === Local imports ===
from RSutil.LogUtil.rs_logging import LOGGERS, set_logger_mode
from eqd2_summation.ui_eqd2 import EQD2SelectionWindow
from RSutil.ErrorsUtil.error_dispatcher import DispatcherConfig
from RSutil.ErrorsUtil.rs_errors import report_error
from RSutil.ErrorsUtil.error_codes import PROMPT_USER, ALERT_PHYSICIST, ABORT_SCRIPT
from breast_sib.SelectUIPlanEvalClinicalGoals import SelectUIPlanEvalClinicalGoals
from RSutil.patient_data_util import PatientDataUtil

# === Setup Logger ===
_logger = LOGGERS["eqd2_summation"]
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
                context={"module": "main_eqd2.py"},
                metadata=metadata,
                message=message,
                dispatcher_config=cfg,
            )

if _ALERT_PHYSICIST_ON_ALL_USES:
    e = RuntimeError("INFO ONLY - EQD2 script initialized.  Review patient data in logs.")
    _alert_physicist_error(e, message=__name__)


@dataclass
class DeformableSettings:
    CorrelationCoefficient = { 
        'NumberOfResolutionLevels': 3, 
        'InitialResolution': { 'x': 0.5, 'y': 0.5, 'z': 0.5 }, 
        'FinalResolution': { 'x': 0.25, 'y': 0.25, 'z': 0.25 }, 
        'InitialGaussianSmoothingSigma': 2, 
        'FinalGaussianSmoothingSigma': 0.333333333333333, 
        'InitialGridRegularizationWeight': 400, 
        'FinalGridRegularizationWeight': 400, 
        'ControllingRoiWeight': 0.5, 
        'ControllingPoiWeight': 0.1, 
        'MaxNumberOfIterationsPerResolutionLevel': 1000, 
        'ImageSimilarityMeasure': "CorrelationCoefficient", 
        'DeformationStrategy': "Default", 
        'ConvergenceTolerance': 1E-05 
    }
    
    MutualInformation = { 
        'NumberOfResolutionLevels': 3, 
        'InitialResolution': { 'x': 0.5, 'y': 0.5, 'z': 0.5 }, 
        'FinalResolution': { 'x': 0.25, 'y': 0.25, 'z': 0.25 }, 
        'InitialGaussianSmoothingSigma': 2, 
        'FinalGaussianSmoothingSigma': 0.333333333333333, 
        'InitialGridRegularizationWeight': 2000, 
        'FinalGridRegularizationWeight': 2000, 
        'ControllingRoiWeight': 0.5, 
        'ControllingPoiWeight': 0.1, 
        'MaxNumberOfIterationsPerResolutionLevel': 1000, 
        'ImageSimilarityMeasure': "MutualInformation", 
        'DeformationStrategy': "Default", 
        'ConvergenceTolerance': 1E-05 
    }

class EQD2DoseSummation():
    
    # === Initialization ===
    def __init__(self):
        _logger.info("Initializing EQD2DoseSummation...")
        self._base_name_reg = "HybridDefReg"
        self._base_name_sum = "SummedDose"
        self._base_name_plan = "SumPlan"
        self.external_threshold_level = -250
        self.eqd2 = {}
        self.deformed_registration = {}
        self.deformed_doses = {}
        try:
            self.pdu = PatientDataUtil()
        except Exception as e:
            self.pdu.case = None
            _logger.error("PatientDataUtil() failed in EQD2DoseSummation initialization: %s", e)
    
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

    
    # === Helper Functions ===
    def _get_new_deformable_name(self):
        deformable_reg_names = self.pdu.get_deformable_registration_names()
        
        # Keep modifying the name until it's unique
        suffix = 1
        deform_reg_name = f"{self._base_name_reg}{suffix}_"
        while any(name.startswith(deform_reg_name) for name in deformable_reg_names):
            deform_reg_name = f"{self._base_name_reg}{suffix}_"
            suffix += 1
        
        return deform_reg_name
    
    def _get_sum_dose_name(self):
        # Keep modifying the name until it's unique
        suffix = 1
        sum_dose_name = f"{self._base_name_sum}"
        while any(name.startswith(sum_dose_name) for name in self.pdu.get_dose_evaluation_names()):
            sum_dose_name = f"{self._base_name_sum}{suffix}"
            suffix += 1
        
        _logger.debug("New sum dose name: %s", sum_dose_name)
        return sum_dose_name
     
    def _get_new_plan_name(self):
        plan_names = self.pdu.get_plan_names()
        # Keep modifying the name until it's unique
        suffix = 1
        plan_name = f"{self._base_name_plan}"
        while any(name.startswith(plan_name) for name in plan_names):
            plan_name = f"{self._base_name_plan}{suffix}"
            suffix += 1
        
        return plan_name
    
    def _assign_target_ct_exam_names(self):
        _logger.debug("Inside _assign_target_ct_exam_names()...")
        
        target_ct_exam_names = []
        for key, value in self.selected_values["plan_data"].items():
            ct_exam_name = value["ct_exam_name"]
            _logger.debug("CT exam name in PlanName_BeamSetName: %s || %s", key, ct_exam_name)
            if ct_exam_name != self.selected_values["ct_exam_name"]:
                target_ct_exam_names.append(ct_exam_name)
    
        target_ct_exam_names = list(set(target_ct_exam_names))
        _logger.debug("Target CT names for deformable registration: %s", target_ct_exam_names)
        return target_ct_exam_names

    def _get_dose_eval_indices(self):
        """Return mapping of DoseOnExaminations index → list of DoseEvaluations indices."""
        dose_eval_indices = {}
        try:
            if not self.pdu.case.TreatmentDelivery.FractionEvaluations[0].DoseOnExaminations:
                _logger.debug("FractionEvaluations is empty in _get_dose_eval_indices().  Returning dose_eval_indices = {}")
                return dose_eval_indices
        except Exception as e:
            _logger.debug("FractionEvaluations does not exist in _get_dose_eval_indices().  Returning dose_eval_indices = {}: %s", str(e))
            return dose_eval_indices
        for idx_exam, dose_on_exam in enumerate(
            self.pdu.case.TreatmentDelivery.FractionEvaluations[0].DoseOnExaminations
        ):
            try:
                dose_eval_indices[idx_exam] = list(range(len(dose_on_exam.DoseEvaluations)))
            except Exception as e:
                _logger.debug("DoseOnExaminations is empty for %s: %s", idx_exam, e)
        
        return dose_eval_indices
    
    @staticmethod
    def _find_new_dose_indices(new_dose_eval_indices, old_dose_eval_indices):
        idx_exam = idx_eval = None
        for exam_idx, eval_list in new_dose_eval_indices.items():
            old_list = old_dose_eval_indices.get(exam_idx, [])
            # find any new eval index in this exam
            new_indices = [i for i in eval_list if i not in old_list]
            if new_indices:
                idx_exam = exam_idx
                idx_eval = new_indices[0]
                break
        return idx_exam, idx_eval
    
    # === Methods ===
    def _find_non_photon_plans(self):
        for key, value in self.selected_values["plan_data"].items():
            beamset = value["beamset"]
            while beamset.Modality != "Photons":
                set_progress("Waiting on user input...", percentage = -1)
                await_user_input(message=f"Change beam set {value['beamset_name']} in plan {value['plan_name']} to photons.  Then, click script play button to to continue.")
                        
    def _check_for_registrations_exist(self):
        """Check that Frame-of-Reference registrations exists for selected CTs"""
        _logger.info("Checking that Frame of Reference registrations exists...")
        errors = []
        _logger.debug("Retrieving FoR CT exam names...")
        for_ct_exam_names = {
            exam.Name: exam.EquipmentInfo.FrameOfReference
            for exam in self.pdu.case.Examinations
            }
        _logger.debug("Assigning target and reference CT exam names...")
        target_ct_exam_names = self._assign_target_ct_exam_names()
        ref_ct_exam_name = self.selected_values["ct_exam_name"]
        ref_for = for_ct_exam_names[ref_ct_exam_name]
        
        _logger.debug("Looping through each target CT exam to check for FoR regsitration...")
        if target_ct_exam_names:
            for target_ct_exam_name in target_ct_exam_names:
                _logger.debug("Inside _check_for_registrations_exist() first for-loop....")
                flag_reg = True
                if self.pdu.case.Registrations:
                    target_for = for_ct_exam_names[target_ct_exam_name]
                    for reg in self.pdu.case.Registrations:
                        _logger.debug("Inside _check_for_registrations_exist() second for-loop....")
                        if (
                                reg.ToFrameOfReference == ref_for 
                                and reg.FromFrameOfReference == target_for
                            ):
                            flag_reg = False
                            break
                if flag_reg:
                    errors.append(f"From: {target_ct_exam_name}  ->  To: {ref_ct_exam_name}") 
        
        if errors:
            exec_message = "Frame of Reference registrations missing."
            _logger.info(" Script ending: %s  %s", exec_message, errors)  
            message = "First, create Frame of Reference registrations for: \n\n"
            message += "\n" + "\n".join(set(errors))
            message += "\n\nThen, run the script again."
            exec_obj = ValueError(exec_message)
            self._prompt_user_acknowledge(exc=exec_obj, message=message)
            
        return errors
    
    def _deformable_registration(self):
        reference_ct_exam_name  = self.selected_values["ct_exam_name"]
        for target_ct_exam_name in self._assign_target_ct_exam_names():
            message = f"Calculating deformable registration: {target_ct_exam_name} -> {reference_ct_exam_name} ..."
            _logger.info(message)
            set_progress(message, percentage = -1)
            errors = []
            try:
                old_deformable_reg_names = self.pdu.get_deformable_registration_names()
                deformable_reg_name = self._get_new_deformable_name()
                self.pdu.case.PatientModel.CreateHybridDeformableRegistrationGroup(
                    RegistrationGroupName=deformable_reg_name, 
                    ReferenceExaminationName=reference_ct_exam_name, 
                    TargetExaminationNames=[target_ct_exam_name], 
                    ControllingRoiNames=[], 
                    ControllingPoiNames=[], 
                    FocusRoiNames=[], 
                    AlgorithmSettings=DeformableSettings.CorrelationCoefficient
                )
            except Exception as e:
                errors = ["Deformable registration failed. "]
                errors.append(
                    (
                        "Check the Target and Reference CTs and Frame of Reference fusion exists for:\n"
                        f"Target CT: {target_ct_exam_name}  ->  Reference CT: {reference_ct_exam_name}"
                    )
                )
                errors.append("\n\nScript will abort.")
                message = "\n\n".join(errors)
                self._prompt_user_acknowledge(exc=e, message=message)
                raise RuntimeError(str(e))
            
            new_deformable_reg_names = self.pdu.get_deformable_registration_names()
            new_reg_name = next(
                (n for n in new_deformable_reg_names if n not in old_deformable_reg_names), 
                None
            )
            
            _logger.debug("Old deformable registration names: %s", old_deformable_reg_names)
            _logger.debug("New deformable registration names: %s", new_deformable_reg_names)
            
            self.deformed_registration[target_ct_exam_name] = self.pdu.case.StructureRegistrations[new_reg_name]

    def _create_external_contour(self):
        message = "Creating External contour if needed..."
        _logger.info(message)
        set_progress(message, percentage = -1)
        
        plan_data = self.selected_values["plan_data"]
        ext_name = self.selected_values["external_info"]["name"]
        _logger.debug("Plan Data keys inside _create_external_contour(): %s", plan_data.keys())
        try:
            for key, value in plan_data.items():
                _logger.debug("value in plan_data[%s]: %s", key, value)
                ct_exam_name = value["ct_exam_name"]
                _logger.debug(
                    "CT exam name inside _create_external_contour() first for-loop: %s",
                    ct_exam_name,
                )
                for idx in range(len(self.selected_values["rois"]["roi_names"])):
                    roi_name = self.selected_values["rois"]["roi_names"][idx]
                    roi_has_contours = self.pdu.has_contours_on_ct(roi_name, ct_exam_name)
                    _logger.debug("ROI %s has contours: %s", roi_name, roi_has_contours)
                    if roi_name == ext_name and not roi_has_contours:
                        _logger.debug("Creating External contour on %s...", ct_exam_name)
                        ct_exam = self.pdu.case.Examinations[ct_exam_name]
                        self.pdu.case.PatientModel.RegionsOfInterest[ext_name].CreateExternalGeometry(
                            Examination=ct_exam, 
                            ThresholdLevel=self.external_threshold_level,
                        )
                        _logger.debug("Created External contour on %s", ct_exam_name)
        
        except Exception as e:
            _alert_physicist_error(e, message=__name__)
            msg_ext = "[FAILED] to create external.  Manually create an external contour on all exams you intend to use."
            _logger.error(msg_ext)
            set_progress("Script exiting...", percentage = -1)
            await_user_input(message=msg_ext)
            set_progress("Sending physicist notification...", percentage = -1)
            time.sleep(3)
            self._abort_script_error(exc=e, message=str(e))

    def _update_dose_statistics(self):
        _logger.info("Updating dose statistics...")
        try:
            for key, value in self.selected_values["plan_data"].items():
                value["beamset"].FractionDose.UpdateDoseGridStructures()
        except Exception as e:
            _logger.error("[FAILED] to update dose statistics in _update_dose_statistics(): %s", str(e))
            self._prompt_user_acknowledge(
                exc=e, 
                message="[FAILED] to update dose statistics.  Verify selected plans/doses contain dose."
            )
            raise RuntimeError(str(e)) 
    
    def _compute_eqd2(self):
        message = "Computing EQD2..."
        _logger.info(message)
        set_progress(message, percentage = -1)

        plan_data = self.selected_values["plan_data"]
        for key, value in plan_data.items():
            _logger.debug("In _compute_eqd2() first for-loop, key: value in plan_data - [%s]: %s", key, value)
            ct_exam_name = value["ct_exam_name"]
            rois, alpha_betas, priorities = [], [], []
            for idx in range(len(self.selected_values["rois"]["roi_names"])):
                roi_name = self.selected_values["rois"]["roi_names"][idx]
                roi_has_contours = self.pdu.has_contours_on_ct(roi_name, ct_exam_name)
                if roi_has_contours:
                    rois.append(self.pdu.case.PatientModel.RegionsOfInterest[roi_name])
                    alpha_betas.append(self.selected_values["rois"]["alpha_betas"][idx])
                    priorities.append(self.selected_values["rois"]["priorities"][idx])
            
            old_dose_eval_indices = self._get_dose_eval_indices()
            
            _logger.debug("Calculating EQD2 on Plan name: %s  ||  Beamset Name: %s", 
                          value["plan_name"], 
                          value["beamset_name"],
            )
            _logger.debug("ROIs: %s, Alpha/Betas: %s, Priorities: %s", rois, alpha_betas, priorities)
            
            value["beamset"].CreateEQD2Dose(Priorities=priorities, AlphaBetas=alpha_betas, Rois=rois)
            
            new_dose_eval_indices = self._get_dose_eval_indices()
            idx_exam, idx_eval = self._find_new_dose_indices(new_dose_eval_indices, old_dose_eval_indices)
            _logger.debug("idx_exam, idx_eval: %s, %s", idx_exam, idx_eval)
            
            self.eqd2[key] = (
                self.pdu.case.TreatmentDelivery
                .FractionEvaluations[0]
                .DoseOnExaminations[idx_exam]
                .DoseEvaluations[idx_eval]
            )
            _logger.debug("New EQD2 dose evaluation for %s: %s", key, self.eqd2[key])

        _logger.debug("EQD2 dose dictionary: %s", self.eqd2) 
            
    def _deform_dose(self):
        message = "Deforming doses..."
        _logger.info(message)
        set_progress(message, percentage = -1)

        for key in self.eqd2.keys():
            _logger.debug("Deforming dose for %s...", key)
            ct_exam_name = self.selected_values["plan_data"][key]["ct_exam_name"]
            _logger.debug("For dose %s, the CT used is %s.", key, ct_exam_name)
            if ct_exam_name == self.selected_values["ct_exam_name"]:
                _logger.debug(
                    "Skipping dose deformation on PlanName_BeamsetName %s. "
                    "Dose already resides on reference CT: %s",
                    key,
                    ct_exam_name,
                )
                self.deformed_doses[key] = self.eqd2[key]
            else:
                _logger.debug(
                    "Deformable registration used for dose deformation: %s",  
                    self.deformed_registration[ct_exam_name]
                )
                _logger.debug("Dose to be deformed: %s",  self.eqd2[key])
                old_dose_eval_indices = self._get_dose_eval_indices()
                
                self.pdu.case.MapDose(
                    FractionEvaluationIndex=0, 
                    DoseDistribution=self.eqd2[key], 
                    StructureRegistration=self.deformed_registration[ct_exam_name], 
                    ReferenceDoseGrid=None
                )
                
                _logger.debug("Dose successfully deformed...")
                
                new_dose_eval_indices = self._get_dose_eval_indices()
                idx_exam, idx_eval = self._find_new_dose_indices(new_dose_eval_indices, old_dose_eval_indices)
                _logger.info("idx_exam, idx_eval: %s, %s", idx_exam, idx_eval)
                
                self.deformed_doses[key] = (
                    self.pdu.case.TreatmentDelivery
                    .FractionEvaluations[0]
                    .DoseOnExaminations[idx_exam]
                    .DoseEvaluations[idx_eval]
                )
                
            _logger.debug("Deformed Doses dictionary: %s", self.deformed_doses)
                
    def _sum_dose(self):
        message = "Summing doses..."
        _logger.info(message)
        set_progress(message, percentage = -1)

        dose_evals = []
        weights = []    
        for key in self.deformed_doses.keys():
            _logger.debug("Current key in _sum_dose() for-loop: %s", key)
            dose_evals.append(self.deformed_doses[key])
            weights.append(self.selected_values["plan_data"][key]["fractions"])
        
        _logger.debug("Weights for Dose Sum: %s", weights)
        _logger.debug("Doses evaluations for Dose Sum: %s", dose_evals)
        sum_dose_name = self._get_sum_dose_name()
        
        self.pdu.case.CreateSummedDose(
            DoseName=sum_dose_name, 
            FractionNumber=0, 
            DoseDistributions=dose_evals, 
            Weights=weights
        )   
    
    def _create_sum_plan(self):
        """Create sum plan for evaluation clarity"""
        message = "Creating plan for evaluation..."
        _logger.info(message)
        set_progress(message, percentage = -1)
        
        plan_name_to_copy = None
        _logger.debug("Finding a plan to copy...")
        for plan_name in self.pdu.get_plan_names():
            if plan_name_to_copy:
                break
            for beamset_name in self.pdu.get_beamset_names_in_plan(plan_name):
                ct_exam_name = self.pdu.get_ct_exam_name_in_plan_beamset(plan_name, beamset_name)
                if (
                    ct_exam_name == self.selected_values["ct_exam_name"]
                    and self.pdu.has_dose_on_plan_beamset(plan_name, beamset_name)
                ):
                    _logger.debug("Found a plan to copy: %s", plan_name)
                    plan_name_to_copy = plan_name
                    break
            
        _logger.debug("Plan name to copy: %s", plan_name_to_copy)
        if plan_name_to_copy:
            _logger.debug("Creating copy of plan in _create_sum_plan()...")
            new_plan_name = self._get_new_plan_name()
            self.pdu.case.CopyPlan(
                PlanName=plan_name_to_copy, 
                NewPlanName=new_plan_name, 
                KeepBeamSetNames=False
            )
            
            set_progress("Saving...", percentage = -1)
            self.pdu.patient.Save()
            self.pdu.case.TreatmentPlans[new_plan_name].SetCurrent()
            
            _logger.debug(
                "Created sum plan for evaluation called %s on CT exam called %s", 
                plan_name,
                self.selected_values["ct_exam_name"]
            )
        else:
            message = "No beamset with dose exists on the selected reference CT. Creating sum plan will be skipped."
            _logger.info(message)
            self._prompt_user_acknowledge(exc=ValueError("No beamset with dose to copy"), message=message)

    
    # === Main loop ===
    def main(self):
        
        try:
            _logger.info("Set UI to Plan evaluation and Clinical goals...")
            SelectUIPlanEvalClinicalGoals(
                layout="DOSE 1_1", 
                layout_tab = "Layout2",
                tab_item="Doses",
            )
            
            values = EQD2SelectionWindow.main()
            if values is None:    
                _logger.debug("EQD2 UI returned no values. Script will be ended with empty return in main method.")
                return                          
            self.selected_values = values
            _logger.info("Selected Values: %s", self.selected_values)
            
            self._find_non_photon_plans()
            
            for_errors = self._check_for_registrations_exist()
            if for_errors:
                return
            
            self._create_external_contour()
            self._update_dose_statistics()
            
            self._deformable_registration()
            
            if self.selected_values["operation_mode"] != "dose_sum":
                self._compute_eqd2()
            else:
                for key, value in self.selected_values["plan_data"].items():
                    self.eqd2[key] = value["dose"]
            
            self._deform_dose()
            
            if self.selected_values["operation_mode"] != "eqd2":
                self._sum_dose()
            
            if self.selected_values["create_sum_plan"]:
                self._create_sum_plan()
         
        except Exception as e:
            _alert_physicist_error(e, message=__name__)
            _logger.error("[FAILED] in %s.  Email notification sent.  Exception: %s", __name__, str(e))
            set_progress("Waiting for user to hit play button...", percentage = -1)
            await_user_input(message="[FAILED] script.  Physicist alerted to address the issue.")
            set_progress("Sending physicist notification...", percentage = -1)
            time.sleep(3)
            self._abort_script_error(exc=e, message=str(e))
            


    