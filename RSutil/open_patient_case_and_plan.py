"""
RSutil/open_patient_case_and_plan.py
------------------------------------

Opens a patient, case, and plan in RayStation.

Provides a single function, `open_patient_case_and_plan()`, that loads the
specified patient by MRN, case name, and plan name, or defaults to the current
open entities if arguments are omitted. Used by other RSutil modules to ensure
the correct RayStation context before performing operations.

Raises:
    Exception: If zero or multiple patients match the given MRN.
    ValueError: For reporting or validation failures.

Created on Thu Oct 23 11:02:18 2025
@author: clanco01
"""
from __future__ import annotations

# === Woring directory ===
import sys
sys.path.append(r"\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
sys.path.append(r"F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")

# === Logger setup ===
from RSutil.LogUtil.rs_logging import LOGGERS
_logger = LOGGERS["system"]

# === RayStation import ===
try:
    from connect import get_current
    RAYSTATION_AVAILABLE = True
except Exception:
    _logger.warning("RayStation environment not detected.")
    RAYSTATION_AVAILABLE = False


def open_patient_case_and_plan(
        mrn: str | None = None, 
        case_name: str | None = None,
        plan_name: str | None = None,
) -> None:
    """
    Opens a patient, patient's case, and patient's plan
    
    Parameters
    ----------
    mrn : str, optional
        PatientID of patient.  If None, defaults to the current patient.
    case_name : str, optional
        Case name to open.  If None, defaults to the current patient's case.
    plan_name : str, optional
        Plan name to open.  If None, defaults to the current patient's plan.

    Raises
    ------
    Exception
        Zero or more than one patient found in the database.  Can not proceed.
    ValueError
        Raised error for reporting.

    Returns
    -------
    None

    """
    if RAYSTATION_AVAILABLE:
        try:
            patient_db = get_current('PatientDB')
            patient = None
            
            # Set patient
            if not mrn:
                try: 
                    # Set patient via get_current()
                    patient = get_current("Patient")
                    _logger.debug("No patient_id provided.  Using current Patient...")
                except:
                    raise ValueError("No patient MRN provided and no patient is currently open.")
            
            else:
                try:
                    info = patient_db.QueryPatientInfo(Filter = {'PatientID': mrn})
                except Exception as e:
                    raise RuntimeError("Input PatientID %s is not valid: %s", mrn, str(e))
                
                if len(info) != 1:
                    raise RuntimeError(
                        f"Expected exactly 1 patient for MRN {mrn}, found {len(info)}."
                    )
                
                # Use input mrn
                try:
                    patient = get_current("Patient") 
                    if patient.PatientID != mrn:
                        raise Exception
                    _logger.debug("Input patient_id %s matches current Patient.  Using current Patient...", mrn)
                except Exception:
                    _logger.debug("Opening patient: %s", mrn)
                    patient = patient_db.LoadPatient(PatientInfo = info[0])
            
            # Check for cases in patient
            if not patient.Cases:
                raise RuntimeError(f"Patient {mrn} has no cases.")
            
            # Set Case
            if not case_name:
                try:
                    current_case = get_current("Case")
                    case_name = current_case.CaseName
                    _logger.debug("No case_name provided.  Using current Case.")
                except Exception:
                    _logger.debug("No case_name provided, and current Case is unavailable.  Opening first Case...")
                    case_name = 0
                    patient.Save()
                    patient.Cases[case_name].SetCurrent()
            else:
                case_names = [case.CaseName for case in patient.Cases]
                if case_name not in case_names:
                    _logger.debug("Input case_name not in Cases.  Using first case...")
                    case_name = 0
                    try:
                        patient.Save()
                        patient.Cases[case_name].SetCurrent()
                    except Exception as e:
                        raise RuntimeError(str(e))
                else:
                    try:
                        current_case = get_current("Case")
                        if case_name == current_case.CaseName:
                            _logger.debug("Input case_name %s matches current Case.  Using current Case...", case_name)
                        else:
                            _logger.debug("Opening Case: %s", case_name)
                            patient.Save()
                            patient.Cases[case_name].SetCurrent()
                    except Exception:
                        _logger.debug("Opening Case in Exception Statement: %s", case_name)
                        patient.Save()
                        patient.Cases[case_name].SetCurrent()
            
            # Set plan
            if not plan_name:
                try:
                    current_plan = get_current("Plan")
                    plan_name = current_plan.Name
                    _logger.debug("No plan_name provided.  Using current Plan...")
                except Exception:
                    _logger.debug("Current Plan unavailable, and current Plan is unavailable.  Opening first Plan...")
                    patient.Save()
                    plan_name = 0
                    patient.Cases[case_name].TreatmentPlans[plan_name].SetCurrent()
            else:
                plan_names = [plan.Name for plan in patient.Cases[case_name].TreatmentPlans]
                if plan_name not in plan_names:
                    _logger.debug("Input plan_name not in TreatmentPlans.  Using first plan...")
                    plan_name = 0
                    try:
                        patient.Save()
                        patient.Cases[case_name].TreatmentPlans[plan_name].SetCurrent()
                    except Exception as e:
                        raise RuntimeError(str(e))
                else:
                    try:
                        current_plan = get_current("Plan")
                        if plan_name == current_plan.Name:
                            _logger.debug("Input plan_name %s matches current Plan.  Using current Plan...", plan_name)
                        else:
                            _logger.debug("Opening Plan: %s", plan_name)
                            patient.Save()
                            patient.Cases[case_name].TreatmentPlans[plan_name].SetCurrent()
                    except Exception:
                        _logger.debug("Opening Plan in Exception Statement: %s", plan_name)
                        patient.Save()
                        patient.Cases[case_name].TreatmentPlans[plan_name].SetCurrent()
            
            message = f"Opened -> patient_id: {mrn} | case: {case_name} | plan: {plan_name}."
            _logger.info(message)
            
            return
            
        except Exception as e:
            message = f"Failed to open patient_id: {mrn}, case: {case_name}, or plan: {plan_name}.  Following error: {str(e)}"
            _logger.exception(message)

    else:
        _logger.warning("open_patient_case_and_plan cannot be instantiated — RayStation 'connect' module missing.")
