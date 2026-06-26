"""
RSutils/get_windows_user_id.py

Returns the windows user id.

Created on Mon Oct  6 11:50:01 2025

@author: clanco01
"""

def get_windows_user_id():
    """Return the current Windows user ID in DOMAIN\\USERNAME format.

    Attempts to retrieve the user ID using .NET interop (via 
    `System.Security.Principal.WindowsIdentity`) when available. 
    Falls back to environment variables (`USERDOMAIN`, `USERNAME`) 
    or `getpass.getuser()` for compatibility with CPython.
    
    Returns:
        str: Uppercase Windows user ID in the format `DOMAIN\\USERNAME`, 
        or `"UNKNOWN\\USER"` if retrieval fails.
    """
    
    # Try .NET (works in IronPython and CPython with RS’s .NET interop)
    try:
        from System.Security.Principal import WindowsIdentity
        return str(WindowsIdentity.GetCurrent().Name).upper()
    except Exception:
        pass

    # Fallback to environment / getpass (works in CPython)
    try:
        import os, getpass
        dom = os.environ.get("USERDOMAIN", "")
        usr = os.environ.get("USERNAME", getpass.getuser())
        return (f"{dom}\\{usr}" if dom else usr).upper()
    except Exception:
        return "UNKNOWN\\USER"

