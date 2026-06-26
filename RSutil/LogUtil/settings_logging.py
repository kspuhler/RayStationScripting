r"""
RSutil\LogUtil\settings_logging.py

This module defines logging settings.

Usage:
    Import settings directly to access any configuration constants globally.

Created on Mon Oct  6 09:02:34 2025

@author: clanco01
"""
from __future__ import annotations

#===IMPORTS===
import os

_CANDIDATE_ROOTS = [
    r"\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD",
    r"F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD",
]

for _root in _CANDIDATE_ROOTS:
    if os.path.isdir(_root):
        PROJECT_ROOT = _root
        break

# Environment can be: "production", "development", "test"
ENVIRONMENT = "production"

LOG_LEVEL = {
    "production": "INFO",
    "development": "DEBUG",
    "test": "WARNING",
}.get(ENVIRONMENT, "INFO")

LOG_DIRECTORY = os.path.join(PROJECT_ROOT, "Logs")

LOG_SPECS = {
    # Always-on verbose debug stream
    "debug":                            {"filename": "debug.log",                           "level": "DEBUG"},
    
    # System-wide - Log level of current environment
    "system":                           {"filename": "system.log",                          "level": LOG_LEVEL},
    "execution":                        {"filename": "execution.log",                       "level": LOG_LEVEL},
    
    # Script-specific - Log level of current environment
    "auto_fusion":                      {"filename": "auto_fusion.log",                     "level": LOG_LEVEL},
    "breast_sib":                       {"filename": "breast_sib.log",                      "level": LOG_LEVEL},
    "collision_model":                  {"filename": "collision_model.log",                 "level": LOG_LEVEL},
    "create_export_qa_plan":            {"filename": "create_export_qa_plan.log",           "level": LOG_LEVEL},
    "eqd2_summation":                   {"filename": "eqd2_summation.log",                  "level": LOG_LEVEL},
    "launch_rs_scripts_manual_website": {"filename": "launch_rs_scripts_manual_website.log","level": LOG_LEVEL},
    "set_max_mlc_jaws":                 {"filename": "set_max_mlc_jaws.log",                "level": LOG_LEVEL},
    "tps_qa":                           {"filename": "tps_qa.log",                          "level": LOG_LEVEL},

    # Triage with error/critical only
    "error":                            {"filename": "errors.log",                          "level": "ERROR"},
    
    # Research logs
    "rag_llm":                          {"filename": "rag_llm.log",                         "level": LOG_LEVEL},
}

LOG_PATHS = {
    name: os.path.join(LOG_DIRECTORY, spec["filename"]) for name, spec in LOG_SPECS.items()
}

LOG_LEVELS = {
    name: (spec.get("level") or LOG_LEVEL) for name, spec in LOG_SPECS.items()
}

LOG_FILENAMES = {name: spec["filename"] for name, spec in LOG_SPECS.items()}

LOG_PATH_SYSTEM = LOG_PATHS["system"]

LOG_MAX_BYTES = 10 * 1024 * 1024
LOG_BACKUP_COUNT = 5
