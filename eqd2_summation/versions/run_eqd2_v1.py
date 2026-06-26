""" 
Front-end to run main_eqd2.py 

Created on 10/02/2025

@author: clanco01
"""

# === Raystation import ===
try:
    from connect import get_current
except:
    pass

# === WORKING DIRECTORY ===
import sys
sys.path.append(r"\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
sys.path.append(r"F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")

# === Standard Imports ===
from typing import Optional

# === Local imports ===
from EQD2_Summation.main_eqd2 import EQD2DoseSummation
from RSutil.LogUtil.rs_logging import LOGGERS
from RSutil.ErrorsUtil.rs_errors import report_error
from RSutil.ErrorsUtil.error_codes import ALERT_PHYSICIST
from RSutil.ErrorsUtil.error_dispatcher import DispatcherConfig

# === Setup Logger ===
_logger = LOGGERS["eqd2_summation"]

patient_info = ""
try:
    patient = get_current("Patient")
    pn, mrn, cn = patient.Name, patient.PatientID, get_current("Case").CaseName
    patient_info = f"Patient: {pn} - MRN: {mrn} - Case Name: {cn}"
except:
    pass
_logger.info("Running EQD2 Summation on patient: %s", patient_info) 

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
            metadata={},
            message=message,
            dispatcher_config=cfg,
        )


# === Run main ===
try:
    eqd2_sum = EQD2DoseSummation()
    eqd2_sum.main()
    _logger.info("Finished EQD2 Summation on patient: %s", patient_info) 

except Exception as e:
    _logger.error("Failed EQD2 summation on patient: %s  Closing script: %s", patient_info, e)
    message = "Failed EQD2 summation in run_eqd2.py."
    _alert_physicist_error(e, message=message)

exit()
