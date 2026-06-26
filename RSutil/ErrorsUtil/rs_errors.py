
"""
RSutil/ErrorsUtil/rs_errors.py

Custom exceptions and centralized error reporting.

This module provides:
    - Custom exception classes for Raystation script errors.
    - A centralized error logger for recording system issues.
"""
from __future__ import annotations

# === DEBUG SETTINGS ===
DEBUG_THIS_MODULE = True

# === Raystation Imports ===
try:
    from connect import get_current
except:
    pass

# === WORKING DIRECTORY ===
import sys
sys.path.append(r"\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
sys.path.append(r"F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")

# === STANDARD IMPORTS ===
import traceback
from typing import Dict, Any

# === LOCAL APPLICATION IMPORTS ===
from RSutil.ErrorsUtil.error_codes import ErrorDefinition, ALERT_PHYSICIST
from RSutil.ErrorsUtil.settings_errors import MAX_TRACEBACK_CHARS, RecommendedAction
from RSutil.ErrorsUtil.error_dispatcher import (
    DispatcherConfig, dispatch_action, ActionOutcome, Handler
)
from RSutil.LogUtil.settings_logging import LOG_PATHS
from RSutil.LogUtil.rs_logging import setup_logger, LOGGERS


# === SETUP LOGGER ===
_debug_logger = LOGGERS["debug"]
_error_logger = None
def _get_error_logger():
    """Initializes and returns the error logger."""
    global _error_logger
    if _error_logger is None:
        _error_logger = setup_logger(
            name="report_error",
            log_path=LOG_PATHS["error"]
        )
    return _error_logger


def report_error(
    error_def: ErrorDefinition,
    original_exception: Exception,
    context: dict,
    *,
    metadata: dict | None = None,
    message: str | None = None,
    dispatcher_config: DispatcherConfig | None = None,
    handler: Dict[RecommendedAction, Handler] | None = None,
    extra: Dict[str, Any] | None = None,
) -> ActionOutcome | None:
    """
    Log an error and dispatch the corresponding action.

    This function records the error with structured metadata and then routes it
    through the appropriate dispatcher handler (e.g., alert, retry, skip, abort).
    It serves as the unified entry point for error handling within RayStation scripts.

    Args:
        error_def (ErrorDefinition): Structured error definition that provides the
            error code, description, severity, and recommended action.
        original_exception (Exception): The caught exception that triggered this report.
        context (dict): Key identifiers describing where the error occurred
            (e.g., module name, function, patient ID).

        metadata (dict, optional): Additional diagnostic details such as input values,
            execution times, or counts. Defaults to None.
        message (str, optional): Optional user-facing message. If not provided,
            defaults to `error_def.description`.
        dispatcher_config (DispatcherConfig, optional): Configuration object defining
            global dispatch behavior (e.g., email recipients, title, auto-exit policy).
            If omitted, a default config is created.
        handler (dict[RecommendedAction, Handler], optional): Optional override mapping
            of specific actions to custom handler functions. Overrides those in
            `dispatcher_config`.
        extra (dict, optional): Arbitrary data forwarded to the dispatcher for
            contextual use by handlers (e.g., patient or system state).

    Returns:
        ActionOutcome | None: The result of the dispatched handler, including
        status flags such as `should_abort`, `did_skip`, or `exit_code`.
        May trigger an automatic script or use the flag as an indicator to 
        perform an action outside of rs_errors such as exiting script.
        
    Additional Notes on DispatcherConfig:
        
        Structure of DispatcherConfig dataclass
        
        @dataclass
        class DispatcherConfig:
            handler: Dict[RecommendedAction, Handler] | None = None
            title: str = "Attention"
            reload_kwargs: Dict[str, Any] | None = None
            alert_recipients: list[str] | None = None  # List of email addresses
            email_subject: Optional[str] = "RayStation Script Alert"
            email_message: Optional[str] = None
    """
    logger = _get_error_logger()

    # === Format traceback ===
    tb_str = "".join(
        traceback.format_exception(
            type(original_exception),
            original_exception,
            original_exception.__traceback__
        )
    )
    tb_str_trimmed = tb_str[:MAX_TRACEBACK_CHARS]

    # === Build context string for logging ===
    ctx_str = " | Context: " + ", ".join(f"{k}={v}" for k, v in context.items())
    
    # === Build metadata string for logging ===
    meta_generic = ""
    if error_def.recommended_action != RecommendedAction.ALERT_PHYSICIST:
        try:
            patient = get_current("Patient")
            pn, mrn, cn = patient.Name, patient.PatientID, get_current("Case").CaseName
            meta_generic = f"Patient: {pn} - MRN: {mrn} - Case Name: {cn}"
        except:
            pass
    meta_input = (
        " | Metadata: " + ", ".join(f"{k}={v}" for k, v in metadata.items())
        if metadata else ""
    )
    meta_str = meta_generic + meta_input

    # === Log error summary ===
    logger.error(
        f"[{error_def.code}] {error_def.description}{ctx_str}{meta_str} | "
        f"Severity: {error_def.severity.value} | Action: {error_def.recommended_action.value}"
    )

    # === Log traceback ===
    logger.error(f"Traceback (trimmed to {MAX_TRACEBACK_CHARS} chars):\n{tb_str_trimmed}")
    
    # build a per-call DispatcherConfig with optional overrides
    cfg = dispatcher_config or DispatcherConfig()
    if handler:
        cfg = DispatcherConfig(
            handler=handler,
            title=cfg.title,
            reload_kwargs=cfg.reload_kwargs,
            alert_recipients=cfg.alert_recipients,
        )

    combined_extra = {"context": context, **(metadata or {})}

    outcome = dispatch_action(
        error_def.recommended_action,
        msg=message or error_def.description,
        error_code=error_def.code,
        exc=original_exception,
        extra=combined_extra,
        cfg=cfg,
    )

    return outcome


# === RUN LOCALLY FOR DEBUGGING ===
if __name__ == "__main__" and DEBUG_THIS_MODULE:
    debug_logger = LOGGERS["debug"]
    debug_logger.info("Debug mode ON...")
    from RSutil.ErrorsUtil.error_codes import ABORT_SCRIPT, PROMPT_USER, ALERT_PHYSICIST, SKIP_STEP
    from RSutil.ErrorsUtil.error_dispatcher import ActionOutcome, DispatchContext

    def _dummy_handler(ctx: DispatchContext) -> ActionOutcome:
        debug_logger.debug(f"[DUMMY HANDLER TRIGGERED] Action: {ctx.action.name}")
        return ActionOutcome(action=ctx.action)

    try:
        raise ValueError("Simulated failure.")
    except Exception as e:
        sample_context = {
            "source_module": "errors",
            "function": "local debug",
        }
        sample_metadata = {
            "debugging": "testing only...",
        }
        
        cfg = DispatcherConfig()
        cfg.alert_recipients = ["owen.clancey@nyulangone.org"]
        
        handler = {RecommendedAction.PROMPT_USER: _dummy_handler}
        
        outcome_alert_physicist = report_error(
            error_def=ALERT_PHYSICIST.SYSF_UNHANDLED_EXCEPTION,
            original_exception=e,
            context=sample_context,
            metadata=sample_metadata,
            dispatcher_config=cfg
        )
        print(outcome_alert_physicist)
        
        outcome_prompt_user = report_error(
            error_def=PROMPT_USER.UIUX_SELECT_INVALID,
            original_exception=e,
            context=sample_context,
            metadata=sample_metadata
        )
        print(outcome_prompt_user)
        
        debug_logger.debug("Single handler...")
        outcome_prompt_user_handler = report_error(
            error_def=PROMPT_USER.UIUX_SELECT_INVALID,
            original_exception=e,
            context=sample_context,
            metadata=sample_metadata,
            message="Single handler",
            handler=handler,
        )
        print(outcome_prompt_user_handler)
        
        outcome_abort_script = report_error(
            error_def=ABORT_SCRIPT.DATA_REQUIRED_MISSING,
            original_exception=e,
            context=sample_context,
            metadata=sample_metadata
        )
        print("THIS TEXT SHOULD NOT APPEAR - CHECK DEBUG CODE IN rs_errors.py.  SCRIPT ABORTED!")
