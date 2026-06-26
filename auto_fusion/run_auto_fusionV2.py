""" Front-end to run AutoFusion class

Created on 11/10/2025

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
from auto_fusion.main_auto_fusionV2 import AutoFusion

# === Setup Logger ===
_logger = LOGGERS["auto_fusion"]


# === Run main ===
def main() -> None:
    _logger.info("\n\n===== Running AutoFusion =====")
    try:
        pdu = PatientDataUtil()
        _logger.info("Patient_ID: %s || CaseName: %s", pdu.patient_id, pdu.case.CaseName)
        _logger.info("Current Windows User: %s", get_windows_user_id())
    except Exception as e:
        _logger.error("Failed to initialize PatientDataUtil or get Windows username: %s", e)
        pass
    try:
        fusion = AutoFusion()
        fusion.run_fusion()
    except Exception as e:
        _logger.exception("[FAILED] AutoFusion: ", str(e))
    _logger.info("\n\n===== Finished AutoFusion =====\n\n") 
    
if __name__ == "__main__":
    main()

