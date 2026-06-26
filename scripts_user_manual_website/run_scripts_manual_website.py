"""
scripts_user_manual_website\run_scripts_manual_website.py

Front-end to run launch_rs_scripts_manual_website.py 

Created on 11/10/2025

@author: clanco01
"""

from __future__ import annotations

# === WORKING DIRECTORY ===
import sys
sys.path.append(r"\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
sys.path.append(r"F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")

# === Local imports ===
from scripts_user_manual_website.launch_rs_scripts_manual_website import open_raystation_user_manual
from RSutil.LogUtil.rs_logging import LOGGERS
from RSutil.get_windows_user_id import get_windows_user_id

# === Setup Logger ===
_logger = LOGGERS["launch_rs_scripts_manual_website"]


# === Run main ===
def main() -> None:
    _logger.info("\n\n===== Running NYU RS Scripts User Manual =====")
    try:
        _logger.info("Current Windows User: %s", get_windows_user_id())
    except Exception as e:
        _logger.error("Failed to get Windows username: %s", e)
        pass
    try:
        open_raystation_user_manual()
    except Exception as e:
        _logger.error("[FAILED] NYU RS Scripts User Manual: %s", str(e))
    _logger.info("\n\n===== Finished NYU RS Scripts User Manual =====\n\n") 
    
if __name__ == "__main__":
    main()