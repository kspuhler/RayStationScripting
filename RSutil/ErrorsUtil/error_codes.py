"""
RSutil/ErrorsUtil/error_codes.py

Defines error codes and their human-readable descriptions.

Class Variable Naming Format:
    <DOMAIN>_<RESOURCE>_<ISSUE>

Where:
    DOMAIN   (str): Broad functional category of the system.
    RESOURCE (str): Specific component or object where the error originates.
    ISSUE    (str): Nature of the problem (controlled vocabulary below).

ISSUE Vocabulary (Controlled Set):
    MISSING      : Required data or resource is absent
    INVALID      : Exists but fails validation
    FAILURE      : General execution failure or hard failure of an operation
    FAULT        : Configuration or setup problem that prevents operation
    TIMEOUT      : External system or internal call exceeded its allowed time
    ERROR        : Unexpected exception not classified by other terms
    UNSUPPORTED  : Operation is not supported
    OVERLOAD     : System exceeded resource limits
    DENIED       : Access or permission was blocked
    CONFLICT     : A resource state conflict occurred
    EXPIRED      : Time-sensitive token or object is no longer valid
    NOT_FOUND    : Reference to a resource that does not exist
    INCOMPLETE   : Partial data or state that blocks completion
    STALE        : Cached or stored data is no longer current or valid
    DUPLICATE    : Redundant or conflicting entries
    EMPTY        : Data exists but contains no usable values

Error Code Schema:
    Name:      <ERROR_CATEGORY>_<CONCISE_DESCRIPTION>
    Format:    E-<MOD>-<NUM>
    Example:   E-FUSN-001

    Format Components:
        E               : Indicates an error code
        <MOD>           : 4-letter uppercase identifier for a module/domain
                          Examples used in this file:
                            FUSN (Fusion), PLAN (PlanGen), DOSE (Dose),
                            DATA (Data I/O), UIUX (User Interface),
                            CONF (Configuration), AUTH (Authentication),
                            NETW (Networking), FILE (Filesystem), 
                            SYSF (System/execution failure), SYSM (System mgmt)
        <NUM>           : Zero-padded numeric identifier unique within each module group

Description Guidelines:
    - Short, clear, complete sentences.
    - Avoid internal abbreviations or dynamic values.
    - Describe both the failure and, where possible, the cause or context.

Linking to system actions:
    Each error is paired with a Severity and a RecommendedAction.
    The classes below group canonical ErrorDefinition instances by the
    *RecommendedAction* your handler should take when this error is raised.

Usage pattern:
    from Errors.error_codes import PROMPT_USER
    try:
        ...
    except ValueError as e:
        report_error(PROMPT_USER.UI_SELECT_INVALID, e, context={"module":"CreateFusion"})
        # your central dispatcher can then perform the PROMPT_USER action.
"""
from __future__ import annotations

# === WORKING DIRECTORY ===
import sys
sys.path.append(r"\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
sys.path.append(r"F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")

# === STANDARD IMPORTS ===
from dataclasses import dataclass

# === LOCAL IMPORTS ===
from RSutil.ErrorsUtil.settings_errors import Severity, RecommendedAction


@dataclass(frozen=True)
class ErrorDefinition:
    code: str
    description: str
    severity: Severity
    recommended_action: RecommendedAction


class LOG_ONLY:
    DATA_EMPTY_INPUT = ErrorDefinition(
        code="E-DATA-001",
        description="Function received empty input payload.",
        severity=Severity.INFO,
        recommended_action=RecommendedAction.LOG_ONLY,
    )


class RETRY_OPERATION:
    NETW_TIMEOUT = ErrorDefinition(
        code="E-NETW-001",
        description="Network request timed out.",
        severity=Severity.WARNING,
        recommended_action=RecommendedAction.RETRY_OPERATION,
    )


class SKIP_STEP:
    UIUX_MISSING_OPTIONAL_INPUT = ErrorDefinition(
        code="E-UIUX-001",
        description="User did not provide an optional field. Skipping step.",
        severity=Severity.INFO,
        recommended_action=RecommendedAction.SKIP_STEP,
    )
    SYSF_UNHANDLED_EXCEPTION = ErrorDefinition(
        code="E-SYSF-002",
        description="Unhandled system exception.  Skipping step.",
        severity=Severity.INFO,
        recommended_action=RecommendedAction.SKIP_STEP,
    )
    UIUX_RSUI_FAILURE = ErrorDefinition(
        code="E-UIUXF-002",
        description="Unhandled RayStation UI exception.  Skipping step.",
        severity=Severity.INFO,
        recommended_action=RecommendedAction.SKIP_STEP,
    )


class RELOAD_PLAN:
    PLAN_BEAMSET_NOT_FOUND = ErrorDefinition(
        code="E-PLAN-001",
        description="Requested beam set was not found in the current case.",
        severity=Severity.WARNING,
        recommended_action=RecommendedAction.RELOAD_PLAN,
    )
    PATIENT_DATA_NOT_FOUND = ErrorDefinition(
        code="E-DATA-003",
        description="Requested patient data was not found in the current case.",
        severity=Severity.WARNING,
        recommended_action=RecommendedAction.RELOAD_PLAN,
    )


class PROMPT_USER:
    UIUX_SELECT_INVALID = ErrorDefinition(
        code="E-UIUX-001",
        description="User made an invalid selection.  Retry or cancel.",
        severity=Severity.WARNING,
        recommended_action=RecommendedAction.PROMPT_USER_RETRY,
    )
    UIUX_USER_ACKNOWLEDGE = ErrorDefinition(
        code="E-UIUX-002",
        description="User made to acknowledge action.",
        severity=Severity.INFO,
        recommended_action=RecommendedAction.PROMPT_USER_ACKNOWLEDGE,
    )


class ABORT_SCRIPT:
    DATA_REQUIRED_MISSING = ErrorDefinition(
        code="E-DATA-002",
        description="Required input data is missing.",
        severity=Severity.ERROR,
        recommended_action=RecommendedAction.ABORT_SCRIPT,
    )


class ALERT_PHYSICIST:
    SYSF_UNHANDLED_EXCEPTION = ErrorDefinition(
        code="E-SYSF-001",
        description="Unhandled system exception. The physics team has been notified.",
        severity=Severity.CRITICAL,
        recommended_action=RecommendedAction.ALERT_PHYSICIST,
    )
    DATA_REQUIRED_MISSING = ErrorDefinition(
        code="E-DATA-003",
        description="Required input data is missing.",
        severity=Severity.ERROR,
        recommended_action=RecommendedAction.ALERT_PHYSICIST,
    )
    DATA_ACCESS_FAILURE = ErrorDefinition(
        code="E-DATA-004",
        description="Failed to read or access required patient or case data.",
        severity=Severity.ERROR,
        recommended_action=RecommendedAction.ALERT_PHYSICIST,
    )
    RAYSTATION_API_FAILURE = ErrorDefinition(
        code="E-RYST-00",
        description="Failed to connect to RayStation API.",
        severity=Severity.ERROR,
        recommended_action=RecommendedAction.ALERT_PHYSICIST,
    )


class SAVE_AND_EXIT:
    FILE_SYSTEM_DENIED = ErrorDefinition(
        code="E-FILE-001",
        description="Filesystem permission denied when writing output.",
        severity=Severity.ERROR,
        recommended_action=RecommendedAction.SAVE_AND_EXIT,
    )



