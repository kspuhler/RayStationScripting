""" 
set_max_mlc_jaws\run_set_max_mlc_jaws.py

Front-end code for the setting the maximum MLC and Jaw position GUI.
The GUI allows the user to change a beam to a maximum MLC and Jaw size as determined by
another beam's MLC and Jaw settings.  The tool is helpful for reducing the size of beams,
when their optimized MLC and Jaws are larger than a givn limit often established by an 
initial physician's field shape.  Ex: Breast Tangents

Created on 11/10/2025

@author: clanco01
"""

from __future__ import annotations

# === WORKING DIRECTORY ===
import sys
sys.path.append(r"\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
sys.path.append(r"F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")

# === Local imports ===
from set_max_mlc_jaws.main_set_max_mlc_jaws import SetMaxBeamShape
from RSutil.LogUtil.rs_logging import LOGGERS
from RSutil.patient_data_util import PatientDataUtil
from RSutil.get_windows_user_id import get_windows_user_id

# === Setup Logger ===
_logger = LOGGERS["set_max_mlc_jaws"]


# === Run main ===
def main() -> None:
    _logger.info("\n\n===== Running Set Max MLC and Jaws =====")
    try:
        pdu = PatientDataUtil()
        _logger.info("Patient_ID: %s || CaseName: %s", pdu.patient_id, pdu.case.CaseName)
        _logger.info("Current Windows User: %s", get_windows_user_id())
    except Exception as e:
        _logger.error("Failed to initialize PatientDataUtil or get Windows username: %s", e)
        pass
    try:
        set_beam_shape = SetMaxBeamShape()
        set_beam_shape.main()
    except Exception as e:
        _logger.error("[FAILED] Set Max MLC and Jaws: %s", str(e))
    _logger.info("\n\n===== Finished Set Max MLC and Jaws =====\n\n") 
    
if __name__ == "__main__":
    main()