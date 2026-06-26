""" 
collision_model/run_collision_model.py

Front-end to run collision model

Created on 12/15/2025

@author: clanco01
"""

from __future__ import annotations

# === WORKING DIRECTORY ===
import sys
sys.path.append(r"\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
sys.path.append(r"F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")

# === Local imports ===
from RSutil.LogUtil.rs_logging import LOGGERS
from RSutil.patient_data_util import PatientDataUtil
from RSutil.get_windows_user_id import get_windows_user_id
from collision_model.main_collision_model import CollisionModel

# === Setup Logger ===
_logger = LOGGERS["collision_model"]


# === Run main ===
def main() -> None:
    _logger.info("\n\n===== Running CollisionModel =====")
    try:
        pdu = PatientDataUtil()
        _logger.info("Patient_ID: %s || CaseName: %s", pdu.patient_id, pdu.case.CaseName)
        _logger.info("Current Windows User: %s", get_windows_user_id())
    except Exception as e:
        _logger.error("Failed to initialize PatientDataUtil or get Windows username: %s", e)
        pass
    try:
        cm = CollisionModel()
        cm.main()
    except Exception as e:
        _logger.error("[FAILED] CollisionModel: %s", str(e))
    _logger.info("\n\n===== Finished CollisionModel =====\n\n") 
    
if __name__ == "__main__":
    main()

