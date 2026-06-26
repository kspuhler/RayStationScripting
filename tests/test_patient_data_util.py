"""
Tests\test_patient_data_util.py

Simple debug assertions for PatientDataUtil.

Usage:
    Open test_patient_data_util inside RayStation create script and run with
    an environemnt with PyQt5 enabled.

Adding Methods for Testing:
    1. If the method requires input(s), add it to METHOD_WITH_INPUTS
    2. If a needed input is not in the TESTING PATIENT INFO section, add it (never delete/change)
    3. If the method requires conversion to get a useful output, add it to one of 
        the lists in the section "Methods requiring conversion".
    4. Add method and expected output to the EXPECTED dictionary.
    5. If a conversion method does not exist in the section "Methods requiring conversion",
        a new "_convert_to_*" method will need to be created in the Convert methods section.

Notes: All results are logged in system.log

Created on Thu Oct 30 16:54:34 2025

@author: clanco01
"""

from __future__ import annotations

# === DEBUG SETTINGS ===
_DEBUG_THIS_MODULE = False

# === Raystation import ===
try:
    from connect import await_user_input
except Exception:
    pass

# === Standard Imports ===
from typing import Any, Dict, List

# === WORKING DIRECTORY ===
import sys
sys.path.append(r"\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
sys.path.append(r"F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")

# === Local imports ===
from RSutil.patient_data_util import PatientDataUtil

# === Logger setup ===
from RSutil.LogUtil.rs_logging import LOGGERS, set_logger_mode
_logger = LOGGERS["system"]
if _DEBUG_THIS_MODULE:
    set_logger_mode(_logger, "debug")

# === TESTING PATIENT INFO - Inputs for Methods ===
'''
Declared variables used in METHOD_WITH_INPUTS.

Usage: patient_id/case_name is strictly fixed.  Only add variables.
'''
patient_id = "9823461111" # DO NOT CHANGE
case_name = "PatientDataUtil" # DO NOT CHANGE
plan_name = "photons_on_ct3"
beamset_name = "beamset_on_ct3"
beam_name = "2 VMAT"
ct_exam_name = "CT 3"
roi_name = "Brain"
roi_name_check = "ROI_Only_on_CT3"
plan_name_for_beamset_name_check = "photons_on_ct2"
include_doc = False
center_coord_roi_name = "External"
exam = None

# === Methods requiring inputs ===
'''
Dictionary of methods that require inputs.

Schema: {..., str(method_name): list[input1, input2, ...], ...}
'''

METHOD_WITH_INPUTS = {
    "get_beam_names_in_plan_beamset": [plan_name, beamset_name],
    "get_beamsets_in_plan": [plan_name_for_beamset_name_check],
    "get_beamset_in_plan": [plan_name, beamset_name],
    "get_beamset_names_in_plan": [plan_name_for_beamset_name_check],
    "get_ct_exam_in_plan": [plan_name],
    "get_ct_exam_name_in_plan": [plan_name],
    "get_ct_exam_name_in_plan_beamset": [plan_name, beamset_name],
    "get_dose_evaluation_names_on_ct": [ct_exam_name],
    "get_dose_evaluations_on_ct": [ct_exam_name], 
    "get_exam_name_from_exam": [exam],
    "get_exam_with_exam_name": [ct_exam_name],
    "get_iso_in_plan_beamset_beam": [plan_name, beamset_name, beam_name],
    "get_machine_in_plan_beamset": [plan_name, beamset_name],
    "get_plan_data": [plan_name],
    "get_roi_center_coord_on_ct": [center_coord_roi_name, ct_exam_name],
    "get_roi_external_on_ct": [ct_exam_name],
    "get_roi_names_with_contours_on_ct": [ct_exam_name],
    "get_roi_on_ct": [roi_name, ct_exam_name],
    "get_rois_on_ct": [ct_exam_name],
    "get_rois_with_contours_in_plan_beamset": [plan_name, beamset_name],
    "get_rois_with_contours_on_ct": [ct_exam_name],
    "get_volume_of_roi_on_ct": [roi_name, ct_exam_name],
    "has_contours_on_ct": [roi_name_check, ct_exam_name],
    "has_ct_exam_name": [ct_exam_name],
    "has_dose_on_plan_beamset": [plan_name, beamset_name],
    "has_plan_beamset_beam_name": [plan_name, beamset_name, beam_name],
    "has_plan_beamset_name": [plan_name, beamset_name],
    "has_plan_name": [plan_name],
    "has_roi_external_contour_on_ct": [ct_exam_name],
    "list_methods": [include_doc],
    "num_rois_with_contours_on_ct": [ct_exam_name],
}

# === Methods requiring conversion ===
METHODS_TEST_LIST = ["list_methods"]

METHODS_CONVERT_TO_BOOL = ["get_current_patient_model", "get_current_patient_db"]

METHODS_CONVERT_TO_CASE_NAME = ["get_current_case",]

METHODS_CONVERT_PLAN_DATA = ["get_current_plan_data", "get_plan_data",]

METHODS_CONVERT_ALL_PLAN_DATA = ["get_all_plan_data",]

METHODS_CONVERT_ROIS_TO_NAME = [
    "get_current_rois_with_contours",
    "get_roi_external_on_ct",
    "get_roi_on_ct",
    "get_rois_on_ct",
    "get_rois_with_contours_on_ct",
    "get_rois_with_contours_in_plan_beamset",
]

METHODS_CONVERT_TO_LIST = [
    "get_beamset_in_plan",
    "get_beamsets_in_plan",
    "get_beamsets_non_photon",
    "get_ct_exam_in_plan",
    "get_ct_exams",
    "get_current_beams",
    "get_current_beamset",
    "get_current_exam",
    "get_current_plan",
    "get_exams",
    "get_exam_with_exam_name",
    "get_mr_exams",
    "get_pet_exams",
    "get_plans",
]

METHODS_CONVERT_DOSE_EVAL_TO_LIST = ["get_dose_evaluations_on_ct", "get_dose_evaluations",]

METHODS_CONVERT_TO_PATIENT_ID = ["get_current_patient",]

METHODS_CONVERT_ALL_CURRENT_DATA = ["get_all_current",]

# === Expected dictionary of outputs
EXPECTED = {
    "get_all": None,
    "get_all_current": {
        "beam_names": ["1 VMAT", "2 VMAT"],
        "beams": ["1 VMAT", "2 VMAT"],
        "beamset": ["beamset_on_ct3"],
        "beamset_name": "beamset_on_ct3",
        "case": case_name,
        "exam": ["CT 3"],
        "exam_name": "CT 3",
        "patient": patient_id,
        "patient_db": True,
        "patient_model": True,
        "plan": ["photons_on_ct3"],
        "plan_data": {
            "beamset_on_ct3": {
                "plan_name": "photons_on_ct3",
                "beamset": ["beamset_on_ct3"],
                "beamset_name": "beamset_on_ct3",
                "delivery_technique": "DynamicArc",
                "dose_object": True,
                "dose_rx": 4500.0,
                "fractions": 25,
                "ct_object": ["CT 3"],
                "ct_exam_name": "CT 3",
                "machine": "TrueBeamSN1106",
                "modality": "Photons",
                "patient_position": "FeetFirstSupine",
                "plan_generation_technique": "Imrt",
            }
        },
        "plan_name": "photons_on_ct3",
        "roi_names_with_contours": ["Brain", "External", "ROI_Only_on_CT3"],
        "rois_with_contours": ["Brain", "External", "ROI_Only_on_CT3"]
    },
    "get_all_plan_data": {
        "electron_on_ct1": {
            "electron_on_ct1": {
                "plan_name": "electron_on_ct1",
                "beamset": ["electron_on_ct1"],
                "beamset_name": "electron_on_ct1",
                "delivery_technique": "SMLC",
                "dose_object": True,
                "dose_rx": 1000.0,
                "fractions": 5,
                "ct_object": ["CT 1"],
                "ct_exam_name": "CT 1",
                "machine": "21EX",
                "modality": "Electrons",
                "patient_position": "HeadFirstSupine",
                "plan_generation_technique": "Conformal",
            }
        },
        "photons_on_ct2": {
            "photons_on_ct2": {
                "plan_name": "photons_on_ct2",
                "beamset": ["photons_on_ct2"],
                "beamset_name": "photons_on_ct2",
                "delivery_technique": "SMLC",
                "dose_object": True,
                "dose_rx": 3000.0,
                "fractions": 10,
                "ct_object": ["CT 2"],
                "ct_exam_name": "CT 2",
                "machine": "21EX",
                "modality": "Photons",
                "patient_position": "HeadFirstSupine",
                "plan_generation_technique": "Conformal",
            },
            "photons_on_ct2_2": {
                "plan_name": "photons_on_ct2",
                "beamset": ["photons_on_ct2_2"],
                "beamset_name": "photons_on_ct2_2",
                "delivery_technique": "SMLC",
                "dose_object": True,
                "dose_rx": 1000.0,
                "fractions": 1,
                "ct_object": ["CT 2"],
                "ct_exam_name": "CT 2",
                "machine": "TrueBeamSN1106",
                "modality": "Photons",
                "patient_position": "HeadFirstSupine",
                "plan_generation_technique": "Conformal",
            }
        },
        "photons_on_ct3": {
            "beamset_on_ct3": {
                "plan_name": "photons_on_ct3",
                "beamset": ["beamset_on_ct3"],
                "beamset_name": "beamset_on_ct3",
                "delivery_technique": "DynamicArc",
                "dose_object": True,
                "dose_rx": 4500.0,
                "fractions": 25,
                "ct_object": ["CT 3"],
                "ct_exam_name": "CT 3",
                "machine": "TrueBeamSN1106",
                "modality": "Photons",
                "patient_position": "FeetFirstSupine",
                "plan_generation_technique": "Imrt",
            }
        }
    },
    "get_beam_names_in_plan_beamset": ["1 VMAT", "2 VMAT"],
    "get_beamset_in_plan": ["beamset_on_ct3"],
    "get_beamsets_in_plan": ["photons_on_ct2", "photons_on_ct2_2"],
    "get_beamset_names_in_plan": ["photons_on_ct2", "photons_on_ct2_2"],
    "get_beamsets_non_photon": ["electron_on_ct1"],
    "get_ct_exam_in_plan": ["CT 3"],
    "get_ct_exam_name_in_plan_beamset": "CT 3",
    "get_ct_exam_name_in_plan": "CT 3",
    "get_ct_exam_names": ["CT 3", "CT 2", "CT 1"],
    "get_ct_exams": ["CT 3", "CT 2", "CT 1"],
    "get_current_beam_names": ["1 VMAT", "2 VMAT"],
    "get_current_beams": ["1 VMAT", "2 VMAT"],
    "get_current_beamset": ["beamset_on_ct3"],
    "get_current_beamset_name": "beamset_on_ct3",
    "get_current_case": case_name,
    "get_current_exam": ["CT 3"],
    "get_current_exam_name": "CT 3",
    "get_current_patient": patient_id,
    "get_current_patient_db": True,
    "get_current_patient_model": True,
    "get_current_plan": ["photons_on_ct3"],
    "get_current_plan_data": {
        "beamset_on_ct3": {
            "beamset": ["beamset_on_ct3"],
            "beamset_name": "beamset_on_ct3",
            "delivery_technique": "DynamicArc",
            "dose_object": True,
            "dose_rx": 4500.0,
            "fractions": 25,
            "ct_object": ["CT 3"],
            "ct_exam_name": "CT 3",
            "machine": "TrueBeamSN1106",
            "modality": "Photons",
            "patient_position": "FeetFirstSupine",
            "plan_generation_technique": "Imrt",
            "plan_name": "photons_on_ct3"
        }
    },
    "get_current_plan_name": "photons_on_ct3",
    "get_current_roi_names_with_contours": ["Brain", "External", "ROI_Only_on_CT3"],
    "get_current_rois_with_contours": ["Brain", "External", "ROI_Only_on_CT3"],
    "get_deformable_registration_names": ["Deform_Test_1", "Deform_Test_2"],
    "get_dose_evaluation_names_on_ct": ["photons_on_ct3","beamset_on_ct3"],
    "get_dose_evaluations_on_ct": ["photons_on_ct3","beamset_on_ct3"],
    "get_dose_evaluations": ["photons_on_ct3","beamset_on_ct3", "photons_on_ct2", "Summed dose 1"],
    "get_dose_evaluation_names": ["photons_on_ct3","beamset_on_ct3", "photons_on_ct2", "Summed dose 1"],
    "get_exam_name_from_exam": "CT 3",
    "get_exam_with_exam_name": ["CT 3"],
    "get_exams": ["MR 3", "CT 3", "MR 2", "MR 1", "CT 2", "CT 1", "PET 1"],
    "get_exam_names": ["MR 3", "CT 3", "MR 2", "MR 1", "CT 2", "CT 1", "PET 1"],
    "get_iso_in_beam": {'x': -0.18908613205732813, 'y': 2.4256388669123643, 'z': -1.162905763108968},
    "get_iso_in_plan_beamset_beam": {'x': -0.18908613205732813, 'y': 2.4256388669123643, 'z': -1.162905763108968},
    "get_machine_in_plan_beamset": "TrueBeamSN1106",
    "get_mr_exam_names": ["MR 3", "MR 2", "MR 1"],
    "get_mr_exams": ["MR 3", "MR 2", "MR 1"],
    "get_ct_exam_name_newest": "CT 3",
    "get_pet_exam_names": ["PET 1"],
    "get_pet_exams": ["PET 1"],
    "get_plan_data": {
        "beamset_on_ct3": {
            "beamset": ["beamset_on_ct3"],
            "beamset_name": "beamset_on_ct3",
            "delivery_technique": "DynamicArc",
            "dose_object": True,
            "dose_rx": 4500.0,
            "fractions": 25,
            "ct_object": ["CT 3"],
            "ct_exam_name": "CT 3",
            "machine": "TrueBeamSN1106",
            "modality": "Photons",
            "patient_position": "FeetFirstSupine",
            "plan_generation_technique": "Imrt",
            "plan_name": "photons_on_ct3"
        }
    },
    "get_plan_names": ["electron_on_ct1", "photons_on_ct2", "photons_on_ct3"],
    "get_plans": ["electron_on_ct1", "photons_on_ct2", "photons_on_ct3"],
    "get_roi_center_coord_on_ct": {'x': -0.7032601357035377, 'y': 1.793381509680365, 'z': -14.502422937945969},
    "get_roi_external_name": "External",
    "get_roi_external_on_ct": ["External"],
    "get_roi_names": [
        "Brain",
        "External",
        "ROI_Only_on_CT2",
        "ROI_Only_on_CT1",
        "ROI_Only_on_CT3"
    ],
    "get_roi_names_with_contours_on_ct": ["Brain", "External", "ROI_Only_on_CT3"],
    "get_roi_on_ct": ["Brain"],
    "get_rois_on_ct": [
        "Brain",
        "External",
        "ROI_Only_on_CT2",
        "ROI_Only_on_CT1",
        "ROI_Only_on_CT3"
    ],
    "get_rois_with_contours_in_plan_beamset": ["Brain", "External", "ROI_Only_on_CT3"],
    "get_rois_with_contours_on_ct": ["Brain", "External", "ROI_Only_on_CT3"],
    "get_volume_of_roi_on_ct": 1425.9666724111519,
    "has_case": True,
    "has_contours_on_ct": True,
    "has_ct_exam_name": True,
    "has_dose_on_plan_beamset": True,
    "has_exams": True,
    "has_patient_model": True,
    "has_plan_beamset_beam_name": True,
    "has_plan_beamset_name": True,
    "has_plan_name": True,
    "has_plans": True,
    "has_roi_external": True,
    "has_roi_external_contour_on_ct": True,
    "has_rois": True,
    "num_plans": 3,
    "num_rois": 5,
    "num_rois_with_contours_on_ct": 3,
    "list_methods": True,
    "clear": True,
}

# === Helper function ===
def _capture_result(pdu_obj: "PatientDataUtil", method_name: str, call_return: Any) -> Any:
    """
    Normalize method return values for eager mode.

    Many get_* methods assign results to attributes and return None when
    eager=True. This helper fetches the hydrated attribute in those cases.

    Args:
        pdu_obj (PatientDataUtil): Instance on which the method was called.
        method_name (str): Name of the executed method (e.g., 'get_plan_data').
        call_return (Any): Raw return value from the method call.

    Returns:
        Any: The method's actual result, preferring the hydrated attribute if
        the call returned None.
    """
    if call_return is not None:
        return call_return
    # Map method name -> attribute name
    if method_name.startswith("get_current_"):
        attr = method_name[len("get_current_"):]
    elif method_name.startswith("get_"):
        attr = method_name[len("get_"):]
    else:
        return call_return
    return getattr(pdu_obj, attr, None)

# ==== Convert methods - internal use only ===
def _convert_to_beam(result: Any) -> Any:
    """
    Convert the result into a beam object

    Parameters
    ----------
    result : Any
        DESCRIPTION.

    Returns
    -------
    Any
        DESCRIPTION.

    """
    
def _convert_to_list(result: Any) -> List:
    """
    Converts the result into a list of names.

    Args:
        result (Any): output result of current method.

    Returns:
        list: list of names.
    """
    result_list = []
    try:
        try:
            result_list = [result.Name for result in result]
        except Exception:
            result_list = [result.DicomPlanLabel for result in result]
    except Exception:
        try:
            result_list = [result.Name]
        except Exception:
            result_list = [result.DicomPlanLabel]
    return result_list

def _convert_to_bool(result: Any) -> bool:
    """
    Converts the result into a boolean for assertion comparision.

    Args:
        result (Any): output result of current method.

    Returns:
        bool: True if the result exists.  Otherwise, False.
    """
    if result:
        return True
    else:
        return False

def _convert_patient(result: Any) -> str:
    """
    Converts the RayStation Patient into a string of the Patient ID.

    Args:
        result (Any): output result of current method.

    Returns:
        str: string of Patient ID.
    """
    return result.PatientID

def _convert_case(result: Any) -> str:
    """
    Converts the RayStation Case into a string of the case name.

    Args:
        result (Any): output result of current method.

    Returns:
        str: string of Case name.
    """
    return result.CaseName

def _convert_rois(result: Any) -> List:
    """
    Converts the ROIs from RayStation into a list of ROI names.

    Args:
        result (Any): output result of current method.

    Returns:
        list: list of ROI names.
    """
    if not isinstance(result, list):
        _logger.debug("None list result inside _convert_rois(): %s", result)
        try:
            result = list(result)
        except Exception:
            result = [result]
        _logger.debug("Converted to list result in _convert_rois(): %s", result)
        
    return [roi.OfRoi.Name for roi in result]

def _convert_dose_eval_to_list(result: Any) -> List:
    """
    Converts the dose evaluation result into a list of its names.

    Args:
        result (Any): output result of current method.

    Returns:
        list: list of dose evaluation names.
    """
    return [dose_eval.Name for dose_eval in result]

def _convert_plan_data(result: Any) -> Any:
    """
    Converts the plan_data result into a comparable result for assertion.

    Args:
        result (Any): output result of current method.

    Returns:
        result: convert result to verifiable result for comparison
    """
    _logger.debug("result for converting plan data: %s", result)
    for key, beamset in result.items():
        if "beamset" in beamset:
            _logger.debug("Converting beamset to list for %s", beamset["beamset"])
            beamset["beamset"] = _convert_to_list(beamset["beamset"])
        if "dose_object" in beamset:
            _logger.debug("Converting dose_object to bool for %s", beamset["dose_object"])
            beamset["dose_object"] = _convert_to_bool(beamset["dose_object"])
        if "ct_object" in beamset:
            _logger.debug("Converting ct_object to list for %s", beamset["ct_object"])
            beamset["ct_object"] = _convert_to_list(beamset["ct_object"])
    return result
        
def _convert_all_plan_data(result: Any) -> Any:
    """
    Converts the all_plan_data result into a comparable result for assertion.

    Args:
        result (Any): output result of current method.

    Returns:
        result: convert items to verifiable result for comparison
    """
    for key, plan in result.items():
        plan = _convert_plan_data(plan)
    return result

def _convert_all_current(result: Any) -> Any:
    """
    Converts the get_all_current result into a comparable result for assertion.

    Args:
        result (Any): output result of current method.

    Returns:
        result: convert items to verifiable result for comparison
    """
    for key, item in result.items():
        if key in ["beams", "beamset", "exam", "plan",]:
            result[key] = _convert_to_list(item)
        elif key == "case":
            result[key] = _convert_case(item)
        elif key == "patient":
            result[key] = _convert_patient(item)
        elif key in ["patient_db", "patient_model"]:
            result[key] = _convert_to_bool(item)
        elif key == "plan_data":
            result[key] = _convert_plan_data(item)
        elif key == "rois_with_contours":
            result[key] = _convert_rois(item)
    return result

def _test_list_methods(pdu, EXPECTED: dict[str, None]) -> bool:
    """
    Verify that PatientDataUtil.list_methods() correctly lists all public methods.

    Args:
        pdu (PatientDataUtil): An instance of PatientDataUtil.
        EXPECTED (dict): Dictionary of expected method names as keys.

    Returns:
        bool: True if all expected methods are present and no unexpected extras, False otherwise.
    """
    try:
        # Get all listed methods from the object
        listed = pdu.list_methods(include_doc=False)
        listed_keys = set(listed.keys())
        expected_keys = set(EXPECTED.keys())

        # --- Compare sets ---
        missing = expected_keys - listed_keys
        extra = listed_keys - expected_keys
        
        _logger.debug(expected_keys)
        _logger.debug(listed_keys)

        if missing:
            _logger.error(f"❌ Missing methods in list_methods(): {sorted(missing)}")
        if extra:
            _logger.error(f"⚠️ Unexpected extra methods returned: {sorted(extra)}")

        # --- Return boolean result ---
        if not missing and not extra:
            print("✅ list_methods() includes all expected methods.")
            return True
        else:
            return False

    except Exception as e:
        _logger.error(f"❌ list_methods() test failed with exception: {e}")
        return False

# === Specific convert method for clear() ===
def _test_clear_method(pdu) -> bool:
    """
    Test whether PatientDataUtil.clear() correctly resets attributes.

    Args:
        pdu (PatientDataUtil): An initialized PatientDataUtil instance.

    Returns:
        bool: True if all checks pass, False if any assertion fails.
    """
    try:
        # --- Capture config values before clearing ---
        eager_before = getattr(pdu, "eager", None)
        patient_info_before = getattr(pdu, "patient_info", None)

        # --- Call clear ---
        pdu.clear(keep_config=True)

        # --- Verify dynamic attributes ---
        for name, value in vars(pdu).items():
            if name in pdu._KEEP_FIELDS:
                continue
            if name.startswith("_"):
                continue

            if value is not None:
                _logger.error(f"❌ Attribute '{name}' not cleared (value={value!r})")
                return False

        # --- Verify config and internal fields ---
        if pdu._hydrated is not False:
            _logger.error("❌ _hydrated was not reset to False")
            return False

        if pdu.eager != eager_before:
            _logger.error("❌ eager flag was not preserved")
            return False

        if pdu.patient_info != patient_info_before:
            _logger.error("❌ patient_info was not preserved")
            return False

        return True

    except Exception as e:
        _logger.error(f"❌ clear() test failed with exception: {e}")
        return False

# === Main test method ===
def run_expected_tests(EXPECTED: dict) -> None:
    """Run simple assertions comparing PatientDataUtil outputs to EXPECTED values."""
    pdu = PatientDataUtil(patient_id=patient_id, case_name=case_name, plan_name=plan_name, eager=True)
    passed, failed = [], []
    exams = pdu.get_ct_exams()
    METHOD_WITH_INPUTS["get_exam_name_from_exam"] = exams[0]
    case = pdu.get_current_case()
    beam = case.TreatmentPlans["photons_on_ct3"].BeamSets["beamset_on_ct3"].Beams["1 VMAT"]
    
    _logger.info("\n\n=== Starting tests for patient_data_util.py ===")
    try:
        _logger.debug("Setting 'CT 3' to primary for testing...")
        pdu.case.Examinations["CT 3"].SetPrimary()
    except Exception as e:
        _logger.warning("[FAILED] to set 'CT 3' to primary for testing: %s", str(e))

    for method_name, expected in EXPECTED.items():
        try:
            # Skip clear method
            if method_name == "clear":
                continue
            
            # Get method reference
            method = getattr(pdu, method_name, None)
            if not callable(method):
                _logger.info(f"⚠️  Skipping {method_name}: not callable")
                continue

            # Run method (handle both get_all and those requiring inputs)
            if method_name in METHOD_WITH_INPUTS:
                args = METHOD_WITH_INPUTS[method_name]
                
                if method_name == "get_exam_name_from_exam":
                    _logger.debug("get_exam_name_from_exam method argument: %s", args)
                    _logger.debug("Input exam name is: %s", args.Name)
                
                _logger.debug("Arguments for %s: %s", method_name, args)
                try:
                    raw_result = method(*args)
                except Exception:
                    raw_result = method(args)
            elif method_name == "get_iso_in_beam":
                raw_result = method(beam)
            else:
                raw_result = method()
            
            result = _capture_result(pdu, method_name, raw_result)
            _logger.debug("Method name and result before conversion: %s || %s", method_name, result)
            if method_name in METHODS_CONVERT_TO_LIST:
                result = _convert_to_list(result)
            
            elif method_name in METHODS_CONVERT_TO_BOOL:
                result = _convert_to_bool(result)
                
            elif method_name in METHODS_CONVERT_ROIS_TO_NAME:
                result = _convert_rois(result)
            
            elif method_name in METHODS_CONVERT_TO_PATIENT_ID:
               result = _convert_patient(result)
            
            elif method_name in METHODS_CONVERT_DOSE_EVAL_TO_LIST:
                result = _convert_dose_eval_to_list(result)
            
            elif method_name in METHODS_CONVERT_TO_CASE_NAME:
                result = _convert_case(result)
            
            elif method_name in METHODS_CONVERT_ALL_PLAN_DATA:
                result = _convert_all_plan_data(result)
                
            elif method_name in METHODS_CONVERT_PLAN_DATA:
                result = _convert_plan_data(result)
                
            elif method_name in METHODS_CONVERT_ALL_CURRENT_DATA:
                result = _convert_all_current(result)
            
            elif method_name in METHODS_TEST_LIST:
                result = _test_list_methods(pdu, EXPECTED)
            
            # Compare
            if result == expected:
                _logger.info(f"✅ {method_name}: passed")
                passed.append(method_name)
            else:
                _logger.error(f"❌ {method_name}: failed\n  Expected: {expected}\n  Got: {result}")
                failed.append(method_name)

        except Exception as e:
            _logger.error(f"💥 {method_name} raised {e}")
            failed.append(method_name)

    # Test clear()
    try:
        result = _test_clear_method(pdu)
        if result == EXPECTED["clear"]:
            _logger.info("✅ clear: passed")
            passed.append(method_name)
        else:
            _logger.error("❌ clear: failed\n  Expected: True\n  Got: False")
            failed.append(method_name)
    except Exception as e:
        failed.append(("clear", str(e)))
        _logger.error("❌ clear() failed: %s", e)

    _logger.info("\n\n=== Summary ===")
    _logger.info(f"✅ Passed: {len(passed)}")
    _logger.info(f"❌ Failed: {len(failed)} -> {failed if failed else 'None'}")

if __name__ == "__main__":
    try:
        run_expected_tests(EXPECTED)
    except ImportError:
        _logger.error("Please import EXPECTED dictionary from your expected_values module.")
    finally:
        message = "To verify execution, check: 'system.log' --> F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD\Logs "
        await_user_input(message=message)

