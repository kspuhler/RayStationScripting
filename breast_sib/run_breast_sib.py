"""Front-end script to rung the beast_sib class.

Created on 11/10/2025

@author: clanco01
"""
from __future__ import annotations

# === WORKING DIRECTORY ===
import sys
sys.path.append(r"\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
sys.path.append(r"F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")

# === Local imports ===
from breast_sib.main_breast_sib import BreastSIB
from RSutil.LogUtil.rs_logging import LOGGERS
from RSutil.patient_data_util import PatientDataUtil
from RSutil.get_windows_user_id import get_windows_user_id

# === Setup Logger ===
_logger = LOGGERS["breast_sib"]


# === Run main ===
def main() -> None:
    _logger.info("\n\n===== Running Breast_SIB =====")
    try:
        pdu = PatientDataUtil()
        _logger.info("Patient_ID: %s || CaseName: %s", pdu.patient_id, pdu.case.CaseName)
        _logger.info("Current Windows User: %s", get_windows_user_id())
    except Exception as e:
        _logger.error("Failed to initialize PatientDataUtil or get Windows username: %s", e)
        pass
    try:
        breast_sib = BreastSIB()
        breast_sib.main()
    except Exception as e:
        _logger.error("[FAILED] Breast_SIB: %s", str(e))
    _logger.info("\n\n===== Finished Breast_SIB =====\n\n") 
    
if __name__ == "__main__":
    main()



