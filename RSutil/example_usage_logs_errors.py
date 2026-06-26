# === WORKING DIRECTORY ===
import sys
sys.path.append(r"\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
sys.path.append(r"F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")

# === Local imports ===
from RSutil.LogUtil.rs_logging import LOGGERS, set_logger_mode
from RSutil.ErrorsUtil.error_dispatcher import DispatcherConfig
from RSutil.ErrorsUtil.rs_errors import report_error
from RSutil.ErrorsUtil.error_codes import PROMPT_USER, ALERT_PHYSICIST, ABORT_SCRIPT
from RSutil.patient_data_util import PatientDataUtil

# === Setup Logger ===
# Note: GO into RSutil\LogUtil\settings_logging.py and insert your script speific log
# into the constant LOG_SPECS
_logger = LOGGERS["EXAMPLE_ONLY"]

# === Error Handling ===
def alert_physicist_error(
        exc: Exception, 
        metadata: Optional[dict] = None, 
        message: Optional[str] = None
):   
                                              
    cfg = DispatcherConfig()
    cfg.alert_recipients = ["JOE_SMOE@nyulangone.org"]
    report_error(
            error_def=ALERT_PHYSICIST.SYSF_UNHANDLED_EXCEPTION, 
            original_exception=exc, 
            context={"module": "main_farts.py"},
            metadata=metadata,
            message=message,
            dispatcher_config=cfg,
        )
    
def prompt_user_acknowledge(
        exc: Exception, 
        metadata: Optional[dict] = None, 
        message: Optional[str] = None
):                                                  
    report_error(
            error_def=PROMPT_USER.UIUX_USER_ACKNOWLEDGE, 
            original_exception=exc, 
            context={"module": "MODULE_NAME.py"},
            metadata={},
            message=message,
        )

def abort_script_error(
        exc: Exception, 
        metadata: Optional[dict] = None, 
        message: Optional[str] = None
):
    report_error(
            error_def=ABORT_SCRIPT.DATA_REQUIRED_MISSING, 
            original_exception=exc, 
            context={"module": "MODULE_NAME.py"},
            metadata={},
            message=message,
        )
    raise RuntimeError(str(exc))
    
    

# === Sample Main Code Only ===

def main():
    try:
        pass
    except Exception as e:
        
        # Alert physicist
        _alert_physicist_error(e, message=__name__)
        
        # Log error
        _logger.error("[FAILED] in %s.  Email notification sent.  Exception: %s", __name__, str(e))
        
        # Log error with a traceback to the line in the code
        _logger.exception("[FAILED] in %s.  Email notification sent.  Exception: %s", __name__, str(e))
        
        # Set RayStation progress bar and native prompt
        set_progress("Waiting for user to hit play button...", percentage = -1)
        await_user_input(message="[FAILED] script.  Physicist alerted to address the issue.")
        set_progress("Sending physicist notification...", percentage = -1)
        
        # Set a sleep to make sure any alert physicist email has time to be sent externally
        time.sleep(3)
        
        # Shut down script gracefully
        abort_script_error(exc=e, message=str(e))