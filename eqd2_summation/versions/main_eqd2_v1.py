"""
RaystationScriptingPROD\EQD2_Summation\main_eqd2.py

Created on Thu Oct  2 15:17:42 2025

Automates an EQD2 dose summation


@author: clanco01
"""
from __future__ import annotations

# === DEBUG SETTINGS ===
DEBUG_THIS_MODULE = False
ALERT_PHYSICIST_ON_ALL_USES = True

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
from dataclasses import dataclass
from typing import Optional

# === Local imports ===
from RSutil.LogUtil.rs_logging import LOGGERS
from EQD2_Summation.ui_eqd2 import EQD2SelectionWindow
from RSutil.ErrorsUtil.error_dispatcher import DispatcherConfig
from RSutil.ErrorsUtil.rs_errors import report_error
from RSutil.ErrorsUtil.error_codes import PROMPT_USER, ALERT_PHYSICIST, ABORT_SCRIPT
from Breast_SIB.SelectUIPlanEvalClinicalGoals import SelectUIPlanEvalClinicalGoals

# === Setup Logger ===
_logger = LOGGERS["eqd2_summation"]


def _alert_physicist_error(
        exc: Exception, 
        metadata: Optional[dict] = None, 
        message: Optional[str] = None
):                                                  
    cfg = DispatcherConfig()
    cfg.alert_recipients = ["owen.clancey@nyulangone.org"]
    report_error(
            error_def=ALERT_PHYSICIST.SYSF_UNHANDLED_EXCEPTION, 
            original_exception=exc, 
            context={"module": "run_eqd2.py"},
            metadata=metadata,
            message=message,
            dispatcher_config=cfg,
        )

if ALERT_PHYSICIST_ON_ALL_USES:
    message = "Running main_eqd2.py...."
    e = RuntimeError("EQD2 script initialized.  Review patient data in logs and summation in Raystation.")
    _alert_physicist_error(e, message=message)


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
        self.eqd2 = {}
        self.deformed_registration = {}
        self.deformed_doses = {}
        try:
            self.case = get_current("Case")
            self.patient = get_current("Patient")
            self.beam_set_ct_names = self._get_beamset_ct_names()
        except Exception as e:
            self.case = None
            _logger.warning("get_current method failed to obtain Case: %s", e)
    
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
        report_error(
                error_def=ABORT_SCRIPT.DATA_REQUIRED_MISSING, 
                original_exception=exc, 
                context={"module": "main_eqd2.py"},
                metadata={},
                message=message,
            )
        raise RuntimeError("Script aborted...")

    
    # === Helper Functions ===
    def _get_deformable_reg_names(self):
        deformable_reg_names = []
        try:
            for sr in self.case.StructureRegistrations:
                deformable_reg_names.append(sr.Name)
        except Exception:
            pass
        
        return deformable_reg_names
    
    def _get_new_deformable_name(self):
        deformable_reg_names = self._get_deformable_reg_names()
        
        # Keep modifying the name until it's unique
        suffix = 1
        deform_reg_name = f"{self._base_name_reg}{suffix}_"
        while any(name.startswith(deform_reg_name) for name in deformable_reg_names):
            deform_reg_name = f"{self._base_name_reg}{suffix}_"
            suffix += 1
        
        return deform_reg_name
    
    def _get_dose_eval_names(self):
        dose_eval_names = []
        try:
            try:
                if not self.case.TreatmentDelivery.FractionEvaluations[0].DoseOnExaminations:
                    _logger.info("FractionEvaluations is empty in _get_dose_eval_names().  Returning dose_eval_names = []")
                    return dose_eval_names
            except Exception as e:
                _logger.info("FractionEvaluations does not exist in _get_dose_eval_names().  Returning dose_eval_names = []: %s", str(e))
                return dose_eval_names
            for dose_exam in self.case.TreatmentDelivery.FractionEvaluations[0].DoseOnExaminations:
                for dose_eval in dose_exam.DoseEvaluations:
                    dose_eval_names.append(dose_eval.Name)
            return dose_eval_names
        except Exception as e:
            _logger.error("[FAILED] try statement in _get_dose_eval_names(): %s", e)
        
        return dose_eval_names
    
    def _get_sum_dose_name(self):
        dose_eval_names = self._get_dose_eval_names()
        # Keep modifying the name until it's unique
        suffix = 1
        sum_dose_name = f"{self._base_name_sum}"
        while any(name.startswith(sum_dose_name) for name in dose_eval_names):
            sum_dose_name = f"{self._base_name_sum}{suffix}"
            suffix += 1
        
        return sum_dose_name
     
    def _get_plan_names(self):
        return [plan.Name for plan in self.case.TreatmentPlans]

    def _get_plan_name(self):
        plan_names = self._get_plan_names()
        # Keep modifying the name until it's unique
        suffix = 1
        plan_name = f"{self._base_name_plan}"
        while any(name.startswith(plan_name) for name in plan_names):
            plan_name = f"{self._base_name_plan}{suffix}"
            suffix += 1
        
        return plan_name
    
    def _get_dose_eval_indices(self):
        """Return mapping of DoseOnExaminations index → list of DoseEvaluations indices."""
        dose_eval_indices = {}
        try:
            try:
                if not self.case.TreatmentDelivery.FractionEvaluations[0].DoseOnExaminations:
                    _logger.info("FractionEvaluations is empty in _get_dose_eval_indices().  Returning dose_eval_indices = {}")
                    return dose_eval_indices
            except Exception as e:
                _logger.info("FractionEvaluations does not exist in _get_dose_eval_indices().  Returning dose_eval_indices = {}: %s", str(e))
                return dose_eval_indices
            for idx_exam, dose_on_exam in enumerate(
                self.case.TreatmentDelivery.FractionEvaluations[0].DoseOnExaminations
            ):
                try:
                    dose_eval_indices[idx_exam] = list(range(len(dose_on_exam.DoseEvaluations)))
                except Exception as e:
                    _logger.info("DoseOnExaminations is empty for %s: %s", idx_exam, e)
        except Exception as e:
            _logger.error("[FAILED] try statement in _get_dose_eval_indices(): %s", e)
        
        return dose_eval_indices
    
    def _find_new_dose_indices(self, new_dose_eval_indices, old_dose_eval_indices):
        idx_exam = idx_eval = None
        try:
            for exam_idx, eval_list in new_dose_eval_indices.items():
                old_list = old_dose_eval_indices.get(exam_idx, [])
                # find any new eval index in this exam
                new_indices = [i for i in eval_list if i not in old_list]
                if new_indices:
                    idx_exam = exam_idx
                    idx_eval = new_indices[0]
                    break
        except Exception as e:
            _logger.error("[FAILED] try statement in _find_new_dose_indices(): %s", e)
        return idx_exam, idx_eval 
    
    def _get_beamset_ct_names(self):
        """ Returns mapping (dict) of each beamset name (str) -> CT name used in the beamset (str)"""
        exam_for_names = {}
        for exam in self.case.Examinations:
            exam_for_names[exam.EquipmentInfo.FrameOfReference] = exam.Name

        bs_ct_names = {}
        for plan in self.case.TreatmentPlans:
            for beam_set in plan.BeamSets:
                bs_ct_names[beam_set.DicomPlanLabel] = exam_for_names[beam_set.FrameOfReference]
                
        return bs_ct_names
    
    def _assign_target_ct_names(self):
        target_ct_names = []
        for key in self.selected_values["plan_data"].keys():
            ct_name = self.beam_set_ct_names[key]
            if ct_name != self.selected_values["ct_name"]:
                target_ct_names.append(ct_name)
        return target_ct_names

    # === Main Methods ===
        
    def _find_non_photon_plans(self):
        try:
            for name in self.selected_values["plan_data"].keys():
                for plan in self.case.TreatmentPlans:
                    for beam_set in plan.BeamSets:
                        while name == beam_set.DicomPlanLabel and beam_set.Modality != "Photons":
                            set_progress("Waiting on user input...", percentage = -1)
                            await_user_input(message=f"Change beam set {beam_set.DicomPlanLabel} in plan {plan.Name} to photons.  Then, click script play button to to continue.")
                            
        except Exception as e:
            _logger.info("User trying to change to photon plan.  Review for upgrades: %s", e)
            
    def _check_for_registrations_exist(self):
        """Check that Frame-of-Reference registrations exists for selected CTs"""
        _logger.info("Checking that Frame of Reference registrations exists...")
        errors = []
        for_ct_names = {
            exam.Name: exam.EquipmentInfo.FrameOfReference
            for exam in self.case.Examinations
            }
        target_ct_names = self._assign_target_ct_names()
        ref_ct_name = self.selected_values["ct_name"]
        ref_for = for_ct_names[ref_ct_name]
        
        if target_ct_names:
            for target_ct_name in target_ct_names:
                flag_reg = True
                if self.case.Registrations:
                    target_for = for_ct_names[target_ct_name]
                    for reg in self.case.Registrations:
                        if (
                                reg.ToFrameOfReference == ref_for 
                                and reg.FromFrameOfReference == target_for
                            ):
                            flag_reg = False
                            break
                if flag_reg:
                    errors.append(f"From: {target_ct_name}  ->  To: {ref_ct_name}") 
        
        if errors:
            exec_message = "Frame of Reference registrations missing."
            _logger.info("%s  %s", exec_message, errors)  
            message = "First, create Frame of Reference registrations for: \n\n"
            message += "\n".join(errors)
            message += "\n\nThen, run the script again."
            exec_obj = ValueError(exec_message)
            self._prompt_user_acknowledge(exc=exec_obj, message=message)
            _logger.info("Script aborting...")
          
        return errors
    
    def _deformable_registration(self):
        reference_ct_name  = self.selected_values["ct_name"]
        for target_ct_name in self._assign_target_ct_names():
            message = f"Calculating deformable registration: {target_ct_name} -> {reference_ct_name} ..."
            _logger.info(message)
            set_progress(message, percentage = -1)
            errors = []
            try:
                old_deformable_reg_names = self._get_deformable_reg_names()
                deformable_reg_name = self._get_new_deformable_name()
                self.case.PatientModel.CreateHybridDeformableRegistrationGroup(
                    RegistrationGroupName=deformable_reg_name, 
                    ReferenceExaminationName=reference_ct_name, 
                    TargetExaminationNames=[target_ct_name], 
                    ControllingRoiNames=[], 
                    ControllingPoiNames=[], 
                    FocusRoiNames=[], 
                    AlgorithmSettings=DeformableSettings.CorrelationCoefficient
                )
            except Exception as e:
                exec_obj = e
                errors = ["Deformable registration failed. "]
                errors.append("Check the Target and Reference CTs and Frame of Reference fusion exists for:\n")
                errors.append(f"Target CT: {target_ct_name}  ->  Reference CT: {reference_ct_name}")
                errors.append("\n\nScript will abort.")
                message = "\n\n".join(errors)
                self._prompt_user_acknowledge(exc=exec_obj, message=message)
                self._abort_script_error(exc=e, message=message)
            
            new_deformable_reg_names = self._get_deformable_reg_names()
            new_reg_name = next((n for n in new_deformable_reg_names if n not in old_deformable_reg_names), None)
            
            _logger.info("Old deformable registration names: %s", old_deformable_reg_names)
            _logger.info("New deformable registration names: %s", new_deformable_reg_names)
            
            self.deformed_registration[target_ct_name] = self.case.StructureRegistrations[new_reg_name]

    def _create_external_contour(self):
        message = "Creating External contour if needed..."
        _logger.info(message)
        set_progress(message, percentage = -1)
        try:
            plan_data = self.selected_values["plan_data"]
            ext_name = self.selected_values["external_info"]["name"]
            for dose_name in plan_data.keys():
                ct_name = self.beam_set_ct_names[dose_name]
                for idx in range(len(self.selected_values["rois"]["roi_names"])):
                    roi_name = self.selected_values["rois"]["roi_names"][idx]
                    roi = self.case.PatientModel.StructureSets[ct_name].RoiGeometries[roi_name]
                    if roi_name == ext_name and not roi.HasContours():
                        _logger.info("Creating External contour on %s...", ct_name)
                        ct_exam = self.case.Examinations[ct_name]
                        self.case.PatientModel.RegionsOfInterest[ext_name].CreateExternalGeometry(
                            Examination=ct_exam, 
                            ThresholdLevel=-250,
                        )
                        _logger.info("Created External contour on %s", ct_name)
        except Exception as e:
            msg = "Failed in _create_external_contour()"
            _logger.error(msg)
            self._abort_script_error(exc=e, message=msg)

    def _update_dose_statistics(self):
        _logger.info("Updating dose statistics...")
        try:
            for key in self.selected_values["plan_data"].keys():
                self.case.TreatmentPlans[self.selected_values["plan_data"][key]["plan_name"]].BeamSets[self.selected_values["plan_data"][key]["beamset_name"]].FractionDose.UpdateDoseGridStructures()
        except Exception:
            message = "[FAILED] to update dose statistics."
            _logger.error(message)
    
    def _compute_eqd2(self):
        message = "Computing EQD2..."
        _logger.info(message)
        set_progress(message, percentage = -1)
        try:
            plan_data = self.selected_values["plan_data"]
            for dose_name in plan_data.keys():
                ct_name = self.beam_set_ct_names[dose_name]
                rois, alpha_betas, priorities = [], [], []
                for idx in range(len(self.selected_values["rois"]["roi_names"])):
                    roi_name = self.selected_values["rois"]["roi_names"][idx]
                    roi = self.case.PatientModel.StructureSets[ct_name].RoiGeometries[roi_name]
                    if roi.HasContours():
                        rois.append(self.case.PatientModel.RegionsOfInterest[roi_name])
                        alpha_betas.append(self.selected_values["rois"]["alpha_betas"][idx])
                        priorities.append(self.selected_values["rois"]["priorities"][idx])
                
                plan_name = plan_data[dose_name]["plan_name"]
                beamset_name = plan_data[dose_name]["beamset_name"]
                
                old_dose_eval_indices = self._get_dose_eval_indices()
                
                _logger.info("Calculating EQD2 on Plan name: %s  ||  Beamset Name: %s", plan_name, beamset_name )
                self.case.TreatmentPlans[plan_name].BeamSets[beamset_name].CreateEQD2Dose(
                    Priorities=priorities, 
                    AlphaBetas=alpha_betas, 
                    Rois=rois
                )
                
                new_dose_eval_indices = self._get_dose_eval_indices()
                idx_exam, idx_eval = self._find_new_dose_indices(new_dose_eval_indices, old_dose_eval_indices)
                _logger.info("idx_exam, idx_eval: %s, %s", idx_exam, idx_eval)
                
                # --- Retrieve the new DoseEvaluation ---
                try:
                    self.eqd2[dose_name] = (
                        self.case.TreatmentDelivery
                        .FractionEvaluations[0]
                        .DoseOnExaminations[idx_exam]
                        .DoseEvaluations[idx_eval]
                    )
                except Exception as e:
                    _logger.error("Could not locate the new EQD2 DoseEvaluation: %s", e)
                    
        except Exception as e:
            message = "[FAILED] to compute EQD2 dose in _compute_eqd2()"
            _logger.error(message)
            self._abort_script_error(exc=e, message=message)
            
             
    def _deform_dose(self):
        message = "Deforming doses..."
        _logger.info(message)
        set_progress(message, percentage = -1)
        try:
            for key in self.eqd2.keys():
                ct_name = self.beam_set_ct_names[key]
                if ct_name == self.selected_values["ct_name"]:
                    self.deformed_doses[key] = self.eqd2[key]
                else:
                    old_dose_eval_indices = self._get_dose_eval_indices()
                    self.case.MapDose(
                        FractionEvaluationIndex=0, 
                        DoseDistribution=self.eqd2[key], 
                        StructureRegistration=self.deformed_registration[ct_name], 
                        ReferenceDoseGrid=None
                    )
                    new_dose_eval_indices = self._get_dose_eval_indices()
                    idx_exam, idx_eval = self._find_new_dose_indices(new_dose_eval_indices, old_dose_eval_indices)
                    self.deformed_doses[key] = self.case.TreatmentDelivery.FractionEvaluations[0].DoseOnExaminations[idx_exam].DoseEvaluations[idx_eval]
        
        except Exception as e:
            message = "[FAILED] to deform dose in _deform_dose()"
            _logger.error(message)
            self._abort_script_error(exc=e, message=message)            
    
    def _sum_dose(self):
        message = "Summing doses..."
        _logger.info(message)
        set_progress(message, percentage = -1)
        try:
            dose_evals = []
            weights = []    
            for key in self.deformed_doses.keys():
                dose_evals.append(self.deformed_doses[key])
                weights.append(self.selected_values["plan_data"][key]["fractions"])
            
            _logger.info("Weights for Dose Sum: %s", weights)
            
            sum_dose_name = self._get_sum_dose_name()
            
            self.case.CreateSummedDose(
                DoseName=sum_dose_name, 
                FractionNumber=0, 
                DoseDistributions=dose_evals, 
                Weights=weights
            )
        except Exception as e:
            message = "[FAILED] to sum dose in _sum_dose()"
            _logger.error(message)
            self._abort_script_error(exc=e, message=message)  
    
    def _create_sum_plan(self):
        """Create sum plan for evaluation clarity"""
        message = "Creating plan for evaluation..."
        _logger.info(message)
        set_progress(message, percentage = -1)
        
        try: 
            plan_name = self._get_plan_name()
            self.case.AddNewPlan(
                PlanName=plan_name, 
                PlannedBy="", 
                Comment="", 
                ExaminationName=self.selected_values["ct_name"], 
                IsMedicalOncologyPlan=False, 
                AllowDuplicateNames=False,
            )
            
            set_progress("Saving...", percentage = -1)
            self.patient.Save()
            self.case.TreatmentPlans[plan_name].SetCurrent()
            
            _logger.info(
                "Created sum plan for evaluation called %s on CT exam called %s", 
                plan_name,
                self.selected_values["ct_name"]
            )
        except Exception as e:
            _logger.error("[FAILED] to create dummy sum plan in _create_sum_plan(): %s", str(e))
    
    # === Main loop ===
    def main(self):
        
        SelectUIPlanEvalClinicalGoals(
            layout="DOSE 1_1", 
            layout_tab = "Layout2",
            tab_item="Doses",
        )
        _logger.info("Set UI to Plan evaluation and Clinical goals...")
        
        values = EQD2SelectionWindow.main()
        if values is None:    
            _logger.info("EQD2 UI canceled by user.")
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
            
        

# === RUN LOCALLY FOR DEBUGGING ===
if __name__ == "__main__" and DEBUG_THIS_MODULE:
    debug_logger = LOGGERS["debug"]
    