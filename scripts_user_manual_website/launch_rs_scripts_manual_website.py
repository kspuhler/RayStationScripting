"""
scripts_user_manual_website\launch_rs_scripts_manual_website.py

This module provides a simple utility function to launch the RayStation User Manual
hosted on SharePoint. It uses the standard Python `webbrowser` module to open the
URL in the user's default browser.

"""
from __future__ import annotations

# === DEBUG SETTINGS ===
_DEBUG_THIS_MODULE = False
_ALERT_PHYSICIST_ON_ALL_USES = True

# === Raystation import ===
try:
    from connect import await_user_input, set_progress
except Exception:
    pass

# === WORKING DIRECTORY ===
import sys
sys.path.append(r"\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
sys.path.append(r"F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")

# === Main library imports ===
import time

# === Local imports ===
from RSutil.LogUtil.rs_logging import LOGGERS, set_logger_mode
from RSutil.ErrorsUtil.error_dispatcher import DispatcherConfig
from RSutil.ErrorsUtil.rs_errors import report_error
from RSutil.ErrorsUtil.error_codes import PROMPT_USER, ALERT_PHYSICIST, ABORT_SCRIPT

# === Setup Logger ===
_logger = LOGGERS["launch_rs_scripts_manual_website"]
if _DEBUG_THIS_MODULE:
    set_logger_mode(_logger, "debug")

# === Error handling ===
def _alert_physicist_error(
        exc: Exception, 
        metadata: dict | None = None, 
        message: str | None = None
):                                              
    cfg = DispatcherConfig()
    cfg.alert_recipients = ["owen.clancey@nyulangone.org"]
    report_error(
            error_def=ALERT_PHYSICIST.SYSF_UNHANDLED_EXCEPTION, 
            original_exception=exc, 
            context={"module": "launch_rs_scripts_manual_website.py"},
            metadata=metadata,
            message=message,
            dispatcher_config=cfg,
        )

def _prompt_user_acknowledge(
        exc: Exception, 
        metadata: dict | None = None, 
        message: str | None = None
):
    _logger.debug("Inside _prompt_user_acknowledge()...")                                         
    report_error(
            error_def=PROMPT_USER.UIUX_USER_ACKNOWLEDGE, 
            original_exception=exc, 
            context={"module": "launch_rs_scripts_manual_website.py"},
            metadata={},
            message=message,
        )
    _logger.debug("Finished _prompt_user_acknowledge()...") 

def _abort_script_error(
        exc: Exception, 
        metadata: dict | None = None, 
        message: str | None = None
):
    _logger.debug("Inside _abort_script_error()...") 
    report_error(
            error_def=ABORT_SCRIPT.DATA_REQUIRED_MISSING, 
            original_exception=exc, 
            context={"module": "launch_rs_scripts_manual_website.py"},
            metadata={},
            message=message,
        )
    _logger.debug("Raising runtime error to stop script in _abort_script_error()...") 
    raise RuntimeError(str(exc))


def open_raystation_user_manual(url: str | None = None) -> None:
    """
    Opens the RayStation User Manual SharePoint site in the default web browser.
    
    Args:
        url (str | None): Optional custom URL to open.
    
    Returns:
        None
    """
    import webbrowser

    if url is None:
        url = "https://nyulangone.sharepoint.com/sites/NYULI_RS_ScriptingUserManual/"
    try:
        webbrowser.open(url, new=2)  # new=2 opens in a new tab, if possible
    except Exception as e:
        _alert_physicist_error(e, message=__name__)
        _logger.error("[FAILED] in %s.  Email notification sent.  Exception: %s", __name__, str(e))
        set_progress("Waiting for user to hit play button...", percentage = -1)
        await_user_input(message="[FAILED] script.  Physicist alerted to address the issue.")
        set_progress("Sending physicist notification...", percentage = -1)
        time.sleep(3)
        _abort_script_error(exc=e, message=str(e))


if __name__ == "__main__":
    open_raystation_user_manual()
