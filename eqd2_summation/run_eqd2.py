"""
eqd2_summation\run_eqd2.py

Front-end to run main_eqd2.py 

Created on 10/02/2025

@author: clanco01
"""

from __future__ import annotations

# === WORKING DIRECTORY ===
import sys
sys.path.append(r"\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
sys.path.append(r"F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")

# === Local imports ===
from eqd2_summation.main_eqd2 import EQD2DoseSummation
from RSutil.LogUtil.rs_logging import LOGGERS
from RSutil.patient_data_util import PatientDataUtil
from RSutil.get_windows_user_id import get_windows_user_id

# === Setup Logger ===
_logger = LOGGERS["eqd2_summation"]


# === Run main ===
def main() -> None:
    _logger.info("\n\n===== Running EQD2 Summation =====")
    try:
        pdu = PatientDataUtil()
        _logger.info("Patient_ID: %s || CaseName: %s", pdu.patient_id, pdu.case.CaseName)
        _logger.info("Current Windows User: %s", get_windows_user_id())
    except Exception as e:
        _logger.error("Failed to initialize PatientDataUtil or get Windows username: %s", e)
        pass
    try:
        eqd2_sum = EQD2DoseSummation()
        eqd2_sum.main()
    except Exception as e:
        _logger.error("[FAILED] EQD2 summation: %s", str(e))
    _logger.info("\n\n===== Finished EQD2 Summation =====\n\n") 
    
if __name__ == "__main__":
    main()