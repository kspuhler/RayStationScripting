r"""
RSutil\ErrorsUtil\settings_errors.py

This module defines Errors settings.

Usage:
    Import settings directly to access any configuration constants globally.

Created on Mon Oct  6 09:02:34 2025

@author: clanco01
"""
from __future__ import annotations

#===IMPORTS===
import os
from enum import Enum

_CANDIDATE_ROOTS = [
    r"\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD",
    r"F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD",
]

for _root in _CANDIDATE_ROOTS:
    if os.path.isdir(_root):
        PROJECT_ROOT = _root
        break

MAX_TRACEBACK_CHARS = 2000

SMTP_SETTINGS = {
    "server": "smtp.gmail.com",
    "port": 465,
    "user": "nyu.raystation.alerts@gmail.com",
    "email_pass": "nyuraystation25",
    "app_pass": "wlwj khiz fwgt raaw"
}

class Severity(str, Enum):
    """Indicates the seriousness of an error for logging and monitoring purposes."""

    INFO = "info"            # Informational only; no action required
    WARNING = "warning"      # Unexpected event; recoverable, monitor situation
    ERROR = "error"          # Significant issue; may affect functionality or stability
    CRITICAL = "critical"    # Severe failure; system integrity at risk


class RecommendedAction(str, Enum):
    """Defines the recommended follow-up or system response to an error in RayStation scripts."""

    LOG_ONLY = "log_only"                               # Record the issue but continue execution
    RETRY_OPERATION = "retry_operation"                 # Attempt the operation again automatically
    SKIP_STEP = "skip_step"                             # Skip the current script step safely
    ALERT_PHYSICIST = "alert_physicist"                 # Escalate issue for manual physics review
    RELOAD_PLAN = "reload_plan"                         # Reload the plan or patient data
    PROMPT_USER_RETRY = "prompt_user_retry"             # Display a GUI message box for user decision to retry/cancel
    PROMPT_USER_ACKNOWLEDGE = "prompt_user_acknowledge" # Display a GUI message box for user decision to ok/cancel
    ABORT_SCRIPT = "abort_script"                       # Stop current script gracefully
    SAVE_AND_EXIT = "save_and_exit"                     # Save patient and Stop current script gracefully
    
    
