
"""
RSutil/ErrorsUtil/error_dispatcher.py

Dispatches actions based on `RecommendedAction` values defined in RSutils.Errors.settings.
Keep this module thin. Business logic lives in callers.

Example:
    from Errors.settings import RecommendedAction
    from Errors.error_dispatcher import dispatch_action, DispatcherConfig

    def do_work():
        ...

    cfg = DispatcherConfig(retry_fn=do_work)
    outcome = dispatch_action(RecommendedAction.PROMPT_USER_RETRY, config=cfg, message="Series not selected.")
    if outcome.should_abort:
        return
    if outcome.retry_attempted:
        result = outcome.retry_result

Notes:
- RayStation-specific actions are injected via DispatcherConfig callbacks to avoid hard deps.
"""
from __future__ import annotations

# === DEBUG SETTINGS ===
DEBUG_THIS_MODULE = True

# === STANDARD IMPORTS ===
from dataclasses import dataclass
from typing import Callable, Optional, Any, Dict
import smtplib
from email.message import EmailMessage
import threading
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt
import tkinter as tk
from tkinter import messagebox

# === Raystation Imports
try:
    from connect import get_current, set_progress
except Exception:
    pass

# === WORKING DIRECTORY ===
import sys
sys.path.append(r"\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
sys.path.append(r"F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")

# === LOCAL IMPORTS ===
from RSutil.ErrorsUtil.settings_errors import RecommendedAction, SMTP_SETTINGS
from RSutil.LogUtil.rs_logging import LOGGERS
from RSutil.open_patient_case_and_plan import open_patient_case_and_plan 

# === Setup logger ===
_logger = LOGGERS["system"]


# === Supporting data structures ===
@dataclass
class ActionOutcome:
    """Represents the result of executing a dispatcher action.

    Each handler returns an ActionOutcome to describe what occurred and
    what the caller should do next. 

    Attributes:
        action: The RecommendedAction value that produced this outcome.
        user_choice: Optional string indicating the user's decision or
            result of an interactive prompt (e.g., "retry", "skip").
        did_skip: Whether the operation was skipped as part of handling.
        retry_attempted: True if a retry was triggered by the handler.
        retry_result: Any data returned from the retry attempt.
        should_abort: Indicates the caller should stop execution or exit.
        exit_code: Optional exit status code (0 for normal, nonzero for error).
        did_save: True if logs were successfully flushed or patient saved.
    """
    action: RecommendedAction
    user_choice: Optional[str] = None
    did_skip: bool = False
    retry_attempted: bool = False
    retry_result: Any = None
    should_abort: bool = False
    exit_code: int | None = None
    did_save: bool = False 

@dataclass
class DispatchContext:
    """
    This class bundles the details of an error or event being handled so that
    every handler receives a consistent set of inputs. 

    Attributes:
        action (RecommendedAction): The RecommendedAction enum value that identifies what the
            dispatcher should perform (e.g., PROMPT_USER_RETRY, RELOAD_PLAN).
        msg (str): A user-facing message or description of the event.
        title (str): Optional title or header text for GUI prompts or logs.
        error_code: The structured error code string (e.g., "E-EPSE-001").
        exc: The original exception instance that triggered this action, if any.
        extra: Arbitrary metadata or additional context (e.g., patient info).
        cfg: The DispatcherConfig object containing handler mappings
            and global configuration options.
    """
    action: RecommendedAction
    msg: str = ""
    title: str = "Attention"
    error_code: Optional[str] = None
    exc: Optional[BaseException] = None
    extra: Dict[str, Any] = None
    cfg: "DispatcherConfig" = None  # backref if a handler needs config

Handler = Callable[[DispatchContext], ActionOutcome]

# === Config object with override registry ===
@dataclass
class DispatcherConfig:
    handler: Dict[RecommendedAction, Handler] | None = None
    title: str = "Attention"
    reload_kwargs: Dict[str, Any] | None = None
    alert_recipients: list[str] | None = None  # List of email addresses
    auto_exit_on_abort: bool = True
    email_subject: Optional[str] = "RayStation Script Alert"
    email_message: Optional[str] = None

    def resolve_handler(self) -> Dict[RecommendedAction, Handler]:
        merged = dict(DEFAULT_HANDLERS)
        if self.handler:
            merged.update(self.handler)  # user overrides take precedence
        return merged

# === Default Handlers ===
def _noop(ctx: DispatchContext) -> ActionOutcome:
    return ActionOutcome(action=ctx.action)

def _skip_step(ctx: DispatchContext) -> ActionOutcome:
    return ActionOutcome(action=ctx.action, did_skip=True)

def _retry_op(ctx: DispatchContext) -> ActionOutcome:
    return ActionOutcome(action=ctx.action, retry_attempted=True)

def _prompt_user_retry(ctx: DispatchContext) -> ActionOutcome:
    """
    Show a Retry/Cancel dialog.
      1) Try PyQt5 (QMessageBox) first
      2) Fallback to Tkinter (askretrycancel)
    """
    try:
        # === First attempt: PyQt5 ===
        try:
            app = QApplication.instance()
            created_app = False
            if app is None:
                # Create a temporary app (no long-running event loop needed for exec_())
                app = QApplication([])
                created_app = True

            box = QMessageBox()
            box.setIcon(QMessageBox.Warning)
            box.setWindowTitle(ctx.title or "Attention")
            box.setText(ctx.msg or "An action is required to continue.")
            box.setStandardButtons(QMessageBox.Retry | QMessageBox.Cancel)
            box.setDefaultButton(QMessageBox.Retry)
            box.setWindowFlag(Qt.WindowStaysOnTopHint, True)

            result = box.exec_()
            if created_app:
                # Don't start app.exec_(); the modal exec_() already ran the loop
                app.quit()

            choice = "retry" if result == QMessageBox.Retry else "abort"

        except Exception:
            # === Second attempt: Tkinter ===
            try:
                root = tk.Tk()
                root.withdraw()
                try:
                    root.attributes("-topmost", True)
                except Exception:
                    pass
                retry = messagebox.askretrycancel(title=ctx.title, message=ctx.msg)
                choice = "retry" if retry else "abort"
                try:
                    root.destroy()
                except Exception:
                    pass
            except Exception:
                _logger.error("Failed to launch user retry/cancel prompt.")

        if choice == "retry":
            return ActionOutcome(
                action=RecommendedAction.PROMPT_USER_RETRY,
                user_choice="retry",
                retry_attempted=True
            )
        else:
            return ActionOutcome(
                action=RecommendedAction.PROMPT_USER_RETRY,
                user_choice="abort",
                should_abort=True
            )

    except Exception as e:
        _logger.error("Failed to prompt user (retry/cancel): %s, %s", ctx or None, e)
        return ActionOutcome(
            action=RecommendedAction.PROMPT_USER_RETRY,
            user_choice="abort",
            should_abort=True
        )

def _prompt_user_acknowledge(ctx: DispatchContext) -> ActionOutcome:
    """
    Show an OK/Cancel dialog.
      1) Try PyQt5 (QMessageBox) first
      2) Fallback to Tkinter (askokcancel)
      3) Close/ESC treated as Cancel
    """
    try:
        choice = "cancel"  # default (safe)

        # === First attempt: PyQt5 ===
        try:
            app = QApplication.instance()
            created_app = False
            if app is None:
                app = QApplication([])
                created_app = True

            box = QMessageBox()
            box.setIcon(QMessageBox.Information)
            box.setWindowTitle(ctx.title or "Please confirm")
            box.setText(ctx.msg or "Please acknowledge to continue.")
            box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
            box.setDefaultButton(QMessageBox.Ok)
            box.setWindowModality(Qt.ApplicationModal)
            box.setWindowFlag(Qt.WindowStaysOnTopHint, True)

            result = box.exec_()
            if created_app:
                app.quit()

            choice = "ok" if result == QMessageBox.Ok else "cancel"

        except Exception:
            # === Second attempt: Tkinter ===
            try:
                root = tk.Tk()
                root.withdraw()
                try:
                    root.attributes("-topmost", True)
                except Exception:
                    pass
                ok = messagebox.askokcancel(title=ctx.title, message=ctx.msg)
                choice = "ok" if ok else "cancel"
                try:
                    root.destroy()
                except Exception:
                    pass
            except Exception:
                _logger.error("Failed to launch user OK/Cancel prompt.")

        # === Outcome mapping ===
        if choice == "ok":
            return ActionOutcome(
                action=RecommendedAction.PROMPT_USER_ACKNOWLEDGE,
                user_choice="ok"
            )
        else:
            # Leave should_abort to caller policy; they can decide to exit or not.
            return ActionOutcome(
                action=RecommendedAction.PROMPT_USER_ACKNOWLEDGE,
                user_choice="cancel"
            )

    except Exception as e:
        _logger.error("Failed to prompt user (ok/cancel): %s, %s", ctx or None, e)
        return ActionOutcome(
            action=RecommendedAction.PROMPT_USER_ACKNOWLEDGE,
            user_choice="cancel"
        )


def _reload_plan(ctx: DispatchContext | None = None) -> ActionOutcome:
    """Fallback reload action: reopen current patient/case/plan using RS API."""
    try:
        open_patient_case_and_plan()
        return ActionOutcome(
            action=ctx.action if ctx else RecommendedAction.RELOAD_PLAN,
            user_choice="reloaded",
        )
    except Exception as e:
        _logger.error("Failed to send reload plan: %s, %s", ctx or None, e)

def _save_and_exit(ctx: DispatchContext) -> ActionOutcome:
    did_save = False
    try:
        for _, lg in LOGGERS.items():
            for h in list(lg.handlers):
                try:
                    h.flush()
                except Exception:
                    pass
                
        try:
            set_progress('Saving patient...', percentage = -1)
            get_current("Patient").Save()
            did_save = True
        except Exception:
            pass
        
        return ActionOutcome(
            action=ctx.action,
            user_choice="exit",
            should_abort=True,
            exit_code=0,
            did_save=did_save,          
        )
    except Exception as e:
        _logger.error("Failed to send save patient and exit script: %s, %s", ctx or None, e)

def _abort_script(ctx: DispatchContext | None = None) -> ActionOutcome:
    """Safely stop script execution without forcing an immediate exit.

    This handler signals the caller to terminate execution after performing any
    necessary cleanup. It does not call sys.exit() directly, allowing the
    controlling layer (e.g., errors.py or RayStation script harness) to decide
    how to stop safely.
    """
    return ActionOutcome(
        action=ctx.action if ctx else RecommendedAction.ABORT_SCRIPT,
        should_abort=True,
        exit_code=1,        # nonzero = abnormal termination
        user_choice="abort"
    )

def _alert_physicist(ctx: DispatchContext | None = None) -> ActionOutcome:
    """DO NOT INCLUDE ANY PHI IN MESSAGE/EMAIL/BODY - HIPPA COMPLIANCE.
    
    Context info is disabled for HIPPA compliance.
    
    Send an email alert to the physics team about a critical error.

    This handler attempts to email one or more recipients with details about
    the error or exception. It returns an ActionOutcome instead of raising,
    so the dispatcher remains stable even if email sending fails.
    """
    
    to_addrs = ctx.cfg.alert_recipients
    
    if isinstance(to_addrs, str):
        to_addrs = [to_addrs]
    to_addrs = to_addrs or []

    msg_body = ctx.cfg.email_message or f"""
    A critical issue occurred during RayStation script execution.

    Error Code: {ctx.error_code or 'N/A'}
    Action: {ctx.action if ctx else RecommendedAction.ALERT_PHYSICIST}
    Message: {ctx.msg or 'No message provided.'}
    Exception: {repr(ctx.exc) if ctx and ctx.exc else 'N/A'}
    """
    
    def _send_email():
        try:
            email_msg = EmailMessage()
            email_msg["Subject"] = ctx.cfg.email_subject
            email_msg["From"] = SMTP_SETTINGS["user"]
            email_msg["To"] = ", ".join(to_addrs)
            email_msg.set_content(msg_body)
    
            with smtplib.SMTP_SSL(SMTP_SETTINGS["server"], SMTP_SETTINGS["port"], timeout=10) as smtp:
                smtp.login(SMTP_SETTINGS["user"], SMTP_SETTINGS["app_pass"])
                smtp.send_message(email_msg)
        except Exception as e:
            _logger.error("Failed to send ALERT_PHYSICIST email: %s, %s", ctx or None, e)

    threading.Thread(target=_send_email, name="rs-alert-physicist-email", daemon=True).start()

    return ActionOutcome(
        action=ctx.action if ctx else RecommendedAction.ALERT_PHYSICIST,
        user_choice="alert_queued",
        did_skip=False,
        retry_result="Email send queued in background",
    )


DEFAULT_HANDLERS: Dict[RecommendedAction, Handler] = {
    RecommendedAction.LOG_ONLY: _noop,
    RecommendedAction.PROMPT_USER_RETRY: _prompt_user_retry,
    RecommendedAction.PROMPT_USER_ACKNOWLEDGE: _prompt_user_acknowledge,
    RecommendedAction.RETRY_OPERATION: _retry_op,
    RecommendedAction.SKIP_STEP: _skip_step,
    RecommendedAction.RELOAD_PLAN: _reload_plan,
    RecommendedAction.ALERT_PHYSICIST: _alert_physicist,
    RecommendedAction.SAVE_AND_EXIT: _save_and_exit,
    RecommendedAction.ABORT_SCRIPT: _abort_script
}

# === Default messages ===
def _default_message_for(action: RecommendedAction) -> str:
    M = {
        RecommendedAction.LOG_ONLY: "Logged the issue. Continuing.",
        RecommendedAction.PROMPT_USER_RETRY: "An action is required to continue.",
        RecommendedAction.RETRY_OPERATION: "Attempting a retry of the last operation.",
        RecommendedAction.SKIP_STEP: "Skipping this step due to a recoverable issue.",
        RecommendedAction.RELOAD_PLAN: "Reloading the current plan.",
        RecommendedAction.ALERT_PHYSICIST: "A critical issue occurred; alerting physics.",
        RecommendedAction.SAVE_AND_EXIT: "Saving and exiting the script.",
        RecommendedAction.ABORT_SCRIPT: "Stopping script safely.",
    }
    return M.get(action, "Processing action.")


# === Dispatcher ===
def dispatch_action(
    action: RecommendedAction,
    *,
    msg: str = "",
    error_code: Optional[str] = None,
    exc: Optional[BaseException] = None,
    extra: Optional[Dict[str, Any]] = None,
    cfg: Optional[DispatcherConfig] = None,
) -> ActionOutcome:
    cfg = cfg or DispatcherConfig()
    msg = msg or _default_message_for(action)
    handler_map = cfg.resolve_handler()
    handler = handler_map.get(action, _noop)

    ctx = DispatchContext(
        action=action,
        msg=msg or _default_message_for(action),
        title=cfg.title,
        error_code=error_code,
        exc=exc,
        extra=extra or {},
        cfg=cfg,
    )
    return handler(ctx)



# === DEBUG TESTS FOR EACH HANDLER ===
if __name__ == "__main__" and DEBUG_THIS_MODULE:
    print("=== Running Dispatcher Debug Tests ===")

    cfg = DispatcherConfig(
        title="Test Dispatcher",
        alert_recipients="owen.clancey@nyulangone.org"
    )

    # Create a simple simulated exception
    try:
        raise ValueError("Simulated test exception")
    except Exception as e:
        test_exc = e
    
    def test_action(action):
        print(f"\n--- Testing {action.value} ---")
        try:
            outcome = dispatch_action(
                action,
                msg=f"Test message for {action.value}",
                error_code=f"E-TEST-{action.name[:4].upper()}",
                exc=test_exc,
                extra={"test_key": "test_value"},
                cfg=cfg,
            )
            print(f"Outcome for {action.value}:")
            print(f"  user_choice: {outcome.user_choice}")
            print(f"  did_skip: {outcome.did_skip}")
            print(f"  retry_attempted: {outcome.retry_attempted}")
            print(f"  should_abort: {outcome.should_abort}")
            print(f"  exit_code: {outcome.exit_code}")
            print(f"  did_save: {outcome.did_save}")
        except Exception as err:
            print(f"Handler for {action.value} raised exception: {err}")
    
    test_action(RecommendedAction.ALERT_PHYSICIST)
    
    # for action in RecommendedAction:
    #     if action != RecommendedAction.SAVE_AND_EXIT:
    #         test_action(action)
    #     else:
    #         try:
    #             from connect import await_user_input
    #             await_user_input(message="Make a change to the plan to test the SAVE_AND_EXIT action in error_dispatcher.py.")
    #             action = RecommendedAction.SAVE_AND_EXIT
    #             test_action(action)
    #         except Exception:
    #             print("SAVE_AND_EXIT was not properly dispatched.  Likely due to running outside of Raystation.  See debug code at the end of error_dispatcher.py")

    print("\n=== Dispatcher Debug Tests Complete ===")

    
    
    