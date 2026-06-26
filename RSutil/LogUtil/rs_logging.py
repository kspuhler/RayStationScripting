r"""
RSutil\LogUtil\rs_logging.py

Provides a utility function to configure and return a logger
for various modules and components.

Functions:
    setup_logger: Initializes a logger with UTC timestamps and writes logs to a specified file.

Usage:
    import rs_logging   # Initializes all LOGGERS
    your_logger = LOGGERS[logger_name]
""" 
from __future__ import annotations

# === DEBUG SETTINGS ===
DEBUG_THIS_MODULE = False

# === WORKING DIRECTORY ===
import sys
sys.path.append(r"\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
sys.path.append(r"F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")

# === IMPORTS ===
import logging
from logging.handlers import RotatingFileHandler
import os
from datetime import datetime

# === LOCAL IMPORTS ===
from RSutil.LogUtil import settings_logging

# === Global dictionary for accessing loggers ===
LOGGERS = {}


def _localtime_converter(secs):
    return datetime.fromtimestamp(secs).timetuple()

def _close_handlers_for_path(path: str):
    """Close any open FileHandlers across all loggers that target `path`."""
    try:
        # root logger
        for h in list(logging.getLogger().handlers):
            if getattr(h, "baseFilename", None) == path:
                h.close()
                logging.getLogger().removeHandler(h)

        # all named loggers
        for name, logger_obj in logging.Logger.manager.loggerDict.items():
            if not isinstance(logger_obj, logging.Logger):
                continue
            for h in list(logger_obj.handlers):
                if getattr(h, "baseFilename", None) == path:
                    h.close()
                    logger_obj.removeHandler(h)
    except Exception:
        pass

def _tail_truncate_file(path: str, max_bytes: int) -> None:
    """
    Truncate `path` in place to the last `max_bytes` bytes, preserving newest content.
    Writes a one-line header noting the truncation. Works even on large files
    without loading the whole thing into memory.
    """
    try:
        size = os.path.getsize(path)
        if size <= max_bytes:
            return

        keep = max_bytes
        with open(path, "rb") as f:
            f.seek(size - keep, os.SEEK_SET)
            tail = f.read()

        # Best effort to start on a line boundary — look for first newline
        nl = tail.find(b"\n")
        if nl != -1 and nl + 1 < len(tail):
            tail = tail[nl + 1 :]

        header = (f"[TRUNCATED: original={size} bytes, kept={len(tail)} bytes]\n").encode("utf-8")

        with open(path, "wb") as f:
            f.write(header)
            f.write(tail)
    except Exception:
        pass


def setup_logger(
        name: str = "system", 
        log_path: str = settings_logging.LOG_PATHS["system"],
        log_level: str = settings_logging.LOG_LEVELS["system"],
) -> logging.Logger:
    """
    Set up and configure a logger for a module or component.

    Args:
        name (str, optional): Name of the logger. Defaults to "system".
        log_path (str, optional):): Full path to the log file.
        log_level (str, optional):): Log level of the log file.

    Returns:
        logging.Logger: Configured logger instance.
    """
    # Check if log_path matches any known paths from settings
    if log_path not in settings_logging.LOG_PATHS.values():
        raise ValueError(
            f"Invalid log_path provided: {log_path}. "
            f"Must be one of settings.LOG_PATHS values."
        )
    
    if os.path.exists(log_path):
        _close_handlers_for_path(log_path)
        _tail_truncate_file(log_path, settings_logging.LOG_MAX_BYTES)
        
    handler = RotatingFileHandler(
        log_path,
        maxBytes=settings_logging.LOG_MAX_BYTES,
        backupCount=settings_logging.LOG_BACKUP_COUNT, 
        encoding="utf-8",
    )
    handler.setLevel(log_level)    
    
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    logger.propagate = False
    
    for h in list(logger.handlers):
        if getattr(h, "baseFilename", None) == log_path:
            h.close()
            logger.removeHandler(h)
        
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(name)s - %(filename)s - %(message)s")
    formatter.converter = _localtime_converter
    
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    return logger

def initialize_all_loggers():
    """
    Initialize all loggers defined in LOGGING['filenames'].
    """
    for logger_name, full_path in settings_logging.LOG_PATHS.items():
        LOGGERS[logger_name] = setup_logger(
            name=logger_name, 
            log_path=full_path,
            log_level=settings_logging.LOG_LEVELS[logger_name]
        )

def set_logger_mode(logger: logging.Logger, mode: str | None = None) -> None:
    """
    Set the level for the specified logger and all its handlers.

    If `mode` is omitted, the level is taken from LOG_SPECS based on logger.name.

    Args:
        logger (logging.Logger): The logger instance to modify (e.g. LOGGERS["system"]).
        mode (str | None): Optional override mode such as "debug", "info", "warning", or "error".
                           If None, uses the default level in LOG_SPECS[logger.name]["level"].

    Example:
        _logger = LOGGERS["system"]
        set_logger_mode(_logger)          # Use level from LOG_SPECS["system"]
        set_logger_mode(_logger, "debug") # Force DEBUG level
    """
    default_level = getattr(logging, settings_logging.LOG_SPECS[logger.name]["level"].upper(), logging.INFO)
    allowed_levels = ("debug", "info", "warning", "error")

    try:
        if mode and mode.lower() in allowed_levels:
            level = getattr(logging, mode.upper())
        else:
            level = default_level

        logger.setLevel(level)
        for h in logger.handlers:
            h.setLevel(level)
        logger.info(f"Logger '{logger.name}' set to {logging.getLevelName(level)}")

    except Exception as e:
        logger.setLevel(default_level)
        for h in logger.handlers:
            h.setLevel(default_level)
        logger.warning(
            f"Reverted '{logger.name}' to default level {logging.getLevelName(default_level)} "
            f"after error: {e}"
        )


# === Auto-initialize all loggers when module is loaded ===
initialize_all_loggers()


# === RUN LOCALLY FOR DEBUGGING ===
if __name__ == "__main__" and DEBUG_THIS_MODULE:
    
    for logger_name in settings_logging.LOG_PATHS.keys():
        LOGGERS[logger_name].critical("Testing RSutil/loggings.py in debug mode...")