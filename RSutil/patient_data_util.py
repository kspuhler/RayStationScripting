"""
PatientDataUtil — Centralized RayStation patient/case data accessor.

Provides a unified interface for retrieving patient, case, plan, beamset, exam,
ROI, and dose data through consistent `get_`, `has_`, and `num_` methods.
Intended for **read-only use** within RayStation scripts to avoid repetitive API calls
and to standardize error handling and logging.

Key features:
- Works with the current open patient/case, or loads a specified one.
- Eager vs. lazy caching for flexible use in interactive vs. batch scripts.
- Graceful handling of missing data via `_error_handling()` and logger output.
- Optional `get_all()` to bulk-hydrate all zero-argument getters.

Method schema:
    get_<thing>()                  → returns or caches item(s)
    get_current_<thing>()          → returns active item in RayStation
    get_<thing>_on_<item>()        → queries relationship (e.g. CT exam name in plan)
    get_<thing>_in_<item>()        → queries contained data (e.g. ROIs in beamset)
    get_<thing>_with_<item>()      → filters by attributes (e.g. ROIs with contours)
    has_<thing>()                  → boolean existence checks
    num_<thing>()                  → numeric counts
    get_all() / get_all_current()  → bulk snapshots / hydration

Example:
    >>> from patient_data_util import PatientDataUtil
    >>> pdu = PatientDataUtil(eager=True)
    >>> pdu.get_plan_names()
    >>> pdu.plan_names

Created on Thu Oct 23 11:02:18 2025

@author: clanco01
"""

from __future__ import annotations

# === Debugging Section ===
_DEBUG = False  # set False for production use

# === WORKING DIRECTORY ===
import sys
sys.path.append(r"\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
sys.path.append(r"F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")

# === Logger setup ===
from RSutil.LogUtil.rs_logging import LOGGERS, set_logger_mode
_logger = LOGGERS["system"]
if _DEBUG:
    set_logger_mode(_logger, "debug")

# === Main library imports ===
from typing import Any, Dict, TypeVar, Protocol
import inspect
T = TypeVar("T")

# === Local imports ===
from RSutil.ErrorsUtil.error_dispatcher import DispatcherConfig
from RSutil.ErrorsUtil.rs_errors import report_error
from RSutil.ErrorsUtil.error_codes import ALERT_PHYSICIST
from RSutil.open_patient_case_and_plan import open_patient_case_and_plan

# === Protocol classes ===
""" Protocol classes of RayStation objects and outputs for attribut, type, and
    method class attributes for ease of use and autocompletion"""
 
class PatientObject(Protocol):
    "Patient"


class PatientDBObject(Protocol):
    "PatientDB"


class CaseObject(Protocol):
    "Patient.Cases"

    
class PatientModelObject(Protocol):
    "Patient.Cases.PatientModel"

 
class ExamObject(Protocol):
    "Patient.Cases.Examinations"
    
    # --- Attributes ---
    Name: str
    PatientPosition: str
    EquipmentInfo: str
    
    # --- Methods ---
    def SetPrimary(self) -> None: ...

class RoiObject(Protocol):
    """Patient.Cases.PatientModel.StructureSets.RoiGeometris"""
    
    # --- Attributes ---
    Name: str
    RoiNumber: int
    Type: str  # i.e. "Gtv", "External"
    
    # --- Methods ---
    def HasContours(self) -> bool: ...
    def GetRoiVolume(self) -> float:...
    def GetCenterOfRoi(self) -> dict[str, float]: ...
    

class BeamObject(Protocol):
    """Patient.Cases.TreatmentPlans.BeamSets.Beams"""
    
    # --- Attributes ---
    Name: str
    BeamMU: float
    BeamQualityId: str
    GantryAngle: float
    
    
    # --- Methods ---


class BeamsetObject(Protocol):
    """Patient.Cases.TreatmentPlans.BeamSets"""
    
    # --- Attributes ---
    DeliveryTechnique: str
    DicomPlanLabel: str
    Modality: str
    FractionPattern: Any
    
    # --- Methods ---


class PlanObject(Protocol):
    """Patient.Cases.TreatmentPlans"""
    
    # --- Attributes ---
    Name: str
    
    # --- Methods ---


class DoseEvaluationObject(Protocol):
    """Patient.Cases.TreatmentDelivery.FractionEvaluations[0].DoseOnExaminations.DoseOnExaminations.DoseEvaluations"""
    
    # --- Attributes ---
    Name: str
    DoseValues: Any
    
    # --- Methods ---
    

# === Error handling ===
def _error_handling(
        exc: Exception, 
        patient_info: dict | None = None, 
        method_name: str | None = None,
        classification: str = "DATA_ACCESS_FAILURE",
) -> None:
    """Handle internal PatientDataUtil errors with alert and log fallback."""
    if _DEBUG:
        return
    
    patient_info = patient_info or {}                                              
    try:      
        cfg = DispatcherConfig()
        cfg.alert_recipients = ["owen.clancey@nyulangone.org"]
        
        if hasattr(ALERT_PHYSICIST, classification):
            error_def = getattr(ALERT_PHYSICIST, classification)
        else:
            error_def = ALERT_PHYSICIST.RAYSTATION_API_FAILURE
        
        message = f"module: patient_data_util -> method: {method_name} -> error: {classification}"
        
        report_error(
                error_def=error_def, 
                original_exception=exc, 
                context={"module": "patient_data_util.py"},
                metadata=patient_info,
                message=message,
                dispatcher_config=cfg,
            )
        _logger.error(
            "[PatientDataUtil] %s failed (%s) | patient_info=%s",
            method_name, classification, patient_info
        )
    
    except Exception as fallback_exc:
        # Guard against logging failures themselves
        print(f"[Critical] Failed to report error in {method_name}: {fallback_exc}")

# === RayStation import ===
try:
    from connect import get_current
    RAYSTATION_AVAILABLE = True
except Exception:
    _logger.warning("RayStation environment not detected.")
    RAYSTATION_AVAILABLE = False


class PatientDataUtil():
    """
    Unified, read-only accessor for RayStation patient and plan data.
    
    Simplifies retrieval of objects and metadata from the active Patient/Case.
    Works in two modes:
      • Lazy (default): returns values directly, no caching.
      • Eager: stores results as attributes (e.g. self.plan_names).
    
    Args:
        patient_id (str | None): 
            Patient MRN to open. Uses current patient if None.
        case_name (str | None): 
            Case name to open. Uses current case if None.
        plan_name (str | None): 
            Plan name to open. Uses current plan if None.
        beamset_name (str | None): 
            Beamset name to open. Optional.
        eager (bool, optional): 
            If True, caches all returned values as attributes.  Defaults to False.
        preload (bool, optional): 
            If True, automatically calls `get_all()` after init.  Defaults to False.
    
    Example:
        >>> pdu = PatientDataUtil(eager=True)
        >>> pdu.get_ct_exam_names()
        >>> print(pdu.ct_exam_names)
        >>> plan_data = pdu.get_plan_data("Plan 1")
    
    Error handling:
        - Returns None/False for expected missing data.
        - Unexpected exceptions are logged via `_error_handling()`.
    
    Notes:
        This class never modifies RayStation data and serves only for consistent,
        read-only access across clinical scripts.
    """
    
    # === Initialization ===
    def __init__(
            self,
            patient_id: str | None = None,
            case_name: str | None = None,
            plan_name: str | None = None,
            beamset_name: str | None = None,
            eager: bool = False, 
            preload: bool = False
    ):
        """Initialize a PatientDataUtil instance for the currently open patient/case 
        or opens user-provided patient data in RayStation."""

        # === Declarations ===
        self.case: Any | None = None
        self.patient: Any | None = None
        self.patient_id: str | None = None
        self.patient_model: Any | None = None
        self.patient_db: Any | None = None
        self.patient_info: dict[str, str | None] | None = None
        self.plan: Any | None = None
        self.plan_name: str | None = None
        self.exam: Any | None = None
        self.exams: Any | None = None
        self.beamset: Any | None = None
        self.beamset_name: list[str] | None = None
        self.beams: Any | None = None
        self.beam_names: list[str] | None = None
        self.deformable_registration_names: list[str] | None = None
        self.exam_names: list[str] | None = None
        self.exam_name: str | None = None
        self.ct_exams: Any | None = None
        self.ct_exam_names: list[str] | None = None
        self.mr_exams: Any | None = None
        self.mr_exam_names: list[str] | None = None
        self.pet_exams: Any | None = None
        self.pet_exam_names: list[str] | None = None
        self.ct_exam_name_newest: str | None = None
        self.plans: Any | None = None
        self.plan_names: list[str] | None = None
        self.plan_data: Any | None = None
        self.all_plan_data: Any | None = None
        self.dose_evaluation_names: list[str] | None = None
        self.dose_evaluation_names_on_ct: list[str] | None = None
        self.dose_evaluations: list[Any] | None = None
        self.dose_evaluations_on_ct: list[Any] | None = None
        self.beamsets_non_photon: Any | None = None
        self.roi_names_with_contours: Any | None = None
        self.rois_with_contours: Any | None = None
        self.roi_names: list[str] | None = None
        self.rois: Any | None = None
        self.roi_external: Any | None = None
        self.roi_external_name: str | None = None
        
        # === Configuration initialize to input patient_id or current Case ===
        self._KEEP_FIELDS = ["eager", "patient_info", "case", "patient", "_hydrated"]
        self.eager = eager
        self._hydrated = False
        
        if not RAYSTATION_AVAILABLE:
            _logger.warning(
                "PatientDataUtil instantiated outside RayStation; "
                "data access methods will not return real RayStation objects."
            )
            return
        
        try:
            if patient_id:
                open_patient_case_and_plan(
                    mrn=patient_id,
                    case_name=case_name,
                    plan_name=plan_name,
                )
            self.case = get_current("Case")
            self.patient = get_current("Patient")
            self.patient_model = getattr(self.case, "PatientModel", None)
        
            if not self.patient or not self.case:
                _logger.warning(
                    "[PatientDataUtil] Initialization failed — no patient or case open. "
                    "(patient_id=%s, case_name=%s)",
                    patient_id, case_name,
                )
                raise RuntimeError("No patient or case currently loaded in RayStation.")
        
            self.patient_id = getattr(self.patient, "PatientID", None)
            self.patient_info = {
                "patient_name": getattr(self.patient, "Name", "Unknown"),
                "patient_id": self.patient_id,
                "case_name": getattr(self.case, "CaseName", "Unknown"),
            }
        
        except RuntimeError as e:
            _logger.error("[PatientDataUtil] %s", e)
            raise  # prevent half-initialized object
        
        except Exception as e:
            # Unexpected failure — true system error, send alert
            _error_handling(
                exc=e,
                patient_info=getattr(self, "patient_info", {}),
                method_name="__init__",
            )
            raise RuntimeError("Failed to initialize PatientDataUtil due to system error.") from e
        
        
        if preload:
            self.get_all()
    
    # === Helper (internal) methods ===
    def _assign_if_eager(self, attr_name: str, value: T) -> T:
        """
        Assign a computed value to an attribute if eager mode is enabled,
        and always return the value.
    
        Args:
            attr_name: 
                Name of the instance attribute to assign.
            value:     
                Value to assign and return.
    
        Returns:
            T: The computed value, regardless of eager mode.
    
        Notes:
            - In eager mode, the value is assigned to `self.<attr_name>` and also returned.
            - In lazy mode, the value is simply returned.
        """
        if self.eager:
            if not hasattr(self, attr_name):
                _logger.warning(
                    "Creating new attribute '%s' on %s during eager assignment.",
                    attr_name, self.__class__.__name__,
                )
            setattr(self, attr_name, value)
        return value
        
    @staticmethod  
    def _safe_attr(obj: Any, attr_chain: str, default: T | None = None) -> T | None:
        """
        Safely resolve a dotted attribute chain on an object.
        
        This walks through each attribute in ``attr_chain`` (e.g.
        "Prescription.PrimaryPrescriptionDoseReference.DoseValue") and returns
        the final value, or ``default`` if any attribute in the chain is missing.
        
        Args:
            obj: The root object to inspect.
            attr_chain: A dot-separated string of attribute names.
            default: Value to return if resolution fails.
        
        Returns:
            T | None: The resolved attribute value, or ``default`` if unavailable.
        """
        cur = obj
        for name in attr_chain.split("."):
            if cur is None or not hasattr(cur, name):
                return default
            cur = getattr(cur, name)
        return cur

    def _try_get_current(self, key: str, attr_name: str) -> object | None:
        """
        Internal helper: fetch a 'current' RayStation object by key.
    
        Args:
            key:       
                Key used by get_current(...) to look up the object
                (e.g. 'case', 'plan', 'beamset').
            attr_name: 
                Attribute name used for eager assignment on self.
    
        Returns:
            The resolved RayStation object, or None if not available.
        """
        try:
            if not self.has_case():
                return None
            obj = get_current(key)
            return self._assign_if_eager(attr_name, obj)
    
        except Exception as e:
            msg = str(e)
    
            if "invalid objecthandle" in msg.lower():
                _logger.debug(
                    "No current %s loaded in RayStation (key=%s). Returning None.", attr_name, key
                )
                return None

            _error_handling(
                exc=e,
                patient_info=getattr(self, "patient_info", {}),
                method_name=f"get_current_{attr_name}",
            )
        return None

    def _find_rois_by_type(self, roi_type: str) -> list[RoiObject()] | None:
        """
        ***Internal Usage Only - Do not use for getting ROI data** * 
        
        Return the first ROI whose Type matches roi_type in the first structure set.  
        
        Args:
            roi_type(str): 
                Type of ROI (i.e. ``External``)
                
        Returns:
            list[RoiObject()]:
                The RayStaion ROI objects with type roi_type;  otherwise, None
        
        """
        if not self.has_rois():
            return None
        rois = [
            roi 
            for roi in self.patient_model.StructureSets[0].RoiGeometries
            if roi.OfRoi.Type == roi_type
        ]
        if not rois:
            return None
        return rois

    # === CLEAR method ===
    def clear(self, keep_config: bool = True) -> None:
        """
        Reset all cached data attributes and internal state.
    
        Args:
            keep_config: If True, retains configuration fields like 'eager' and logger.
                         If False, resets everything except the logger.
        
        Returns:
            None
    
        This does NOT delete the object, but empties all patient- or case-specific data.
        """
        try:
            # Save config if needed
            eager_flag = getattr(self, "eager", False)
            patient_info = getattr(self, "patient_info", None)
    
            # Iterate over all attributes
            for name in list(vars(self).keys()):
                # Skip protected/internal ones
                if name.startswith("_"):
                    continue
                # Skip config if requested
                if keep_config and name in self._KEEP_FIELDS:
                    continue
    
                setattr(self, name, None)
    
            # Reset hydration flag
            self._hydrated = False
    
            # Restore config if we kept it
            if keep_config:
                self.eager = eager_flag
                self.patient_info = patient_info
    
            _logger.debug("PatientDataUtil object cleared (keep_config=%s)", keep_config)
    
        except Exception as e:
            _error_handling(
                exc=e,
                patient_info=getattr(self, "patient_info", {}),
                method_name="clear",
                classification="SYSF_UNHANDLED_EXCEPTION",
            )
    
    # === GET current methods ===
    def get_current_patient_db(self) -> PatientDBObject() | None:
        """Return the currently loaded RayStation Patient DB, or None if no case is active.

        Returns:
            PatientDBObject() | None: The current Patient DB object, or None if no case is loaded.
        """
        return self._try_get_current("PatientDB", "patient_db")
    
    def get_current_case(self) -> CaseObject() | None:
        """Return the currently loaded RayStation Case, or None if no case is active.

        Returns:
            CaseObject() | None: The current Case object, or None if no case is loaded.
        """
        return self._try_get_current("Case", "case")
    
    def get_current_patient(self) -> PatientObject() | None:
        """Return the currently loaded RayStation Patient, or None if no patient is active.

        Returns:
            PatientObject() | None: The current Patient object, or None if no patient is loaded.
        """
        return self._try_get_current("Patient", "patient")
    
    def get_current_plan(self) -> PlanObject() | None:
        """Return the currently loaded RayStation Plan, or None if no plan is active.

        Returns:
            PlanObject() | None: The current Plan object, or None if no plan is loaded.
        """
        return self._try_get_current("Plan", "plan")
    
    def get_current_patient_model(self) -> PatientModelObject() | None:
        """Return the currently loaded RayStation Patient Model, or None if no plan is active.

        Returns:
            PatientModelObject() | None: The current Patient Model object, or None if no plan is loaded.
        """
        try:
            case = self.get_current_case()
            if not case:
                return None
            return self._assign_if_eager("patient_model", getattr(case, "PatientModel", None))
        except Exception as e:
            _error_handling(
                exc=e,
                patient_info=getattr(self, "patient_info", {}),
                method_name="get_current_patient_model",
            )
            return None
    
    def get_current_plan_data(self) -> dict[str, dict[str, Any]] | None:
        """
        Get plan data for the currently loaded treatment plan.
    
        Returns:
            dict[str, dict[str, Any]] | None: 
                Dictionary keyed by beamset name with plan/beamset details,
                or None if no current plan is loaded.
        """
        try:
            if not self.has_plans():
                return None
            plan = self.get_current_plan()
            if not plan:
                return None
    
            plan_name = getattr(plan, "Name", None)
            if not plan_name:
                return None
    
            plan_data = self.get_plan_data(plan_name)
            if not plan_data:
                return None
    
            return self._assign_if_eager("plan_data", plan_data)
    
        except Exception as e:
            _error_handling(
                exc=e,
                patient_info=getattr(self, "patient_info", {}),
                method_name="get_current_plan_data",
            )
            return None

    def get_current_plan_name(self) -> str | None:
        """Return the currently loaded RayStation Plan Name, or None if no plan is active.

        Returns:
            str | None: The current Plan Name, or None if no plan is loaded.
        """
        try:
            plan = self.get_current_plan()
            if not plan:
                return None
            return self._assign_if_eager("plan_name", getattr(plan, "Name", None))
        except Exception as e:
            _error_handling(
                exc=e,
                patient_info=getattr(self, "patient_info", {}),
                method_name="get_current_plan_name",
            )
            return None
    
    def get_current_beamset(self) -> BeamsetObject() | None:
        """Return the currently loaded RayStation BeamSet, or None if no beamset is active.

        Returns:
            BeamsetObject() | None: The current BeamSet object, or None if no beamset is loaded.
        """
        return self._try_get_current("BeamSet", "beamset")
    
    def get_current_beamset_name(self) -> str | None:
        """Return the currently loaded RayStation BeamSet name, or None if no beamset is active.

        Returns:
            str | None: The current BeamSet name, or None if no beamset is loaded.
        """
        try:
            beamset = self.get_current_beamset()
            if not beamset:
                return None
            name = getattr(beamset, "DicomPlanLabel", None)
            return self._assign_if_eager("beamset_name", name)
        except Exception as e:
            _error_handling(
                exc=e,
                patient_info=getattr(self, "patient_info", {}),
                method_name="get_current_beamset_name",
            )
            return None
    
    def get_current_beams(self) -> list[BeamObject()] | None:
        """Return a list of the currently loaded RayStation BeamSet's Beams, 
            or None if no beams exist.

        Returns:
            list[BeamObject()] | None: List of the current BeamSet's Beams, 
                or None if no beams exist.
        """
        try:
            beamset = self.get_current_beamset()
            if not beamset:
                return None
            beams = list(getattr(beamset, "Beams", []))
            return self._assign_if_eager("beams", beams)
        except Exception as e:
            _error_handling(
                exc=e,
                patient_info=getattr(self, "patient_info", {}),
                method_name="get_current_beams",
            )
            return None
    
    def get_current_beam_names(self) -> list[str] | None:
        """Return the currently loaded RayStation BeamSet's Beams' names, 
            or None if no beams exists.

        Returns:
            list[str] | None: List of current BeamSet's Beam names, 
                or None if no beams exist.
        """
        try:
            beamset = self.get_current_beamset()
            if not beamset:
                return None
            beam_names = [beam.Name for beam in getattr(beamset, "Beams", [])]
            return self._assign_if_eager("beam_names", beam_names)
        except Exception as e:
            _error_handling(
                exc=e,
                patient_info=getattr(self, "patient_info", {}),
                method_name="get_current_beam_names",
            )
            return None
    
    def get_current_exam(self) -> ExamObject() | None:
        """Return the currently loaded RayStation Examination, or None if no exam is active.

        Returns:
            ExamObject() | None: The current Examination object, or None if no exam is loaded.
        """
        return self._try_get_current("Examination", "exam")
    
    def get_current_exam_name(self) -> str | None:
        """Return the currently loaded RayStation Examination's name, or None if no exam is active.

        Returns:
            str | None: The current Examination's name, or None if no exam is loaded.
        """
        try:
            exam = self.get_current_exam()
            if not exam:
                return None
            name = getattr(exam, "Name", None)
            return self._assign_if_eager("exam_name", name)
        except Exception as e:
            _error_handling(
                exc=e,
                patient_info=getattr(self, "patient_info", {}),
                method_name="get_current_exam_name",
            )
            return None
    
    def get_current_roi_names_with_contours(self) -> list[str] | None:
        """
        Get ROI names that have existing contours on the current examination.
        
        Returns:
            list[str] | None:
                A list of ROI names with valid contours on the current exam,
                or None if no exam or contours are available.
        """
        try:
            exam_name = self.get_current_exam_name()
            if not exam_name:
                return None 
            roi_names_with_contours = self.get_roi_names_with_contours_on_ct(exam_name)
            if not roi_names_with_contours:
                return None
            return self._assign_if_eager("roi_names_with_contours", roi_names_with_contours)
        except Exception as e:
            _error_handling(
                exc=e,
                patient_info=getattr(self, "patient_info", {}),
                method_name="get_current_roi_names_with_contours",
            )
            return None
    
    def get_current_rois_with_contours(self) -> list[RoiObject()] | None:
        """
        Get structure set ROIs that have existing contours on the current examination.
        
        Returns:
            list[RoiObject()] | None:
                A list of ROI with valid contours on the current exam,
                or None if no exam or contours are available.
        """
        try:
            exam_name = self.get_current_exam_name()
            if not exam_name:
                return None
            rois_with_contours = self.get_rois_with_contours_on_ct(exam_name)
            if not rois_with_contours:
                return None
            return self._assign_if_eager("rois_with_contours", rois_with_contours)
        except Exception as e:
            _error_handling(
                exc=e,
                patient_info=getattr(self, "patient_info", {}),
                method_name="get_current_rois_with_contours",
            )
            return None
    
    # === GET exam methods ===
    def get_exams(self) -> list[ExamObject()] | None:
        """Get all examinations in the current case.
    
        Returns:
            list[ExamObject()] | None: 
                All examination if available, otherwise ``None``.
        """
        try:
            if not self.has_exams():
                return None
            exams = [exam for exam in self.case.Examinations]
            return self._assign_if_eager("exams", exams)
        except Exception as e:
            _error_handling(
                exc=e,
                patient_info=getattr(self, "patient_info", {}),
                method_name="exams",
            )
            return None
        
    def get_exam_names(self) -> list[str] | None:
        """Get the names of all examinations in the current case.
    
        Returns:
            list[str] | None: 
                A list of examination names if available, otherwise ``None``.
        """
        try:
            if not self.has_exams():
                return None
            exam_names = [exam.Name for exam in self.case.Examinations]
            return self._assign_if_eager("exam_names", exam_names)
        except Exception as e:
            _error_handling(
                exc=e,
                patient_info=getattr(self, "patient_info", {}),
                method_name="get_exam_names",
            )
            return None
    
    def get_exam_with_exam_name(self, exam_name: str | None = None) -> ExamObject() | None:
        """Get the examination with the name of the exam_name.
    
        Args:
            exam_name (str): 
                Name of the examination.
    
        Returns:
            ExamObject() | None: 
                The examination with the exam_name, otherwise ``None``.
        """
        try:
            exams = self.get_exams() or []
            if exams:
                for exam in exams:
                    if exam_name == exam.Name:
                        return exam
            return None
        except Exception as e:
            _error_handling(
                exc=e,
                patient_info=getattr(self, "patient_info", {}),
                method_name="get_exam_with_exam_name",
            )
            return None
    
    def get_exam_name_from_exam(self, exam: ExamObject() | None = None) -> str | None:
        """Get the examination name from the exam.
    
        Args:
            exam (ExamObject()): 
                The RayStation examination object.
    
        Returns:
            str | None: 
                The examination name from the exam, otherwise ``None``.
        """
        try:
            if exam:
                return getattr(exam, "Name", None)
            return None
        except Exception as e:
            _error_handling(
                exc=e,
                patient_info=getattr(self, "patient_info", {}),
                method_name="get_exam_name_from_exam",
            )
            return None
    
    def get_ct_exam_names(self) -> list[str] | None:
        """Get the names of all CT examinations in the current case.
    
        Returns:
            list[str] | None: 
                A list of CT exam names if available, otherwise ``None``.
        """
        try:
            if not self.has_exams():
                return None
            ct_exam_names = [
                exam.Name
                for exam in self.case.Examinations
                if getattr(exam.EquipmentInfo, "Modality", None) == "CT"
            ]
            return self._assign_if_eager("ct_exam_names", ct_exam_names)
        except Exception as e:
            _error_handling(
                exc=e,
                patient_info=getattr(self, "patient_info", {}),
                method_name="get_ct_exam_names",
            )
            return None
    
    def get_ct_exams(self) -> list[ExamObject()] | None:
        """Get all CT examination objects in the current case.
    
        Returns:
            list[ExamObject()] | None: 
                A list of CT examination objects if available, otherwise ``None``.
        """
        try:
            if not self.has_exams():
                return None
            ct_exams = [
                exam
                for exam in self.case.Examinations
                if getattr(exam.EquipmentInfo, "Modality", None) == "CT"
            ]
            return self._assign_if_eager("ct_exams", ct_exams)
        except Exception as e:
            _error_handling(
                exc=e,
                patient_info=getattr(self, "patient_info", {}),
                method_name="get_ct_exams",
            )
            return None
    
    def get_mr_exam_names(self) -> list[str] | None:
        """Get the names of all MR examinations in the current case.
    
        Returns:
            list[str] | None: 
                A list of MR exam names if available, otherwise ``None``.
        """
        try:
            if not self.has_exams():
                return None
            mr_exam_names = [
                exam.Name
                for exam in self.case.Examinations
                if getattr(exam.EquipmentInfo, "Modality", None) == "MR"
            ]
            return self._assign_if_eager("mr_exam_names", mr_exam_names)
        except Exception as e:
            _error_handling(
                exc=e,
                patient_info=getattr(self, "patient_info", {}),
                method_name="get_mr_exam_names",
            )
            return None
    
    def get_mr_exams(self) -> list[ExamObject()] | None:
        """Get all MR examination objects in the current case.
    
        Returns:
            list[ExamObject()] | None: 
                A list of MR examination objects if available, otherwise ``None``.
        """
        try:
            if not self.has_exams():
                return None
            mr_exams = [
                exam
                for exam in self.case.Examinations
                if getattr(exam.EquipmentInfo, "Modality", None) == "MR"
            ]
            return self._assign_if_eager("mr_exams", mr_exams)
        except Exception as e:
            _error_handling(
                exc=e,
                patient_info=getattr(self, "patient_info", {}),
                method_name="get_mr_exams",
            )
            return None
    
    def get_pet_exam_names(self) -> list[str] | None:
        """Get the names of all PET examinations in the current case.
    
        Returns:
            list[str] | None: 
                A list of PET exam names if available, otherwise ``None``.
        """
        try:
            if not self.has_exams():
                return None
            pet_exam_names = [
                exam.Name
                for exam in self.case.Examinations
                if getattr(exam.EquipmentInfo, "Modality", None) == "Pet"
            ]
            return self._assign_if_eager("pet_exam_names", pet_exam_names)
        except Exception as e:
            _error_handling(
                exc=e,
                patient_info=getattr(self, "patient_info", {}),
                method_name="get_pet_exam_names",
            )
            return None
    
    def get_pet_exams(self) -> list[ExamObject()] | None:
        """Get all PET examination objects in the current case.
    
        Returns:
            list[ExamObject()] | None: 
                A list of PET examination objects if available, otherwise ``None``.
        """
        try:
            if not self.has_exams():
                return None
            pet_exams = [
                exam
                for exam in self.case.Examinations
                if getattr(exam.EquipmentInfo, "Modality", None) == "Pet"
            ]
            return self._assign_if_eager("pet_exams", pet_exams)
        except Exception as e:
            _error_handling(
                exc=e,
                patient_info=getattr(self, "patient_info", {}),
                method_name="get_pet_exams",
            )
            return None
    
    def get_ct_exam_name_newest(self) -> str | None:
        """Get the most recent CT exam name by acquisition date/time.
    
        Returns:
            str | None: 
                The name of the most recently acquired CT exam, or ``None`` if not found.
        """
        try:
            if not self.has_exams():
                return None
        
            ct_exam_names = self.get_ct_exam_names()
            if not ct_exam_names:
                return None
        
            dated = []
            for name in ct_exam_names:
                try:
                    dt = self.case.Examinations[name].GetExaminationDateTime()
                    if dt is not None:
                        dated.append((name, dt))
                except Exception:
                    continue
        
            if not dated:
                return None
        
            ct_exam_name_newest = max(dated, key=lambda pair: pair[1])[0]
            return self._assign_if_eager("ct_exam_name_newest", ct_exam_name_newest)
        except Exception as e:
            _logger.error("[FAILED] in get_ct_exam_name_newest: %s", str(e))
            _error_handling(
                exc=e,
                patient_info=getattr(self, "patient_info", {}),
                method_name="get_ct_exam_name_newest",
            )
            return None
    
    def get_ct_exam_name_in_plan(self, plan_name: str | None = None) -> str | None:
        """Get the CT examination name associated with a given plan name.
    
        Args:
            plan_name (str): 
                Name of the treatment plan containing the beamset.
    
        Returns:
            str | None: 
                The name of the CT examination used for that plan, or ``None`` if not found.
    
        Notes:
            - Requires a valid case, plan, and beamset.
        """
        try:
            if not plan_name:
                return None
            if not self.has_plan_name(plan_name):
                return None
            plan = next((p for p in self.case.TreatmentPlans if p.Name == plan_name), None)
            if not plan:
                _logger.info("No plan in get_ct_exam_name_in_plan()...")
                return None
    
            if not plan.BeamSets:
                _logger.info("No plan.Beamsets in get_ct_exam_name_in_plan()...")
                return None
    
            try:
                planning_exam = plan.BeamSets[0].GetPlanningExamination()
            except Exception:
                planning_exam = None
            
            if planning_exam is None:
                _logger.info("No planning examination in get_ct_exam_name_in_plan()...")
                return None
            
            ct_exam_name = getattr(planning_exam, "Name", None)
            return ct_exam_name
    
        except Exception as e:
            _error_handling(
                exc=e,
                patient_info=getattr(self, "patient_info", {}),
                method_name="get_ct_exam_name_in_plan",
            )
            return None

    def get_ct_exam_in_plan(self, plan_name: str | None = None) -> ExamObject() | None:
        """Get the CT examination associated with a given plan name.
    
        Args:
            plan_name (str): 
                Name of the treatment plan containing the beamset.
    
        Returns:
            ExamObject() | None: 
                The CT examination used for that plan, or ``None`` if not found.
    
        Notes:
            - Requires a valid case, plan, and beamset.
        """
        try:
            if not plan_name:
                return None
            if not self.has_plan_name(plan_name):
                return None
            plan = next((p for p in self.case.TreatmentPlans if p.Name == plan_name), None)
            if not plan:
                _logger.info("No plan in get_ct_exam_name_in_plan()...")
                return None
    
            if not plan.BeamSets:
                _logger.info("No plan.Beamsets in get_ct_exam_name_in_plan()...")
                return None
    
            try:
                planning_exam = plan.BeamSets[0].GetPlanningExamination()
            except Exception:
                planning_exam = None
            
            return planning_exam
    
        except Exception as e:
            _error_handling(
                exc=e,
                patient_info=getattr(self, "patient_info", {}),
                method_name="get_ct_exam_in_plan",
            )
            return None
    
    def get_ct_exam_name_in_plan_beamset(
            self, 
            plan_name: str | None = None, 
            beamset_name: str | None = None
    ) -> str | None:
        """Get the CT examination name associated with a given plan and beamset.
    
        Args:
            plan_name (str): 
                Name of the treatment plan containing the beamset.
            beamset_name (str): 
                DICOM plan label of the beamset.
    
        Returns:
            str | None: 
                The name of the CT examination used for that beamset, or ``None`` if not found.
    
        Notes:
            - Requires a valid case, plan, and beamset.
        """
        try:
            if not plan_name or not beamset_name:
                return None
            if not self.has_plan_beamset_name(plan_name, beamset_name):
                return None
    
            plan = next((p for p in self.case.TreatmentPlans if p.Name == plan_name), None)
            if not plan:
                return None
    
            beamset = next((b for b in plan.BeamSets if b.DicomPlanLabel == beamset_name), None)
            if not beamset:
                return None
    
            try:
                planning_exam = beamset.GetPlanningExamination()
            except Exception:
                planning_exam = None
            
            if planning_exam is None:
                return None
            
            ct_exam_name = getattr(planning_exam, "Name", None)
            return ct_exam_name
    
        except Exception as e:
            _error_handling(
                exc=e,
                patient_info=getattr(self, "patient_info", {}),
                method_name="get_ct_exam_name_in_plan_beamset",
            )
            return None

    # === GET dose methods ===
    def get_dose_evaluation_names_on_ct(self, ct_exam_name: str | None = None) -> list[str] | None:
        """Get the names of all dose evaluation objects on a CT exam in the case.
        
        Args:
            ct_exam_name (str): 
                Name of the CT exam plan containing the dose evluations.
    
        Returns:
            list[str] | None:
                A list of dose evaluation names, or ``None`` if unavailable.
        """
        try:
            if not self.has_case() or not ct_exam_name:
                return None
            dose_evals = self.get_dose_evaluations_on_ct(ct_exam_name)
            dose_evaluation_names = [dose_eval.Name for dose_eval in dose_evals]
            return dose_evaluation_names
    
        except Exception as e:
            _error_handling(
                exc=e,
                patient_info=getattr(self, "patient_info", {}),
                method_name="get_dose_evaluation_names_on_ct",
            )
            return None
    
    def get_dose_evaluations_on_ct(self, ct_exam_name: str | None = None) -> list[DoseEvaluationObject()] | None:
        """Get all dose evaluation objects on a CT exam in the current case.
        
        Args:
            ct_exam_name (str): 
                Name of the CT exam plan containing the dose evluations.
        
        Returns:
            list[DoseEvaluationObject()] | None:
                A dictionary mapping each dose evaluation name to its corresponding
                dose evaluation object, or ``None`` if unavailable.
        """
        try:
            if not self.has_case() or not ct_exam_name:
                return None
            dose_evaluations = [
                dose_eval
                for fe in self.case.TreatmentDelivery.FractionEvaluations
                for exam in fe.DoseOnExaminations
                if exam.OnExamination.Name == ct_exam_name
                for dose_eval in exam.DoseEvaluations
            ]
        
            return dose_evaluations

        except Exception as e:
            _error_handling(
                exc=e,
                patient_info=getattr(self, "patient_info", {}),
                method_name="get_dose_evaluations_on_ct",
            )
            return None
    
    def get_dose_evaluation_names(self) -> list[str] | None:
        """Get the names of all dose evaluation objects in the case.
        
        Returns:
            list[str] | None:
                A list of dose evaluation names, or ``None`` if unavailable.
        """
        try:
            if not self.has_case():
                return None
            dose_evals = self.get_dose_evaluations()
            dose_evaluation_names = [dose_eval.Name for dose_eval in dose_evals]
    
            return self._assign_if_eager("dose_evaluation_names", dose_evaluation_names)
    
        except Exception as e:
            _error_handling(
                exc=e,
                patient_info=getattr(self, "patient_info", {}),
                method_name="get_dose_evaluation_names",
            )
            return None
    
    def get_dose_evaluations(self) -> list[DoseEvaluationObject()] | None:
        """Get all dose evaluation objects in the current case.
        
        list[DoseEvaluationObject()] | None:
                A dictionary mapping each dose evaluation name to its corresponding
                dose evaluation object, or ``None`` if unavailable.
        """
        try:
            if not self.has_case():
                return None
            dose_evaluations = [
                dose_eval
                for fe in self.case.TreatmentDelivery.FractionEvaluations
                for exam in fe.DoseOnExaminations
                for dose_eval in exam.DoseEvaluations
            ]
        
            return self._assign_if_eager("dose_evaluations", dose_evaluations)

        except Exception as e:
            _error_handling(
                exc=e,
                patient_info=getattr(self, "patient_info", {}),
                method_name="get_dose_evaluations",
            )
            return None

    
    # === GET plan metadata methods ===
    
    def get_iso_in_beam(self, beam: BeamObject() | None = None) -> dict | None:
        """Get isocenter in beam object.
    
        Args:
            beam (BeamObject):
                RayStation BeamObject containing the isocenter.
    
        Returns:
            dict| None:
                A dict of (x, y, z) isocenter coordinates, otherwise ``None``.
        """
        try:
            if not beam:
                return None
            iso = getattr(beam, "Isocenter", None)
            pos = getattr(iso, "Position", None) if iso else None
            return pos
    
        except Exception as e:
            _error_handling(
                exc=e,
                patient_info=getattr(self, "patient_info", {}),
                method_name="get_iso_in_beam",
            )
            return None
    
    def get_iso_in_plan_beamset_beam(
            self, 
            plan_name: str | None = None, 
            beamset_name: str | None = None,
            beam_name: str | None = None,
    ) -> dict | None:
        """Get isocenter in plan-beamset-beam.
    
        Args:
            plan_name (str):
                Name of the treatment plan.
            beamset_name (str):
                DICOM plan label of the beamset within that plan.
            beam_name (str):
                Name of the beam in beamset-plan.
    
        Returns:
            dict| None:
                A dict of (x, y, z) isocenter coordinates, otherwise ``None``.
        """
        try:
            if not plan_name or not beamset_name or not beam_name:
                return None
            if not self.has_plan_beamset_beam_name(plan_name, beamset_name, beam_name):
                return None
            beam = self.case.TreatmentPlans[plan_name].BeamSets[beamset_name].Beams[beam_name]
            
            iso = getattr(beam, "Isocenter", None)
            pos = getattr(iso, "Position", None) if iso else None
            return pos
    
        except Exception as e:
            _error_handling(
                exc=e,
                patient_info=getattr(self, "patient_info", {}),
                method_name="get_iso_in_plan_beamset_beam",
            )
            return None
    
    def get_beamsets_in_plan(self, plan_name: str | None = None) -> list[BeamsetObject()] | None:
        """Get all beamsets in the plan_name.
        
        Args:
            plan_name (str):
                Name of the treatment plan.
    
        Returns:
            list[BeamsetObject()] | None:
                A list of beamsets in the plan if available, otherwise ``None``.
        """
        try:
            if not self.has_plan_name(plan_name):
                return None
            beamsets = [bs for bs in self.case.TreatmentPlans[plan_name].BeamSets]
            return beamsets
    
        except Exception as e:
            _error_handling(
                exc=e,
                patient_info=getattr(self, "patient_info", {}),
                method_name="get_beamsets_in_plan",
            )
            return None

    def get_beamset_in_plan(
            self, 
            plan_name: str | None = None,
            beamset_name: str | None = None,
    ) -> BeamsetObject() | None:
        """Get the beamset in the plan.
        
        Args:
            plan_name (str):
                Name of the treatment plan.
            beamset_name (str):
                DICOM plan label of the beamset within that plan.
    
        Returns:
            BeamsetObject() | None:
                A beamset in the plan if available, otherwise ``None``.
        """
        try:
            if not plan_name or not beamset_name:
                return None
            if not self.has_plan_beamset_name(plan_name, beamset_name):
                return None
            return self.case.TreatmentPlans[plan_name].BeamSets[beamset_name]
    
        except Exception as e:
            _error_handling(
                exc=e,
                patient_info=getattr(self, "patient_info", {}),
                method_name="get_beamset_in_plan",
            )
            return None
    
    def get_beamset_names_in_plan(self, plan_name: str | None = None) -> list[str] | None:
        """Get the names of all beamset in the plan_name.
        
        Args:
            plan_name (str):
                Name of the treatment plan.
    
        Returns:
            list[str] | None:
                A list of beamset names in the plan if available, otherwise ``None``.
        """
        try:
            _logger.debug("Retrieving beamset names in plan...")
            if not self.has_plan_name(plan_name):
                return None
            beamset_names = [bs.DicomPlanLabel for bs in self.case.TreatmentPlans[plan_name].BeamSets]
            return beamset_names
    
        except Exception as e:
            _error_handling(
                exc=e,
                patient_info=getattr(self, "patient_info", {}),
                method_name="get_beamset_names_in_plan",
            )
            return None

    def get_beam_names_in_plan_beamset(
        self,
        plan_name: str | None = None,
        beamset_name: str | None = None,
    ) -> list[str] | None:
        """Return list of beam names in the plan-beamset. Empty list if not found.
        
        Args:
            plan_name (str):
                Name of the treatment plan.
            beamset_name (str):
                DICOM plan label of the beamset within that plan.
        
        Returns:
            list[str] | None:
                A list of beam names in the beamset and plan if available, otherwise ``None``.
        """        
        try:
            if not plan_name or not beamset_name:
                return None
            
            beamset = self.get_beamset_in_plan(plan_name, beamset_name)
            _logger.debug("Retrieved Beamset: %s", beamset)
            if not beamset:
                return None
            
            beam_names = [b.Name for b in beamset.Beams]
            _logger.debug("Retrieved beam names: %s", beam_names)
            if beam_names is None:
                return None
            return beam_names
        except Exception as e:
            _error_handling(
                exc=e, 
                patient_info=getattr(self, "patient_info", {}), 
                method_name="get_beam_names_in_plan_beamset")
            return []

    def get_machine_in_plan_beamset(
            self, 
            plan_name: str | None = None,
            beamset_name: str | None = None,
    ) -> str | None:
        """Get the MachineName in the plan-beamset.
        
        Args:
            plan_name (str):
                Name of the treatment plan.
            beamset_name (str):
                DICOM plan label of the beamset within that plan.
    
        Returns:
            str | None:
                The MachineName in the plan-beamset if available, otherwise ``None``.
        """
        try:
            if not plan_name or not beamset_name:
                return None
            bs = self.get_beamset_in_plan(plan_name, beamset_name)
            mach_ref = getattr(bs, "MachineReference", None)
            mach_name = getattr(mach_ref, "MachineName", None)
            return mach_name
    
        except Exception as e:
            _error_handling(
                exc=e,
                patient_info=getattr(self, "patient_info", {}),
                method_name="get_machine_in_plan_beamset",
            )
            return None
    
    def get_plans(self) -> list[PlanObject()] | None:
        """Get all treatment plans in the current case.
    
        Returns:
            list[PlanObject()] | None:
                A list of treatment plan if available, otherwise ``None``.
        """
        try:
            if not self.has_plans():
                return None
            plans = [plan for plan in self.case.TreatmentPlans]
            return self._assign_if_eager("plans", plans)
    
        except Exception as e:
            _error_handling(
                exc=e,
                patient_info=getattr(self, "patient_info", {}),
                method_name="get_plans",
            )
            return None    
    
    def get_plan_names(self) -> list[str] | None:
        """Get the names of all treatment plans in the current case.
    
        Returns:
            list[str] | None:
                A list of treatment plan names if available, otherwise ``None``.
        """
        try:
            if not self.has_plans():
                return None
            plan_names = [plan.Name for plan in self.case.TreatmentPlans]
            return self._assign_if_eager("plan_names", plan_names)
    
        except Exception as e:
            _error_handling(
                exc=e,
                patient_info=getattr(self, "patient_info", {}),
                method_name="get_plan_names",
            )
            return None
    
    def get_plan_data(self, plan_name: str | None = None) -> dict[str, dict[str, Any]] | None:
        """
        Get plan and beamset data for a specified treatment plan.
    
        Safely retrieves key attributes (dose, fractions, CT, and machine details)
        for all beamsets in the given plan. Returns empty dict if the plan name is
        invalid, missing, or contains no beamsets. Missing attributes are returned
        as 'None'.
    
        Args:
            plan_name (str): 
                Name of the treatment plan. If not provided or not found, returns {}.
    
        Returns:
            dict[str, dict[str, Any]] | None: 
                Dictionary keyed by beamset name, where each value contains plan and
                beamset information (e.g., dose, CT, machine, modality, technique).
        """
        try:
            if not self.has_plan_name(plan_name):
                return None
            
            plan_data = {}
            for plan in self.case.TreatmentPlans:
                plan_name_str = getattr(plan, "Name", None)
                if plan_name_str != plan_name:
                    continue
                for beamset in getattr(plan, "BeamSets", []):
                    beamset_name = getattr(beamset, "DicomPlanLabel", None)
                    if not beamset_name:
                        continue
                    
                    dose_obj = getattr(beamset, "FractionDose", None) if self.has_dose_on_plan_beamset(plan_name, beamset_name) else None
                    dose_rx = self._safe_attr(
                        beamset, 
                        "Prescription.PrimaryPrescriptionDoseReference.DoseValue", 
                        None
                    )
                    fractions = self._safe_attr(beamset, "FractionationPattern.NumberOfFractions", None)
                    
                    ct_obj = None
                    ct_exam_name = None
                    if hasattr(beamset, "GetPlanningExamination"):
                        try:
                            ct_obj = beamset.GetPlanningExamination()
                            ct_exam_name = getattr(ct_obj, "Name", None)
                        except Exception:
                            ct_obj = None
                            ct_exam_name = None
                    
                    machine = self._safe_attr(beamset, "MachineReference.MachineName", None) 
                    modality = self._safe_attr(beamset, "Modality", None)
                    patient_position = self._safe_attr(beamset, "PatientPosition", None)
                    delivery_technique = self._safe_attr(beamset, "DeliveryTechnique", None)
                    plan_generation_technique = self._safe_attr(beamset, "PlanGenerationTechnique", None)
     
                    plan_data[beamset_name] = {
                        "plan_name": plan_name_str,
                        "beamset": beamset,
                        "beamset_name": beamset_name,
                        "dose_object": dose_obj,
                        "dose_rx": dose_rx,
                        "fractions": fractions,
                        "ct_object": ct_obj,
                        "ct_exam_name": ct_exam_name,
                        "machine": machine,
                        "modality": modality,
                        "patient_position": patient_position,
                        "delivery_technique": delivery_technique,
                        "plan_generation_technique": plan_generation_technique,
                    }
                # Found the plan
                break
    
            return plan_data
        except Exception as e:
            _logger.error("[FAILED] inside get_plan_data:  Plan Name - %s", plan_name)
            _error_handling(
                exc=e, 
                patient_info=getattr(self, "patient_info", {}),
                method_name="get_plan_data",
            )
            return None
    
    def get_beamsets_non_photon(self) -> list[BeamsetObject()] | None:
        """Get all beamsets in the current case that are *not* photon-based.
    
        Returns:
            list[BeamsetObject()] | None:
                A list of non-photon beamset objects (e.g., electron or proton beamsets),
                or ``None`` if unavailable.
        """
        try:
            if not self.has_plans():
                return None
            beamsets_non_photon = [
                beamset
                for plan in self.case.TreatmentPlans
                for beamset in plan.BeamSets
                if beamset.Modality != "Photons"
            ]
            return self._assign_if_eager("beamsets_non_photon", beamsets_non_photon)
        except Exception as e:
            _error_handling(
                exc=e, 
                patient_info=getattr(self, "patient_info", {}),
                method_name="get_beamsets_non_photon",
            )
            return None
        
        
    # === GET Registation methods ===
    # def get_for_registration_names(self):
    #     """ DOC STRING HERE"""
    #     pass
    
    # def get_image_registration_names(self):
    #     """ DOC STRING HERE"""
    #     pass
    
    def get_deformable_registration_names(self) -> list[str] | None:
        """Get all deformable (deformable-structure) registration names in the current case.
    
        Returns:
            list[str] | None:
                A list of deformable registration names,
                or ``None`` if no case is loaded.
        """
        deformable_registration_names: list[str] = []
        try:
            if not self.has_case():
                return None
    
            for sr in self.case.StructureRegistrations:
                structure_group = getattr(sr, "InStructureRegistrationGroup", None)
                if structure_group is not None:
                    deformable_registration_names.append(sr.Name)
    
            return self._assign_if_eager(
                "deformable_registration_names",
                deformable_registration_names,
            )
    
        except Exception as e:
            _error_handling(
                exc=e,
                patient_info=getattr(self, "patient_info", {}),
                method_name="get_deformable_registration_names",
            )
            return None

    
    # def get_registration_number_from_name(self, registration_name):
    #     """ DOC STRING HERE"""
    #     pass
    #     # # Find the registration number
    #     # for i, registration in enumerate(self.case.RigidRegistrations):
    #     #     if registration.Name == registration_name:
    #     #         self.registration_number = i
    #     #         break  # Stop searching after the first match
    
    
    # === GET ROI methods
    def get_roi_names_with_contours_on_ct(self, ct_exam_name: str) -> list[str] | None:
        """Get ROI names that have contours on a given CT examination.
    
        Args:
            ct_exam_name (str):
                The name of the CT examination (i.e. StructureSet key) to inspect.
    
        Returns:
            list[str] | None:
                A list of ROI names that actually have contour data on that CT,
                or ``None`` if unavailable.
        """
        try:
            if not self.has_rois():
                return None
            
            if not self.has_ct_exam_name(ct_exam_name):
                return None
            
            structure_sets = getattr(self.patient_model, "StructureSets", {})
            structure_set = structure_sets[ct_exam_name]
            
            if structure_set is None:
                return None
            
            rois_with_contours = [
                roi.OfRoi.Name
                for roi in structure_set.RoiGeometries
                if roi.HasContours()
            ]
            
            return rois_with_contours
    
        except Exception as e:
            _logger.error("[FAILED] in get_roi_names_with_contours_on_ct with: %s", str(e))
            _error_handling(
                exc=e,
                patient_info=getattr(self, "patient_info", {}),
                method_name="get_roi_names_with_contours_on_ct",
            )
            return None

    def get_roi_on_ct(
            self,
            roi_name: str | None = None,
            ct_exam_name: str | None = None,
        ) -> RoiObject() | None:
        """Get an ROI geometry object on a given CT examination.
    
        Args:
            roi_name (str):
                ROI object name to query.
            ct_exam_name (str):
                The name of the CT examination (i.e., StructureSet key) to inspect.
    
        Returns:
            list[RoiObject()] | None:
                A list of structure set ROI geometry objects on the specified CT,
                or ``None`` if unavailable.
        """
        try:
            if not roi_name or not ct_exam_name:
                return None
                    
            if not self.has_ct_exam_name(ct_exam_name) and not self.has_rois():
                return None
            
            roi_names = self.get_roi_names()
            
            if not roi_names:
                return None
            
            if roi_name not in roi_names:
                return None
            
            rois = self.get_rois_on_ct(ct_exam_name)
            if not rois:
                return None
            
            roi = [roi for roi in rois if roi.OfRoi.Name == roi_name]
            
            return roi
    
        except Exception as e:
            _error_handling(
                exc=e,
                patient_info=getattr(self, "patient_info", {}),
                method_name="get_roi_on_ct",
            )
            return None

    def get_rois_on_ct(
            self, 
            ct_exam_name: str | None = None,
        ) -> list[RoiObject()] | None:
        """Get structure set ROI geometry objects on a given CT examination.
    
        Args:
            ct_exam_name (str):
                The name of the CT examination (i.e., StructureSet key) to inspect.
    
        Returns:
            list[RoiObject()] | None:
                A list of structure set ROI geometry objects on the specified CT,
                or ``None`` if unavailable.
        """
        try:
            if not self.has_rois():
                return None
            
            if not self.has_ct_exam_name(ct_exam_name):
                return None
    
            structure_sets = getattr(self.case.PatientModel, "StructureSets", {})
            structure_set = structure_sets[ct_exam_name]
            if structure_set is None:
                return None
            
            rois = [roi for roi in structure_set.RoiGeometries]
            return rois
    
        except Exception as e:
            _error_handling(
                exc=e,
                patient_info=getattr(self, "patient_info", {}),
                method_name="get_rois_on_ct",
            )
            return None

    def get_rois_with_contours_on_ct(
            self, 
            ct_exam_name: str | None = None,
        ) -> list[RoiObject()] | None:
        """Get structure set ROI geometry objects that have contours on a given CT examination.
    
        Args:
            ct_exam_name (str):
                The name of the CT examination (i.e., StructureSet key) to inspect.
    
        Returns:
            list[RoiObject()] | None:
                A list of structure set ROI geometry objects that have contour data on the specified CT,
                or ``None`` if unavailable.
        """
        try:
            rois = self.get_rois_on_ct(ct_exam_name)
            if not rois:
                return None
            
            roi_with_contours = [roi for roi in rois if roi.HasContours()]
            return roi_with_contours
    
        except Exception as e:
            _error_handling(
                exc=e,
                patient_info=getattr(self, "patient_info", {}),
                method_name="get_rois_with_contours_on_ct",
            )
            return None

    def get_rois_with_contours_in_plan_beamset(
            self, 
            plan_name: str | None = None, 
            beamset_name: str | None = None
    ) -> list[RoiObject()] | None:
        """Get the structure set ROIs associated with a specific plan and beamset.
    
        Args:
            plan_name (str):
                Name of the treatment plan.
            beamset_name (str):
                DICOM plan label of the beamset within that plan.
    
        Returns:
            list[RoiObject()] | None:
                A list of structure set ROI objects in the plan and beamset,
                or ``None`` if unavailable, if the plan/beamset cannot be found, 
                or if prerequisites (case, patient model) are missing.
        """
        try:
            if not self.has_rois():
                return None
            if not self.has_plan_beamset_name(plan_name, beamset_name):
                return None
            
            ct_exam_name = self.get_ct_exam_name_in_plan_beamset(plan_name, beamset_name)
            
            return self.get_rois_with_contours_on_ct(ct_exam_name)
    
        except Exception as e:
            _error_handling(
                exc=e,
                patient_info=getattr(self, "patient_info", {}),
                method_name="get_rois_with_contours_in_plan_beamset",
            )
            return None

    def get_roi_names(self) -> list[str] | None:
        """Return all Region of Interest (ROI) names in the current **Patient Model**.
        
        Returns:
            list[str] | None: 
                List of ROI names, or None if unavailable or the patient model is missing.
        """
        try:
            if not self.has_rois():
                return None
            
            structure_sets = getattr(self.case.PatientModel, "StructureSets", {})
            structure_set = structure_sets[0]
            if structure_set is None:
                return None
            
            roi_names = [roi.OfRoi.Name for roi in structure_set.RoiGeometries]
            return self._assign_if_eager("roi_names", roi_names)
    
        except Exception as e:
            _error_handling(
                exc=e,
                patient_info=getattr(self, "patient_info", {}),
                method_name="get_roi_names",
            )
            return None

    def get_roi_center_coord_on_ct(
            self, 
            roi_name: str | None = None,
            ct_exam_name: str | None = None,
        ) -> dict[str, float] | None:
        """
        Get the center coordinate of an ROI on a given CT examination.
    
        Args:
            roi_name: 
                ROI name to query.
            ct_exam_name: 
                CT exam name (StructureSet key) to query.
    
        Returns:
            dict[str, float] | None:
                The center coordinate of the ROI in DICOM coordinates (cm),
                or ``None`` if unavailable.
        
        Notes:
            Example return -> {"x": 1.0, "y": 5.0, "z": 10.0}
        """
        try:
            if not self.has_rois():
                return None
            
            if not roi_name or not ct_exam_name:
                return None
    
            roi_names = self.get_roi_names_with_contours_on_ct(ct_exam_name) or []
            if roi_name not in roi_names:
                return None
    
            geo = self.patient_model.StructureSets[ct_exam_name].RoiGeometries[roi_name]
            if geo is None:
                return None
    
            center = geo.GetCenterOfRoi()
            if center is None:
                return None
            return center
    
        except Exception as e:
            _error_handling(
                exc=e,
                patient_info=getattr(self, "patient_info", {}),
                method_name="get_roi_center_coord_on_ct",
            )
            return None

    def get_roi_external_on_ct(self, ct_exam_name: str | None = None,) -> RoiObject() | None:
        """
        Get the ROI of type 'External' on the CT exam from the current patient model.
        
        Args:
            ct_exam_name: 
                CT exam name (StructureSet key) to query.
        
        Returns:
            str | None:
                The 'External' ROI if a single external ROI exists; otherwise None.
        """
        try:
            if not ct_exam_name:
                return None
            
            ext_name = self.get_roi_external_name()
            external_roi = self.get_roi_on_ct(ext_name, ct_exam_name)
            
            return external_roi
    
        except Exception as e:
            _error_handling(
                exc=e,
                patient_info=getattr(self, "patient_info", {}),
                method_name="get_roi_external_on_ct",
            )
            return None

    def get_roi_external_name(self) -> str | None:
        """
        Get the name of the ROI of type 'External' from the current patient model.
    
        Returns:
            str | None:
                The name of the 'External' ROI if it exists; otherwise None.
        """
        try:
            rois = self._find_rois_by_type("External")
            of_roi = getattr(rois[0], "OfRoi", None)
            name = getattr(of_roi, "Name", None)
            return self._assign_if_eager("roi_external_name", name)
    
        except Exception as e:
            _error_handling(
                exc=e,
                patient_info=getattr(self, "patient_info", {}),
                method_name="get_roi_external_name",
            )
            return None
    
    def get_volume_of_roi_on_ct(
        self,
        roi_name: str | None = None,
        ct_exam_name: str | None = None,
    ) -> float | None:
        """Return ROI volume (cm³) on the given CT, or None if invalid/missing.
    
        Args:
            roi_name: 
                ROI name to query.
            ct_exam_name: 
                CT exam name to use.
    
        Returns:
            float | None: Volume in cm³, or None if CT/ROI invalid or no contours.
        """
        try:
            if not roi_name or not ct_exam_name:
                return None
            
            rois_with_contours = self.get_roi_names_with_contours_on_ct(ct_exam_name)
            if roi_name not in rois_with_contours:
                return None
            
            geo = self.patient_model.StructureSets[ct_exam_name].RoiGeometries[roi_name]
            if geo is None:
                return None
            vol = geo.GetRoiVolume()  # cm³
            return float(vol) if vol is not None else None
    
        except Exception as e:
            _error_handling(
                exc=e,
                patient_info=getattr(self, "patient_info", {}),
                method_name="get_volume_of_roi_on_ct",
            )
            return None

    # === GET_ALL methods ===
    def get_all_current(self) -> Dict[str, Any]:
        """
        Collect all currently loaded RayStation objects and names.
    
        Works for both eager and lazy modes:
          - In eager mode, values are stored as attributes and also returned.
          - In lazy mode, values are simply returned.
    
        Returns:
            Dict[str, Any]: Dictionary containing all current-case objects and metadata.
        """
        results = {}
        for method_name in dir(self):
            if not method_name.startswith("get_current_"):
                continue
            key = method_name[12:]
            fn = getattr(self, method_name, None)
            if not callable(fn):
                _logger.debug("No method found for key '%s'", key)
                results[key] = None
                continue
    
            try:
                value = fn()
                # In eager mode this may be None, so fetch from attribute
                if value is None:
                    value = getattr(self, key, None)
                results[key] = value
            except Exception as e:
                _logger.error(f"Error in get_all_current for method %s and key %s: str{e}", method_name, key)
                _error_handling(
                    exc=e,
                    patient_info=getattr(self, "patient_info", {}),
                    method_name=method_name,
                )
                results[key] = None
    
        return results
    
    def get_all_plan_data(self) -> dict[str, Any] | None:
        """
        Get plan and beamset data for all treatment plans in the case.
    
        Iterates through all plans in the current case and collects their
        beamset-level data using :meth:`get_plan_data`. Each plan name is
        used as a key in the returned dictionary.
    
        Returns:
            dict[str, Any]: 
                Dictionary keyed by plan name, where each value is the
                corresponding output of :meth:`get_plan_data`.
        """
        try:
            all_plan_data = {
                plan.Name: self.get_plan_data(plan.Name)
                for plan in self.case.TreatmentPlans
            }
            return self._assign_if_eager("all_plan_data", all_plan_data)
        except Exception as e:
            _error_handling(
                exc=e, 
                patient_info=getattr(self, "patient_info", {}),
                method_name="get_all_plan_data",
            )
            return None
    
    def get_all(self) -> None:
        """
        Call every "no-arg" get_* methods on this object (except get_all itself),
        collect their data, and ensure the instance ends up hydrated.
    
        Behavior:
        - For each get_<thing>(), we infer <thing> as the attribute name.
        - We call get_<thing>() once.
            * In eager mode: that will cache to self.<thing> and often return None.
            * In lazy mode: that will return the value directly and NOT cache.
        - We then read the final value from either the return or from self.<thing>.
          If it's still not on self in lazy mode, we set it.
    
        Returns:
            None
            
        Notes: If eager mode is active, attributes assigned.
        """
        results = {}
        
        for method_name in dir(self):
            if not method_name.startswith("get_"):
                continue
            if method_name == "get_all":
                continue
            if method_name.startswith("get_current"):
                continue
    
            fn = getattr(self, method_name)
            if not callable(fn):
                continue
            
            # Skip methods that require arguments
            sig = inspect.signature(fn)
            params = sig.parameters
            if any(
                p.default == inspect.Parameter.empty and p.name != "self"
                for p in params.values()
            ):
                continue
            
            attr_name = method_name[4:]  # strip "get_"
            try:
                returned_value = fn()
            except Exception as e:
                _error_handling(
                    exc=e,
                    patient_info=getattr(self, "patient_info", {}),
                    method_name=method_name,
                )
                # on failure, record None and continue
                results[attr_name] = None
                continue
            
            value = (
                returned_value
                if returned_value is not None
                else getattr(self, attr_name, None)
            )
            results[attr_name] = value
    
            if self.eager and value is not None:
                setattr(self, attr_name, value)
    
        self._hydrated = True
        if not self.eager:
            return results
    
        return None
    
    # === HAS methods ===
    def has_case(self) -> bool:
        """
        Check whether a valid Case object is loaded.
    
        Returns:
            bool: True if a valid Case exists and is accessible, False otherwise.
        """
        try:
            if getattr(self, "case", None) is not None:
                return True
    
            _logger.warning("[PatientDataUtil] No active case found.")
            return False
    
        except Exception as e:
            _error_handling(
                exc=e,
                patient_info=getattr(self, "patient_info", {}),
                method_name="has_case",
            )
            return False

    def has_patient_model(self) -> bool:
        """
        Check whether the current case has a valid PatientModel object.
    
        Returns:
            bool: True if a valid PatientModel exists and is accessible, False otherwise.
        """
        try:
            if not self.has_case():
                False
            if not hasattr(self, "patient_model") or self.patient_model is None:
                self.patient_model = getattr(self.case, "PatientModel", None)
    
            if self.patient_model is None:
                _logger.warning(
                    "[PatientDataUtil] No PatientModel found in current case (%s).",
                    getattr(self, "patient_info", {}).get("case_name", "Unknown"),
                )
                return False
    
            return True
    
        except Exception as e:
            _error_handling(
                exc=e,
                patient_info=getattr(self, "patient_info", {}),
                method_name="has_patient_model",
            )
            return False
    
    def has_plans(self) -> bool:
        """
        Check if the current case contains one or more treatment plans.
    
        Returns:
            bool: 
                True if at least one treatment plan exists in the case; otherwise False.
        """
        try:
            if not self.has_case():
                return False
            treatment_plans = getattr(self.case, "TreatmentPlans", None)
            if treatment_plans is None:
                return False
    
            return len(treatment_plans) > 0
    
        except Exception as e:
            _error_handling(
                exc=e,
                patient_info=getattr(self, "patient_info", {}),
                method_name="has_plans",
            )
            return False

    def has_exams(self) -> bool:
        """
        Check if the current case contains one or more Examinations.
    
        Returns:
            bool: 
                True if at least one Examination exists in the case; 
                otherwise False.
        """
        try:
            if not self.has_case():
                return False
            exams = getattr(self.case, "Examinations", None)
            if exams is None:
                return False
    
            return len(exams) > 0
    
        except Exception as e:
            _error_handling(
                exc=e,
                patient_info=getattr(self, "patient_info", {}),
                method_name="has_exams",
            )
            return False

    def has_rois(self) -> bool:
        """
        Check if the current case contains at least one ROI.
    
        Returns:
            bool: 
                True if at least one ROI exists in the case; otherwise False.
        """
        try:
            if not self.has_patient_model():
                return False
            rois = getattr(self.patient_model, "RegionsOfInterest", None)
            if rois is None or len(rois) == 0:
                return False
            
            return True
    
        except Exception as e:
            _error_handling(
                exc=e,
                patient_info=getattr(self, "patient_info", {}),
                method_name="has_rois",
            )
            return False
        
    def has_plan_name(self, plan_name: str | None = None) -> bool:
        """
        Check if a treatment plan with the given name exists in the current case.
        
        Uses eager or lazy loading depending on object state to verify whether
        the specified plan name is present among the case's treatment plans.
        
        Args:
            plan_name (str): 
                Name of the treatment plan to check.
        
        Returns:
            bool: 
                True if the plan exists in the case; otherwise False.
        """
        try:
            if not plan_name:
                return None
            
            plan_names = self.get_plan_names()
            if not plan_names:
                return False
            return plan_name in plan_names
        except Exception as e:
            _error_handling(
                exc=e,
                patient_info=getattr(self, "patient_info", {}),
                method_name="has_plan_name",
            )
            return False
    
    
    def has_plan_beamset_name(self, plan_name: str | None = None, beamset_name: str | None = None) -> bool:
        """
        Check if a beamset with the given name exists within the specified treatment plan.
        
        Args:
            plan_name (str): 
                Name of the treatment plan to check.
            beamset_name (str): 
                DICOM plan label of the beamset to check.
        
        Returns:
            bool: 
                True if the beamset exists within the specified plan; otherwise False.
        """
        try:
            if not plan_name or not beamset_name:
                return False
            if not self.has_plan_name(plan_name):
                return False
    
            plan = next(
                (p for p in self.case.TreatmentPlans if getattr(p, "Name", None) == plan_name),
                None,
            )
            if plan is None:
                return False
    
            beamset_exists = any(
                getattr(bs, "DicomPlanLabel", None) == beamset_name
                for bs in getattr(plan, "BeamSets", [])
            )
    
            if not beamset_exists:
                return False
    
            return True

        except Exception as e:
            _error_handling(
                exc=e,
                patient_info=getattr(self, "patient_info", {}),
                method_name="has_plan_beamset_name",
            )
            return False

    def has_plan_beamset_beam_name(
            self, 
            plan_name: str | None = None, 
            beamset_name: str | None = None,
            beam_name: str | None = None,
    ) -> bool:
        """
        Check if a beam with the given name exists within the specified beamset-plan.
        
        Args:
            plan_name (str): 
                Name of the treatment plan to check.
            beamset_name (str): 
                DICOM plan label of the beamset to check.
            beam_name (str): 
                Name of the beam to check.
        
        Returns:
            bool: 
                True if the beam exists within the specified beamset-plan; otherwise False.
        """
        try:
            if not plan_name or not beamset_name or not beam_name:
                return False
            if not self.has_plan_beamset_name(plan_name, beamset_name):
                return False
    
            plan = next(
                (p for p in self.case.TreatmentPlans if getattr(p, "Name", None) == plan_name),
                None,
            )
            if plan is None:
                return False
            
            beamset = next(
                (bs for bs in plan.BeamSets if getattr(bs, "DicomPlanLabel", None) == beamset_name),
                None,
            )
            if beamset is None:
                return False
            
            beam_exists = any(
                getattr(b, "Name", None) == beam_name
                for b in getattr(beamset, "Beams", [])
            )
    
            if not beam_exists:
                return False
    
            return True

        except Exception as e:
            _error_handling(
                exc=e,
                patient_info=getattr(self, "patient_info", {}),
                method_name="has_plan_beamset_beam_name",
            )
            return False
    
    def has_dose_on_plan_beamset(self, plan_name: str | None = None, beamset_name: str | None = None) -> bool:
        """
        Check if a beamset with the given name has dose within the specified treatment plan's beamset.
        
        Args:
            plan_name (str): 
                Name of the treatment plan to check.
            beamset_name (str): 
                DICOM plan label of the beamset to check.
        
        Returns:
            bool: 
                True if the dose exists on the beamset within the specified plan; otherwise False.
        """
        try:
            if not plan_name or not beamset_name:
                return False
            if not self.has_plan_beamset_name(plan_name, beamset_name):
                return False
            
            plan = next((p for p in self.case.TreatmentPlans if p.Name == plan_name), None)
            if plan is None:
                return False
            
            beamset = next(
                (b for b in plan.BeamSets if b.DicomPlanLabel == beamset_name),
                None,
            )
            if beamset is None:
                return False
            
            fd = getattr(beamset, "FractionDose", None)
            if fd is None:
                return False
            if not hasattr(fd, "DoseValues"):
                return False
            return bool(fd.DoseValues)
        except Exception as e:
            _error_handling(
                exc=e,
                patient_info=getattr(self, "patient_info", {}),
                method_name="has_dose_on_plan_beamset",
            )
            return False
    
    def has_roi_external(self) -> bool:
        """
        Check whether an ROI of type 'External' exists in the current patient model.
    
        Returns:
            bool:
                True if an ROI of type 'External' exists; otherwise False.
        """
        try:
            return self._find_rois_by_type("External") is not None
    
        except Exception as e:
            _error_handling(
                exc=e,
                patient_info=getattr(self, "patient_info", {}),
                method_name="has_roi_external",
            )
            return False
    
    def has_roi_external_contour_on_ct(self, ct_exam_name: str | None = None) -> bool:
        """
        Check whether an external ROI has contours on a CT examination.
    
        Args:
            ct_exam_name (str): 
                The CT examination name of the structure set to check for the external contours.
                
        Return:
            Bool:
                True if external has contours; otherwise, False.
        """
        try:
            if not ct_exam_name:
                return False
            
            ext_name = self.get_roi_external_name()
            if not ext_name:
                return False
    
            return self.has_contours_on_ct(ext_name, ct_exam_name)
    
        except Exception as e:
            _error_handling(
                exc=e,
                patient_info=getattr(self, "patient_info", {}),
                method_name="has_roi_external_contour_on_ct",
            )
            return False
    
    # def has_for_registration(self) -> bool:
    #     """ DOC STRING HERE"""
    #     pass
    
    # def has_image_registration(self) -> bool:
    #     """ DOC STRING HERE"""
    #     pass
    
    def has_ct_exam_name(self, ct_exam_name: str | None = None) -> bool:
        """
        Check whether a CT examination with the given name exists in the current case.
    
        Args:
            ct_exam_name (str): 
                The CT examination name to check (e.g., "CT 1", "PlanningCT", etc.).
        """
        try:
            if not ct_exam_name:
                return False
            
            ct_exam_names = self.get_ct_exam_names()
    
            if not ct_exam_names:
                return False
    
            return ct_exam_name in ct_exam_names
    
        except Exception as e:
            _error_handling(
                exc=e,
                patient_info=getattr(self, "patient_info", {}),
                method_name="has_ct_exam_name",
            )
            return False
        
    def has_contours_on_ct(self, roi_name: str | None = None, ct_exam_name: str | None = None) -> bool:
        """
        Check whether a given ROI has any contours on a specific CT exam.
    
        Args:
            roi_name (str):
                Name of the ROI to check.
            ct_exam_name (str):
                The CT exam name (i.e. the StructureSet key).
    
        Returns:
            bool:
                True if that ROI exists on that CT and has at least one contour.
                False if the patient model is missing, the CT isn't found,
                the ROI isn't found on that CT, or on error.
        """
        try:
            if not roi_name or not ct_exam_name:
                return False
    
            if not self.has_patient_model():
                return False
    
            structure_sets = getattr(self.patient_model, "StructureSets", {})
            structure_set = structure_sets[ct_exam_name]
            if structure_set is None:
                return False
    
            roi_geometries = getattr(structure_set, "RoiGeometries", {})
            roi_geom = roi_geometries[roi_name]
            if roi_geom is None:
                return False
            return bool(roi_geom.HasContours())
    
        except Exception as e:
            _error_handling(
                exc=e,
                patient_info=getattr(self, "patient_info", {}),
                method_name="has_contours_on_ct",
            )
            return False
    
    # === NUM methods ===
    def num_plans(self) -> int:
        """
        Return the number of treatment plans in the current case.
    
        Returns:
            int:
                The number of treatment plans if available.
                Returns 0 if no case is loaded or on error.
        """
        try:
            plan_names = self.get_plan_names()
    
            if not plan_names:
                return 0
    
            return len(plan_names)
    
        except Exception as e:
            _error_handling(
                exc=e,
                patient_info=getattr(self, "patient_info", {}),
                method_name="num_plans",
            )
            return 0
    
    def num_rois(self) -> int:
        """
        Return the number of ROIs in the current case.
    
        Returns:
            int:
                The number of treatment ROIs if available.
                Returns 0 if no case is loaded or on error.
        """
        try:
            rois_names = self.get_roi_names()
    
            if not rois_names:
                return 0
    
            return len(rois_names)
    
        except Exception as e:
            _error_handling(
                exc=e,
                patient_info=getattr(self, "patient_info", {}),
                method_name="num_plans",
            )
            return 0
        
    def num_rois_with_contours_on_ct(self, ct_exam_name: str | None = None) -> int:
        """
        Return the number of ROIs with contours on the CT exam in the current case.
    
        Returns:
            int:
                The number of ROIs with contours on the CT exam if available.
                Returns 0 if no case is loaded or on error.
        """
        try:
            rois_with_contours = self.get_rois_with_contours_on_ct(ct_exam_name)
            if not rois_with_contours:
                return 0
    
            return len(rois_with_contours)
    
        except Exception as e:
            _error_handling(
                exc=e,
                patient_info=getattr(self, "patient_info", {}),
                method_name="num_rois_with_contours_on_ct",
            )
            return 0
        
    # === LIST methods ===
    def list_methods(self, include_doc=False) -> dict[str, str | None]:
        """
        Return a directory of all public methods in PatientDataUtil.
    
        Args:
            include_doc (bool): 
                If True, include the first line of each docstring.
    
        Returns:
            dict[str, str | None]: 
                Mapping of method names to doc summaries.
        """
        import inspect
        methods = {}
        for name, fn in inspect.getmembers(self, predicate=inspect.ismethod):
            if name.startswith("_"):
                continue
            if not callable(fn):
                continue
            if include_doc:
                doc = (inspect.getdoc(fn) or "").splitlines()[0] if fn.__doc__ else ""
                methods[name] = doc
            else:
                methods[name] = None
        return methods


 
# === DEBUG CODE ===
# Old code - Test\test_patient_data_util.py
def run_debug_tests():
    """Run the PatientDataUtil debug test suite manually after import."""
    import inspect
    import time
    from pprint import pformat
    
    import logging
    
    original_level = _logger.getEffectiveLevel()
    _logger.setLevel(logging.DEBUG)
    for h in _logger.handlers:
        h.setLevel(logging.DEBUG)
    _logger.debug("\n\n=== PatientDataUtil Debug Mode (manual) ===")

    try:
        
        def _capture_result(pdu_obj, method_name, call_return):
            """
            For get_* methods on an eager PatientDataUtil, prefer the hydrated attribute.
            For has_* / num_* methods, or anything else, just use the return value.
            """
            if method_name.startswith("get_"):
                attr_name = method_name.replace("get_", "", 1)
                if hasattr(pdu_obj, attr_name):
                    return getattr(pdu_obj, attr_name)
            if method_name.startswith("get_current_"):
                attr_name = method_name.replace("get_current_", "", 1)
                if hasattr(pdu_obj, attr_name):
                    return getattr(pdu_obj, attr_name)
            return call_return

        
        # === TESTING PATIENT INFO ===
        patient_id="9823461111"
        case_name="PatientDataUtil" #"PatientDataUtil"  "EmptyCase"
        plan_name = "photons_on_ct3" #"photons_on_ct3"   None
        
        pdu_lazy = PatientDataUtil(patient_id=patient_id, case_name=case_name, plan_name=plan_name, eager=False)
            
        # test get_all() in eager and preload snapshot
        try:
            preload_snapshot = pdu_lazy.get_all()
            _logger.debug("Preload snapshot keys: %s", list(preload_snapshot.keys()))
        except Exception as e:
            _logger.exception("Failed during get_all() preload: %s", e)
            preload_snapshot = {}

        # test in eager mode
        pdu = PatientDataUtil(eager=True)

        results = {}
        failed = []
        
        # Methods that *should* get tested with context args
        _CONTEXTUAL_METHODS  = {
            "has_ct_exam_name",
            "has_contours_on_ct",
            "has_dose_on_plan_beamset",
            "has_roi_external_contour_on_ct",
            "has_plan_name",
            "has_plan_beamset_name",
            "has_plan_beamset_dose",
            "get_plan_data",
            "get_ct_exam_name_in_plan_beamset",
            "get_dose_evaluations_on_ct",        
            "get_dose_evaluation_names_on_ct",
            "get_rois_with_contours_in_plan_beamset",
            "get_roi_names_with_contours_on_ct",
            "get_rois_with_contours_on_ct",
            "get_registration_number_from_name",
            "get_volume_of_roi_on_ct",
        }
        _SKIP_ZERO_ARG_FALSE_OPTIONALS = _CONTEXTUAL_METHODS

        # -------------------------------------------------
        # 1. Auto-test zero-argument public methods
        # -------------------------------------------------
        for name in dir(pdu):
            if name.startswith("_"):
                continue
            
            if name in _SKIP_ZERO_ARG_FALSE_OPTIONALS :
                continue
            
            method = getattr(pdu, name)
            if not callable(method):
                continue

            # Only test get_*, has_*, num_*, get_all
            if not (
                name.startswith(("get_", "has_", "num_"))
                or name in ("get_all",)
            ):
                continue

            # Skip methods that need required positional args
            sig = inspect.signature(method)
            if any(p.default is inspect._empty and p.name != "self" for p in sig.parameters.values()):
                continue

            t0 = time.time()
            try:
                val = method()
                dt = time.time() - t0
                norm_val = _capture_result(pdu, name, val)
                results[name] = norm_val
                assert not isinstance(val, Exception)
                _logger.debug("✅ %s() ok (%.3fs)", name, dt)
            except AssertionError as e:
                failed.append((name, str(e)))
                _logger.error("❌ %s() assertion failed: %s", name, e)
            except Exception as e:
                failed.append((name, str(e)))
                _error_handling(
                    exc=e,
                    patient_info=getattr(pdu, "patient_info", {}),
                    method_name=name,
                )

        # -------------------------------------------------
        # 2. Parameterized tests (auto)
        # -------------------------------------------------

        # Build a pool of realistic argument values from this patient/case
        context = {
            "plan_name": None,
            "beamset_name": None,
            "ct_exam_name": None,
            "roi_name": None, 
        }
        plan_names = getattr(pdu, "plan_names", None) or preload_snapshot.get("plan_names")
        if not context["plan_name"] and plan_names:
            context["plan_name"] = plan_names[-1]
        
        if context["plan_name"]:
            pdict = pdu.get_plan_data(context["plan_name"]) or {}
            if pdict:
                context["beamset_name"] = context["beamset_name"] or next(iter(pdict.keys()))
                beamset_info = pdict.get(context["beamset_name"], {})
                context["ct_exam_name"] = context["ct_exam_name"] or beamset_info.get("ct_exam_name")
        
        if context["ct_exam_name"]:
            rois = pdu.get_roi_names_with_contours_on_ct(context["ct_exam_name"]) or []
            if rois and not context["roi_name"]:
                context["roi_name"] = rois[0]


        _logger.debug("Context for parametrized methods: %s", context)

        # Map parameter names -> keys in context
        alias_map = {
            "plan_name": "plan_name",
            "beamset_name": "beamset_name",
            "ct_exam_name": "ct_exam_name",
            "roi_name": "roi_name",
        }

        def build_positional_args(name, sig):
            """Return (ok, args). ok=False if we can't satisfy required params."""
            args = []
            contextual = name in _CONTEXTUAL_METHODS
        
            for p in sig.parameters.values():
                if p.name == "self":
                    continue
        
                # Try to pull a value for this param from context via alias_map
                cand = None
                if p.name in alias_map:
                    cand = context.get(alias_map[p.name])
        
                if contextual:
                    # contextual method: every param is logically required
                    if cand is None:
                        return False, []
                    args.append(cand)
                else:
                    # non-contextual method: only params with no default are required
                    is_required = (p.default is inspect._empty)
                    if is_required and cand is None:
                        return False, []
                    if cand is not None:
                        args.append(cand)
                    # if optional and we have no cand, we just don't append it
        
            return True, args

        # Walk public methods and call anything whose required params we can satisfy
        for name in dir(pdu):
            if name.startswith("_"):
                continue
            if not name.startswith(("get_", "has_", "num_")):
                continue
            if name in ("get_all",):
                continue
        
            method = getattr(pdu, name, None)
            if not callable(method):
                continue
        
            sig = inspect.signature(method)
        
            # Decide if this method belongs in the param-driven section.
            # We include it if:
            # - it's explicitly contextual (in our allowlist), OR
            # - it has at least one truly required param (no default).
            has_truly_required = any(
                p.default is inspect._empty and p.name != "self"
                for p in sig.parameters.values()
            )
            if not (name in _CONTEXTUAL_METHODS or has_truly_required):
                continue
        
            ok, arg_list = build_positional_args(name, sig)
            if not ok:
                _logger.debug("Skipping %s(): missing context args.", name)
                continue
        
            t0 = time.time()
            try:
                val = method(*arg_list)
                dt = time.time() - t0
                norm_val = _capture_result(pdu, name, val)
                results[f"{name}{tuple(arg_list)}"] = norm_val
                assert not isinstance(val, Exception)
                _logger.debug("✅ %s%r ok (%.3fs)", name, tuple(arg_list), dt)
            except AssertionError as e:
                failed.append((name, str(e)))
                _logger.error("❌ %s%r assertion failed: %s", name, tuple(arg_list), e)
            except Exception as e:
                failed.append((name, str(e)))
                _error_handling(
                    exc=e,
                    patient_info=getattr(pdu, "patient_info", {}),
                    method_name=name,
                )
                _logger.error("❌ %s%r failed: %s", name, tuple(arg_list), e)

        # -------------------------------------------------
        # 3. Test clear()
        # -------------------------------------------------
        try:
            pdu.clear()
            _logger.debug("✅ clear() ok")
        except Exception as e:
            failed.append(("clear", str(e)))
            _logger.error("❌ clear() failed: %s", e)


        # -------------------------------------------------
        # Summary
        # -------------------------------------------------
        _logger.debug("=== Debug summary ===")
        _logger.debug(pformat(results))
        _logger.debug("Hydrated = %s", pdu._hydrated)

        if failed:
            _logger.warning(
                "⚠️ %d method(s) failed during debug: %s",
                len(failed),
                [f[0] for f in failed]
            )
        else:
            _logger.debug("✅ All tested methods executed successfully.")

    except Exception as e:
        _logger.exception("🚨 Initialization failed during module debug: %s", e)

    finally:
      _logger.setLevel(original_level)
      for h in _logger.handlers:
          h.setLevel(original_level)
      _logger.info("Logger level restored to %s", logging.getLevelName(original_level))

    
    
