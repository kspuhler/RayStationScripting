"""
tps_qa\run_tps_monthly_qa.py

Runs a front-end for generating the TPS Monthly QA PDF document.

Created on Mon Apr  7 10:23:22 2025

@author: clanco01
"""

from __future__ import annotations

# === WORKING DIRECTORY ===
import sys
sys.path.append(r"\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
sys.path.append(r"F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")

# === Local imports ===
from tps_qa.main_tps_monthly_qa import TPSMonthlyQA
from RSutil.LogUtil.rs_logging import LOGGERS
from RSutil.get_windows_user_id import get_windows_user_id

# === Setup Logger ===
_logger = LOGGERS["tps_qa"]


# === Run main ===
def main() -> None:
    _logger.info("\n\n===== Running TPS Monthly QA =====")
    try:
        _logger.info("Current Windows User: %s", get_windows_user_id())
    except Exception as e:
        _logger.error("Failed to get Windows username: %s", e)
        pass
    try:
        tps_monthly = TPSMonthlyQA()
        tps_monthly.main()
    except Exception as e:
        _logger.error("[FAILED] TPS Monthly QA: %s", str(e))
    _logger.info("\n\n===== Finished TPS Monthly QA =====\n\n") 
    
if __name__ == "__main__":
    main()


