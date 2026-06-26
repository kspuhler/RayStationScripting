"""Front-end for running main_create_export_qa_plan.py

Created on 11/10/2025

@author: clanco01
"""

from __future__ import annotations

# === WORKING DIRECTORY ===
import sys
sys.path.append(r"\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
sys.path.append(r"F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")

# === Local imports ===
from create_export_qa_plan.main_create_export_qa_plan import CreateExportQAPlan
from RSutil.LogUtil.rs_logging import LOGGERS
from RSutil.patient_data_util import PatientDataUtil
from RSutil.get_windows_user_id import get_windows_user_id

# === Setup Logger ===
_logger = LOGGERS["create_export_qa_plan"]


# === Run main ===
def main() -> None:
    _logger.info("\n\n===== Running Create And Export QA Plan =====")
    try:
        pdu = PatientDataUtil()
        _logger.info("Patient_ID: %s || CaseName: %s", pdu.patient_id, pdu.case.CaseName)
        _logger.info("Current Windows User: %s", get_windows_user_id())
    except Exception as e:
        _logger.error("Failed to initialize PatientDataUtil or get Windows username: %s", e)
        pass
    try:
        create_export_qa_plan = CreateExportQAPlan()
        create_export_qa_plan.main()
    except Exception:
        # Exception and erroring handling captured inside main method
        pass
    _logger.info("\n\n===== Finished Create And Export QA Plan =====\n\n") 
    
if __name__ == "__main__":
    main()


