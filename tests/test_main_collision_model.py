"""
tests/test_main_collision_model.py

Minimal  tests for the Collision Model script.
Intended to run inside the RayStation.

Plans expected to exist listed in Constants

Expected behavior:
  - For Test_21EX / Test_TB / Test_Rad / Test_Multi_BeamSets:
      CollisionModel.main() returns a numeric volume (cc) you can compare to expected.
  - For Test_Multi_Machines / Test_CK / Test_No_Beams / Test_Pass:
      CollisionModel.main() returns False (failure).
  - For Test_Pass:
      CollisionModel.main() returns True (pass).

Created on Thu Jan  8 15:46:20 2026

@author: clanco01
"""

from __future__ import annotations

# === WORKING DIRECTORY ===
import sys
sys.path.append(r"\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
sys.path.append(r"F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")

# === Local imports ===
from collision_model.main_collision_model import CollisionModel
from RSutil.patient_data_util import PatientDataUtil

# === Logger setup ===
from RSutil.LogUtil.rs_logging import LOGGERS
_logger = LOGGERS["system"]

# ==== Constants ===

# Plan data
PATIENT_ID = "0000Collision"
CASE_NAME = "Test_Model"
TEST_PLAN_NAME_21EX = "Test_21EX"
TEST_PLAN_NAME_TB = "Test_TB"
TEST_PLAN_NAME_RAD = "Test_Rad"
TEST_PLAN_NAME_MULTI_BEAMSETS = "Test_Multi_BeamSets"
TEST_PLAN_NAME_MULTI_MACHINES = "Test_Multi_Machines"
TEST_PLAN_NAME_CK = "Test_CK"
TEST_PLAN_NAME_NO_BEAMS = "Test_No_Beams"
TEST_PLAN_NAME_PASS = "Test_Pass"

# Volume assertion values
VOL_21EX = 1279.18
VOL_TB = 16511.28
VOL_RAD = 6343.18
VOL_VMAT = 8559.69
VOL_3D = 3732.84

# Volume epsilon tolerance
EPS = 0.01

# Output suppression
DISPLAY_OUTPUT = False

# ---------------------------
# Helpers
# ---------------------------

def _select_plan_by_name(plan_name: str) -> None:
    """
    Select/open the plan in RayStation by name so CollisionModel.main() operates on it.
    """
    pdu = PatientDataUtil(patient_id=PATIENT_ID, case_name=CASE_NAME, plan_name=plan_name)
    pdu.get_current_patient_model()
    return pdu


def _assert_close(actual: float, expected: float, tol: float = EPS) -> None:
    assert abs(actual - expected) <= tol, f"Expected {expected} ± {tol}, got {actual}"

def delete_rois(pdu) -> None:
    pm = pdu.get_current_patient_model()
    roi_names = pdu.get_roi_names()
    for roi_name in roi_names:
        if roi_name.startswith("COLL_"):
            pm.RegionsOfInterest[roi_name].DeleteRoi()

# ---------------------------
# Tests
# ---------------------------

def test_test_21ex():
    pdu = _select_plan_by_name(TEST_PLAN_NAME_21EX)

    try:
        result = CollisionModel(display_output=DISPLAY_OUTPUT).main()
        vol = result["failures"][0]["collision_volume_cc"]
    
        assert isinstance(vol, (int, float)), f"Expected numeric volume return, got {type(vol)}"
        _assert_close(float(vol), VOL_21EX)
    
    finally:
        delete_rois(pdu)


def test_test_tb():
    pdu = _select_plan_by_name(TEST_PLAN_NAME_TB)

    try:
        result = CollisionModel(display_output=DISPLAY_OUTPUT).main()
        vol = result["failures"][0]["collision_volume_cc"]
    
        assert isinstance(vol, (int, float)), f"Expected numeric volume return, got {type(vol)}"
        _assert_close(float(vol), VOL_TB)
    
    finally:
        delete_rois(pdu)


def test_test_rad():
    pdu = _select_plan_by_name(TEST_PLAN_NAME_RAD)
    try:
        result = CollisionModel(display_output=DISPLAY_OUTPUT).main()
        vol = result["failures"][0]["collision_volume_cc"]
    
        assert isinstance(vol, (int, float)), f"Expected numeric volume return, got {type(vol)}"
        _assert_close(float(vol), VOL_RAD)
        
    finally:
        delete_rois(pdu)
    
def test_test_multi_beamsets():
    pdu = _select_plan_by_name(TEST_PLAN_NAME_MULTI_BEAMSETS)

    try:
        result = CollisionModel(display_output=DISPLAY_OUTPUT).main()
        vol_0 = result["failures"][0]["collision_volume_cc"]
        vol_1 = result["failures"][1]["collision_volume_cc"]
    
        assert isinstance(vol_0, (int, float)), f"Expected numeric volume return, got {type(vol_0)}"
        _assert_close(float(vol_0), VOL_3D)
        
        assert isinstance(vol_1, (int, float)), f"Expected numeric volume return, got {type(vol_1)}"
        _assert_close(float(vol_1), VOL_VMAT)
    
    finally:   
        delete_rois(pdu)


def test_test_multi_machines():
    pdu = _select_plan_by_name(TEST_PLAN_NAME_MULTI_MACHINES)

    try:
        result = CollisionModel(display_output=DISPLAY_OUTPUT).main()
        ok = result["passed"] 
        _logger.info("Test Result: %s", ok)
        assert ok is False, f"Expected False (failure) for multi plan, got {ok!r}"
    
    finally:
        delete_rois(pdu)

def test_test_ck():
    pdu = _select_plan_by_name(TEST_PLAN_NAME_CK)
    
    try:
        result = CollisionModel(display_output=DISPLAY_OUTPUT).main()
        ok = result["passed"] 
        assert ok is False, f"Expected False (failure) for CK plan, got {ok!r}"
    
    finally:        
        delete_rois(pdu)

def test_test_no_beams():
    pdu = _select_plan_by_name(TEST_PLAN_NAME_NO_BEAMS)

    try:
        result = CollisionModel(display_output=DISPLAY_OUTPUT).main()
        ok = result["passed"] 
        assert ok is False, f"Expected False (failure) for CK plan, got {ok!r}"

    finally:        
        delete_rois(pdu)
    
def test_test_pass():
    pdu = _select_plan_by_name(TEST_PLAN_NAME_PASS)
    try:
        result = CollisionModel(display_output=DISPLAY_OUTPUT).main()
        ok = result["passed"] 
        assert ok is True, f"Expected True (failure) for Pass plan, got {ok!r}"

    finally:        
        delete_rois(pdu)


if __name__ == "__main__":
    _logger.info("\n\n===== Starting test on collision_model.py =====")
    tests = [
        test_test_21ex,
        test_test_tb,
        test_test_rad,
        test_test_multi_machines,
        test_test_ck,
        test_test_multi_beamsets,
        test_test_no_beams,
        test_test_pass,
    ]
    try:
        for t in tests:
            _logger.info(f"Running {t.__name__}...")
            t() 
            _logger.info(f"Passed {t.__name__}!")
        _logger.info("==========All tests passed.================")
    except Exception as e:
        _logger.exception("[FAILED] in %s: %s", t.__name__, str(e))
        
        
        
        
