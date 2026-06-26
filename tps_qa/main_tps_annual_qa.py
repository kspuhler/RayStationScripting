"""
main_tps_annual_qa

Created on Mon Nov  3 08:30:52 2025

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
import os
from datetime import datetime
from typing import Any

# === Local imports ===
from RSutil.patient_data_util import PatientDataUtil
from RSutil.LogUtil.rs_logging import LOGGERS, set_logger_mode
from RSutil.ErrorsUtil.error_dispatcher import DispatcherConfig
from RSutil.ErrorsUtil.rs_errors import report_error
from RSutil.ErrorsUtil.error_codes import PROMPT_USER, ALERT_PHYSICIST, ABORT_SCRIPT, SKIP_STEP
from DicomExport.TPSExport import TPSExport
from create_export_qa_plan.main_create_export_qa_plan import CreateExportQAPlan
from auto_fusion.main_auto_fusion import AutoFusion
from RSutil.open_patient_case_and_plan import open_patient_case_and_plan

# === Setup Logger ===
_logger = LOGGERS["tps_qa"]
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
                context={"module": "main_tps_annual_qa.py"},
                metadata=metadata,
                message=message,
                dispatcher_config=cfg,
            )

if _ALERT_PHYSICIST_ON_ALL_USES:
    message = "Running main_tps_annual_qa.py...."
    e = RuntimeError("INFO ONLY - TPS Annual QA initialized.  Review patient data in logs and summation in Raystation.")
    _alert_physicist_error(e, message=message)



class TPSAnnualQA():
    
    def __init__(
            self, 
            root_dir: str = r"\\Client\F$\SHARING\Radiation Oncology Physics\TPS Annual QA\RayStation TPS Annual",
            data_dir_ext: str = "tps_data",
            save_dir_ext: str = str(datetime.now().year)
    ) -> None:
        set_progress("Initializing...", percentage = -1)
        _logger.info("Initializing object of TPSAnnualQA...")
        
        # === Base plan patient info ===
        self.base_mrn = "0000BASE"
        self.base_case = "Baseline"
        
        # === Path and directories ===
        self.year = str(datetime.now().year)
        self.case_name = self.year
        _logger.debug("Current year: %s", self.year)
        
        self.data_dir = os.path.join(root_dir, data_dir_ext)
        _logger.info("Data Directory: %s", self.data_dir)
        self.manual_import = False
        if not os.path.exists(self.data_dir):
            _logger.warning("Data directory does not exist.  Manual import set to true.")
            self.manual_import = True
        
        self.save_dir = os.path.join(root_dir, save_dir_ext)
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
            _logger.info("Created folder: %s", self.save_dir)
        else:
            _logger.info("Save Data folder already exists: %s", self.save_dir)
        
        # === Geometry and Fields config ===
        self.imaging_system_name = "CT Sim 264"
        self.voxel_size = {"x": 0.25, "y": 0.25, "z": 0.25}
        self.external_name = "External"
        self.dvh_dose_ct_exam_name = "Water"
        self.dvh_dose_body_name = "Body"
        self.box_name = "Box_Around_Center"
        self.hu_minus_250_name = "HU_minus_250"
        self.ptv_name = "PTV"
        self.gtv_name = "GTV"
        self.dvh_dose_ptv_name = "PTV_DVH"
        self.external_threshold = -250
        self.center_coord_external: dict[str, float] | None = None
        self.ct_exam: Any | None = None
        self.ct_exam_name = "Geometry"
        self.geometry_plan_name = "Geometry"
        self.machine_name = "TrueBeamSN1106"
        self.gantry_angles = [0, 90, 270]
        self.plan: Any | None = None
        self.beamset: Any | None = None
        
        # === DVH and Dose Display config ===
        self.dvh_dose_plan_name = "DVHandDose"
        self.roi_100cGy_name = "100cGy"
        self.roi_100cGy: Any | None = None
        self.roi_100cGy_threshold = 100
        self.clinical_goals_template_name = "TPS_Annual"
        
        # === Create and Export QA plan config ===
        self.flag_for_user_questions = False
        self.plans_names_to_skip = [self.dvh_dose_plan_name, self.geometry_plan_name]
        
        # === Error tracking ===
        self.errors = []
        
        _logger.debug("Finished initalization...")

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
                context={"module": "main_tps_annual_qa.py"},
                metadata={},
                message=message,
            )
    
    def _skipping_step_error(
            self, 
            exc: Exception, 
            metadata: dict | None = None, 
            message: str | None = None
    ):                                                  
        report_error(
                error_def=SKIP_STEP.SYSF_UNHANDLED_EXCEPTION, 
                original_exception=exc, 
                context={"module": "main_tps_annual_qa.py"},
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
                context={"module": "main_tps_annual_qa.py"},
                metadata={},
                message=message,
            )
        raise RuntimeError(str(exc))
    
    # === Helper methods ===    
    def _iter_plan_beamsets(self) -> tuple[str, Any, str]:
        """Yield all beamsets across all plans in the patient."""
        for plan_name in self.pdu.get_plan_names():
            for beamset in self.pdu.get_beamsets_in_plan(plan_name):
                beamset_name = getattr(beamset, "DicomPlanLabel", getattr(beamset, "Name", "<unknown>"))
                yield plan_name, beamset, beamset_name

    # === Worker methods ===
    def _set_imaging_system(self) -> None:
        """ Set CT Imaging system and name"""
        msg = "Setting all CTs to default CT..."
        _logger.info(msg)
        set_progress(msg, percentage = -1)
        try:
            for exam in self.pdu.get_ct_exams():
                try:
                    exam.EquipmentInfo.SetImagingSystemReference(ImagingSystemName=self.imaging_system_name)
                except Exception:
                    self.errors.append(f"Failed to set imaging system for {exam.Name}")
            
        except Exception as e:
            _logger.error("[FAILED] to set CT imaging system: %s", str(e))
            self.errors.append("Failed to set imaging system.")
            self._skipping_step_error(exc=e, metadata={"method": "_set_imaging_system"})
    
    def _create_external(self) -> None:
        msg = "Creating External structure..."
        _logger.info(msg)
        set_progress(msg, percentage = -1)
        external_name = self.pdu.get_roi_external_name()
        try:
            self.pdu.patient_model.RegionsOfInterest[external_name].Name = self.external_name
            for ct_exam in self.pdu.get_ct_exams():
                ct_exam_name = self.pdu.get_exam_name_from_exam(ct_exam)
                _logger.debug("Current CT in _create_external: %s", ct_exam_name)
                if not self.pdu.has_roi_external_contour_on_ct(ct_exam_name):
                    _logger.debug("Creating external on %s...", ct_exam_name)
                    self.pdu.patient_model.RegionsOfInterest[self.external_name].CreateExternalGeometry(
                        Examination=ct_exam, 
                        ThresholdLevel=self.external_threshold
                    )
        
        except Exception as e:
            _logger.error("[FAILED] to create external contour.")
            self.errors.append("Failed to create external.")
            self._skipping_step_error(exc=e, metadata={"method": "_create_external"})

    def _copy_body_to_external(self):
        msg = "Copying Body to External structure for Water CT..."
        _logger.info(msg)
        set_progress(msg, percentage = -1)
        try:
            ct_exam = self.pdu.get_exam_with_exam_name(self.dvh_dose_ct_exam_name)
            dvh_dose_ext = self.pdu.patient_model.RegionsOfInterest[self.external_name].SetAlgebraExpression(
                ExpressionA={ 
                    'Operation': "Union", 
                    'SourceRoiNames': [self.dvh_dose_body_name], 
                    'MarginSettings': { 
                        'Type': "Expand", 
                        'Superior': 0, 
                        'Inferior': 0, 
                        'Anterior': 0, 
                        'Posterior': 0, 
                        'Right': 0, 
                        'Left': 0 
                    } 
                }, 
                ExpressionB={ 
                    'Operation': "Union", 
                    'SourceRoiNames': [], 
                    'MarginSettings': { 
                        'Type': "Expand", 
                        'Superior': 0, 
                        'Inferior': 0, 
                        'Anterior': 0, 
                        'Posterior': 0, 
                        'Right': 0, 
                        'Left': 0 
                    } 
                }, 
                ResultOperation="None", 
                ResultMarginSettings={ 
                    'Type': "Expand", 
                    'Superior': 0, 
                    'Inferior': 0, 
                    'Anterior': 0, 
                    'Posterior': 0, 
                    'Right': 0, 
                    'Left': 0 
                }
            )
            dvh_dose_ext.UpdateDerivedGeometry(Examination=ct_exam, Algorithm="Auto")
        except Exception:
            msg_ext = "[FAILED] to create external contour on for DVHandDose plan."
            _logger.error(msg_ext)
            self.errors.append(msg_ext) 
    
    def _roi_geometry(self) -> tuple[float, float]:
        msg = "Creating ROI geometry..."
        _logger.info(msg)
        set_progress(msg, percentage = -1)
        gtv_vol, ptv_vol = None, None
        try:
            box_roi = self.pdu.patient_model.CreateRoi(
                Name=self.box_name, 
                Color="Blue", 
                Type="Control", 
                TissueName=None, 
                RbeCellTypeName=None, 
                RoiMaterial=None
            )
    
            box_roi.CreateBoxGeometry(
                Size={ 'x': 3, 'y': 3, 'z': 3 }, 
                Examination=self.ct_exam, 
                Center=self.center_coord_external, 
                Representation="TriangleMesh", 
                VoxelSize=None
            )
    
            hu_minus_250 = self.pdu.patient_model.CreateRoi(
                Name=self.hu_minus_250_name, 
                Color="SaddleBrown", 
                Type="Control", 
                TissueName=None, 
                RbeCellTypeName=None, 
                RoiMaterial=None
            )
    
            hu_minus_250.GrayLevelThreshold(
                Examination=self.ct_exam, 
                LowThreshold=-3024, 
                HighThreshold=self.external_threshold, 
                PetUnit="", 
                CbctUnit=None, 
                BoundingBox=None
            )
    
            gtv_roi = self.pdu.patient_model.CreateRoi(
                Name=self.gtv_name, 
                Color="Blue", 
                Type="Gtv", 
                TissueName=None, 
                RbeCellTypeName=None, 
                RoiMaterial=None
            )
    
            gtv_roi.SetAlgebraExpression(
                ExpressionA={ 
                    'Operation': "Union", 
                    'SourceRoiNames': [self.hu_minus_250_name], 
                    'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } 
                }, 
                ExpressionB={ 
                    'Operation': "Union", 
                    'SourceRoiNames': [self.box_name], 
                    'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } 
                }, 
                ResultOperation="Intersection", 
                ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 }
            )
    
            gtv_roi.UpdateDerivedGeometry(Examination=self.ct_exam, Algorithm="Auto")
    
            ptv_roi = self.pdu.patient_model.CreateRoi(
                  Name=self.ptv_name, 
                  Color="Pink", 
                  Type="Ptv", 
                  TissueName=None, 
                  RbeCellTypeName=None, 
                  RoiMaterial=None
              )
    
            ptv_roi.SetAlgebraExpression(
                ExpressionA={ 
                    'Operation': "Union", 
                    'SourceRoiNames': [self.gtv_name], 
                    'MarginSettings': { 'Type': "Expand", 'Superior': 1, 'Inferior': 1, 'Anterior': 1, 'Posterior': 1, 'Right': 1, 'Left': 1 } 
                }, 
                ExpressionB={ 
                    'Operation': "Union", 
                    'SourceRoiNames': [], 
                    'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } 
                }, 
                ResultOperation="None", 
                ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })
    
            ptv_roi.UpdateDerivedGeometry(Examination=self.ct_exam, Algorithm="Auto")
            
            gtv_vol = round(self.pdu.get_volume_of_roi_on_ct(self.gtv_name, self.ct_exam_name), 2)
            ptv_vol = round(self.pdu.get_volume_of_roi_on_ct(self.ptv_name, self.ct_exam_name), 2)
        
        except Exception as e:
            _logger.error("[FAILED] in _roi_geometry: %s", str(e))
            self.errors.append("Failed to compute roi geometry.")
            self._skipping_step_error(exc=e, metadata={"method": "_roi_geometry"})
        
        return gtv_vol, ptv_vol

    def _field_geometry(self) -> tuple(dict[str, float], dict[str, dict[str, float]]):
        msg = "Creating field geometry..."
        _logger.info(msg)
        set_progress(msg, percentage = -1)
        ssd_dict = {}
        jaws_dict = {}
        try:
            self.plan = self.pdu.case.AddNewPlan(
                PlanName=self.geometry_plan_name, 
                PlannedBy="", 
                Comment="", 
                ExaminationName=self.ct_exam_name, 
                IsMedicalOncologyPlan=False, 
                AllowDuplicateNames=False
            )
    
            self.beamset = self.plan.AddNewBeamSet(
                Name=self.geometry_plan_name, 
                ExaminationName=self.ct_exam_name, 
                MachineName=self.machine_name, 
                Modality="Photons", 
                TreatmentTechnique="Conformal", 
                PatientPosition="HeadFirstSupine", 
                NumberOfFractions=1, 
                CreateSetupBeams=False, 
                UseLocalizationPointAsSetupIsocenter=False, 
                UseUserSelectedIsocenterSetupIsocenter=False, 
                Comment="", 
                RbeModelName=None, 
                EnableDynamicTrackingForVero=False, 
                NewDoseSpecificationPointNames=[], 
                NewDoseSpecificationPoints=[], 
                MotionSynchronizationTechniqueSettings={ 
                    'DisplayName': None, 
                    'MotionSynchronizationSettings': None, 
                    'RespiratoryIntervalTime': None, 
                    'RespiratoryPhaseGatingDutyCycleTimePercentage': None, 
                    'MotionSynchronizationTechniqueType': "Undefined" 
                }, 
                Custom=None, 
                ToleranceTableLabel="3D PLAN"
            )
            
            self.beamset.SetJawSetback(JawSetback=False)
            field_name = f"G{self.gantry_angles[0]}"
            self.beamset.CreatePhotonBeam(
                BeamQualityId="6", 
                CyberKnifeCollimationType="Undefined", 
                CyberKnifeNodeSetName=None, 
                CyberKnifeRampVersion=None, 
                CyberKnifeAllowIncreasedPitchCorrection=None, 
                GimbalPanAngle=0, 
                GimbalTiltAngle=0, 
                IsocenterData={ 
                    'Position': self.center_coord_gtv, 
                    'NameOfIsocenterToRef': "", 
                    'Name': "Geometry 1", 
                    'Color': "98, 184, 234" 
                }, 
                Name=field_name, 
                Description="", 
                GantryAngle=self.gantry_angles[0], 
                CouchRotationAngle=0, 
                CouchPitchAngle=0, 
                CouchRollAngle=0, 
                CollimatorAngle=0
            )
            
            self.beamset.SelectToUseROIasTreatOrProtectForAllBeams(RoiName=self.gtv_name)
            
            self.beamset.Beams[field_name].SetTreatAndProtectMarginsForBeam(
                TopMargin=0,
                BottomMargin=0,
                LeftMargin=0,
                RightMargin=0,
                Roi=self.gtv_name,
            )
            
            self.beamset.Beams[field_name].ConformMlc()
            
            for i in range(1, 3, 1):
                self.beamset.CopyBeam(BeamName=field_name)
                angle = self.gantry_angles[i]
                field_name = f"G{angle}"
                self.beamset.Beams[i].Name = field_name
                self.beamset.Beams[field_name].GantryAngle = angle
                self.beamset.Beams[field_name].ConformMlc()
            
            _logger.debug("X1: -%s", self.beamset.Beams[field_name].Segments[0].JawPositions[0])
            _logger.debug("X1: %s", -self.beamset.Beams[field_name].Segments[0].JawPositions[0])
            
            for angle in self.gantry_angles:
                beam_name = f"G{angle}"
            
                jaws_dict[angle] = {
                    "X1": round(-self.beamset.Beams[beam_name].Segments[0].JawPositions[0], 2),
                    "X2": round(self.beamset.Beams[beam_name].Segments[0].JawPositions[1], 2),
                    "Y1": round(-self.beamset.Beams[beam_name].Segments[0].JawPositions[2], 2),
                    "Y2": round(self.beamset.Beams[beam_name].Segments[0].JawPositions[3], 2),
                }
                ssd_dict[angle] = round(self.beamset.Beams[beam_name].GetSSD(), 2)
            
        except Exception as e:
            _logger.error("[FAILED] in _field_geometry")
            self.errors.append("Failed to compute field geometry.")
            self._skipping_step_error(exc=e, metadata={"method": "_field_geometry"})
        
        return ssd_dict, jaws_dict

    def _check_for_deprecated_machines(self) -> None:
        """ DOC STRING"""
        msg = "Checking for deprecated machines..."
        _logger.info(msg)
        set_progress(msg, percentage = -1)
        try:
            all_plan_data = self.pdu.get_all_plan_data()
            _logger.debug("All Plan Data: %s", all_plan_data)
            for plan, plan_info in all_plan_data.items():
                _logger.debug("Plan Data: %s", plan_info)
                for beamset, beamset_info in plan_info.items():
                    comm_flag = False
                    _logger.debug("Beamset Info: %s", beamset_info)
                    while not comm_flag:
                        
                        machine_name = beamset_info["machine"]
                        comm_time = beamset_info["beamset"].MachineReference.CommissioningTime
                        _logger.debug("Machine and Commissioned Time: %s - %s", machine_name, comm_time)
                        
                        machine_db = get_current("MachineDB")
                        machine = machine_db.QueryCommissionedMachineInfo(Filter={'Name': machine_name})
                        
                        if comm_time == machine[0]["CommissionTime"]:
                            _logger.debug(f"{machine_name} is commissioned")
                            comm_flag = True
                        else:
                            await_user_input(message=f"Update machine in plan - beamset: {beamset['plan_name']} - {beamset['beamset_name']}")
        except Exception as e:
            _logger.error("[FAILED] to check for deprecated machines in _check_for_deprecated_machines(): %s", str(e))
            await_user_input(message="Change any deprecated machines to commissioned machines.")

    def _delete_dose_to_all_beamsets(self) -> None:
        _logger.info("Deleting dose to all beamsets...")
        for plan_name, beamset, beamset_name in self._iter_plan_beamsets(): 
            try:
                dose_grid = beamset.GetDoseGrid()
                dose_grid.Corner.x += self.voxel_size["x"]  
                beamset.SetDefaultDoseGrid(VoxelSize=self.voxel_size)
                beamset.FractionDose.UpdateDoseGridStructures()
                
            except Exception as e:
                _logger.warning(
                    "[WARNING] in _delete_dose_to_all_beamsets for %s - %s",
                    plan_name,
                    beamset_name,
                )
                self.errors.append(
                    f"Failed to delete beamset dose in Plan || Beamset: {plan_name} || {beamset_name}"
                )
                self._skipping_step_error(exc=e, metadata={"method": "_delete_dose_to_all_beamsets"})

    def _compute_dose_for_all_beamsets(self) -> None:
        """DOC STRING"""
        msg = "Calculating dose for all beamsets..."
        _logger.info(msg)
        set_progress(msg, percentage = -1)
        for plan_name, beamset, beamset_name in self._iter_plan_beamsets():
            try:
                _logger.info(f"Computing dose to {plan_name} - {beamset_name}")
                set_progress(f"Computing dose to {plan_name} - {beamset_name}", percentage = -1)
                beamset.SetDefaultDoseGrid(VoxelSize=self.voxel_size)
                beamset.ComputeDose(
                    ComputeBeamDoses=True, 
                    DoseAlgorithm="CCDose", 
                    ForceRecompute=False, 
                    RunEntryValidation=True
                )
            except Exception as e:
                _logger.error(
                    "[FAILED] in _compute_dose_for_all_beamsets for %s - %s", 
                    plan_name, 
                    beamset_name,
                    )
                self.errors.append(
                    f"Failed to compute dose on Plan || Beamset: {plan_name} || {beamset_name}"
                )
                self._skipping_step_error(exc=e, metadata={"method": "_compute_dose_for_all_beamsets"})
            
    def _export_plans(self) -> None:
        """ DOC STRING"""
        plans = self.pdu.get_plans()
        for plan_name, beamset, beamset_name in self._iter_plan_beamsets():
            if plan_name in self.plans_names_to_skip:
                continue
            try:
                _logger.info(f"Exporting: {plan_name} - {beamset_name}")
                set_progress(f"Exporting: {plan_name} - {beamset_name}", percentage = -1)       
                plan = next((p for p in plans if getattr(p, "Name", None) == plan_name), None)
                plan.SetCurrent()
                beamset.SetCurrent()
                TPSExport()
            except Exception as e:
                _logger.error(
                    "[FAILED] in _export_plans for %s - %s", 
                    plan_name, 
                    beamset_name,
                )
                self.errors.append(
                    f"Failed to export plans on Plan || Beamset: {plan_name} || {beamset_name}"
                )
                self._skipping_step_error(exc=e, metadata={"method": "_export_plans"})
                    
    def _create_and_export_qa_plans(self) -> None:
        """ DOC STRING"""
        plans = self.pdu.get_plans()
        for plan_name, beamset, beamset_name in self._iter_plan_beamsets():
            if plan_name in self.plans_names_to_skip:
                continue
            try:
                _logger.info(f"Creating and Exporting QA plan: {plan_name} - {beamset_name}")
                set_progress(f"Creating and Exporting QA plan: {plan_name} - {beamset_name}", percentage = -1)
                plan = next((p for p in plans if getattr(p, "Name", None) == plan_name), None)
                plan.SetCurrent()
                beamset.SetCurrent()
                qa_plan = CreateExportQAPlan(
                    path=self.save_dir, 
                    flag_for_user_questions=self.flag_for_user_questions
                )
                qa_plan.main()
            except Exception as e:
                _logger.error(
                    "[FAILED] in _create_qa_plans for %s - %s", 
                    plan_name, 
                    beamset_name,
                )
                self.errors.append(
                    f"Failed to export QA plans on Plan || Beamset: {plan_name} || {beamset_name}"
                )
                self._skipping_step_error(exc=e, metadata={"method": "_create_and_export_qa_plans"})

    def main(self) -> None:
        try:
            _logger.info("Inside TPS QA main method...")
            
            # === Data imports ===
            msg_waiting = "Waiting on user to finish and hit the script play button..."
            set_progress(msg_waiting, percentage = -1)
            msg_pre = '''Prerequisites:\n
            1. Two different scans of the Penta-guide ready to be imported from the drive.
            2. Nothing should be imported into this year's TPS Annual patient'''
            await_user_input(message=msg_pre)
            
            set_progress("Opening baseline patient...", percentage = -1)
            open_patient_case_and_plan(self.base_mrn, self.base_case)
            
            msg_rsbak = "Backup annonymized baseline and restore..."
            set_progress(msg_rsbak, percentage = -1)
            msg_rsbak_full = f'''Backup annonymized baseline and restore:\n
            1. Backup as annonymized to -> TPS Annual QA\RayStation TPS Annual\{self.year}
            2. Check off 'Retain dates', 'Retain device identity', and 'Retain institution identity'.
            3. Uncheck 'Retain safe private attributes'\n\n
            Then, restore the *.rsbak file to the new patient: \n
            Last Name: TPS_Annual
            First Name: {self.year}
            Patient ID: 0000{self.year} \n\n
            Note: Copy the message if needed.
            '''
            await_user_input(message=msg_rsbak_full)
            
            msg_patient_info = f'''Verify you updated the patient data to the new patient: \n 
            Last Name: TPS_Annual
            First Name: {self.year}
            Patient ID: 0000{self.year} 
            DOB: 01/01/1980\n\n
            Note: Copy the message if needed.'''
            msg_patient = f"Patient -> TPS_Annual, {self.year} 0000{self.year} DOB: 01/01/1980"
            set_progress(msg_patient, percentage = -1)
            await_user_input(message=msg_patient_info)
            
            msg_import_pentaguide = "Import two different CT scans of the Penta-Guide."
            await_user_input(message=msg_import_pentaguide)
            
            # === Patient setup ===
            _logger.info("Creating patient data util object..")
            self.pdu = PatientDataUtil()
            self._set_imaging_system()
            self._create_external()
            # self._copy_body_to_external() # No longer needed but saved for fallback scenario.
            
            # === Dose calculation ===
            self._check_for_deprecated_machines()
            self._delete_dose_to_all_beamsets()
            self._compute_dose_for_all_beamsets()
            
            # === Plan exports ===
            self.pdu.patient.Save()
            self._export_plans()
            self._create_and_export_qa_plans()
            
            # === Fusion ===
            set_progress(msg_waiting, percentage = -1)
            msg_fusion = '''For the Fusion:\n\n
            1. Use the two Penta-Guide scans for the fusion. \n\n 
            2. Use a CT scan aligned "well" (positioned without misalignment to the cross-hairs) as the Reference (fixed) image.  \n\n
            3. Use the "External" (not an auto-contour structure) as the target structure.\n\n\n
            Note: Copy the message if needed.'''
            await_user_input(message=msg_fusion)
            _logger.info("Starting AutoFusion...")
            self.auto_fusion = AutoFusion()
            self.auto_fusion.run_fusion()
            set_progress(msg_waiting, percentage = -1)
            msg_fusion_error = '''Record the fusion deviation.'''
            await_user_input(message=msg_fusion_error)
            
            
            
            # === Field and Geometry ===
            self.ct_exam = self.pdu.get_exam_with_exam_name(self.ct_exam_name)
            self.center_coord_external = self.pdu.get_roi_center_coord_on_ct(
                self.external_name, 
                self.ct_exam_name,
            )
            gtv_vol, ptv_vol = self._roi_geometry()
            self.center_coord_gtv = self.pdu.get_roi_center_coord_on_ct(
                self.gtv_name, 
                self.ct_exam_name
            )
            ssd_dict, jaws_dict = self._field_geometry()
            set_progress(msg_waiting, percentage = -1)
            _logger.info("SSD Dict: %s", ssd_dict)
            _logger.info("Jaws Dict: %s", jaws_dict)
            if ssd_dict and jaws_dict:
                msg_geometry = f'''Record the following measurements: \n\n
                    GTV Volume = {gtv_vol} cm^3 \n\n
                    PTV Volume = {ptv_vol} cm^3 \n\n
                    SSD Values:     
                        G{self.gantry_angles[0]} = {ssd_dict[self.gantry_angles[0]]}
                        G{self.gantry_angles[1]} = {ssd_dict[self.gantry_angles[1]]}
                        G{self.gantry_angles[2]} = {ssd_dict[self.gantry_angles[2]]}\n\n
                    Jaw Values: 
                        G{self.gantry_angles[0]} = {jaws_dict[self.gantry_angles[0]]}
                        G{self.gantry_angles[1]} = {jaws_dict[self.gantry_angles[1]]}
                        G{self.gantry_angles[2]} = {jaws_dict[self.gantry_angles[2]]}
                    '''
            else:
                msg_geometry = "Manually review SSD and jaw settings.  Failed to automate."
            await_user_input(message=msg_geometry)
            
            msg_mlc_shape = "Review the BEV and DRRs for the associated tasks."
            await_user_input(message=msg_mlc_shape)
            
            # === DVH and Dose display ===
            msg_dvh_dose = '''In the DVHDoseDisplay plan:\n
            1. Load "TPS_Annual" clinical goals in plan evaluation.
            2. Record values in associated DVH and Dose display task.
            3. Print the report.'''
            await_user_input(message=msg_dvh_dose)
            
            # === Final message ===
            set_progress("Finishing...", percentage = -1)
            msg_final = '''Final actions: \n\n
            1.  All exported doses and plans should be in this year's RayStation TPS Annual folder.
            2.  Prepare all exported plans for measurement.
            '''
            await_user_input(message=msg_final)
            
            if self.errors:
                e = ValueError("Fix user selection errors.")
                message = "\n\n".join(self.errors)
                await_user_input(message=message)
                _alert_physicist_error(exc=e, message=message)
            
        except Exception as e:
            _logger.error("[FAILED] in main_tps_annual_qa.py.  Email notification sent.  Exception: %s", str(e))
            await_user_input(message="[FAILED] script.  Physicist alerted to address the issue.")
            _alert_physicist_error(e)
            self._abort_script_error(exc=e, message=str(e))
            
        





