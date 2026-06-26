#Changelog mainv3.py
#6.5.25 adding prompt for user to select additional structures like CIED
#1.12.26 adding handling for hand calc vs full report
#1.13.26 patched bug for DIBH
import os
import sys


import tkinter as tk
from tkinter import ttk


sys.path.append("F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
sys.path.append("\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")

from FrontEnd.GenericPopup import GenericPopup


try:
    from connect import *
except:
    pass

#CONFIG
REPORT_PATH =  "\\\Client\\F$\\SHARING\\Radiation Oncology Physics\\RayStation\\Report Templates"
FULL_REPORT_PATH = os.path.join(REPORT_PATH, "Lean-and-mean.rst")
HAND_CALC_REPORT_PATH = os.path.join(REPORT_PATH, "2D Calculation Report.rst")
COPYABLE_OUT_PATH = "F:\SHARING\Radiation Oncology Physics\Raystation Plan PDFs"


def showReportTypeWindow(defaultFullReport: bool = False):
    """
    Opens a simple Tkinter window with two radio options:
      - Full Report
      - Hand Calc Report

    Default selection:
      - Hand Calc Report (defaultFullReport=False)
      - Full Report (defaultFullReport=True)

    Returns:
      "Full Report" | "Hand Calc Report" | None (if canceled)
    """
    result = {"value": None}

    root = tk.Tk()
    root.title("Select Report Type")
    root.resizable(False, False)

    frame = ttk.Frame(root, padding=12)
    frame.grid(row=0, column=0, sticky="nsew")

    ttk.Label(frame, text="Choose report type:").grid(row=0, column=0, sticky="w", pady=(0, 8))

    reportTypeVar = tk.StringVar(value=("Full Report" if defaultFullReport else "Hand Calc Report"))

    ttk.Radiobutton(frame, text="Full Report",      variable=reportTypeVar, value="Full Report").grid(row=1, column=0, sticky="w")
    ttk.Radiobutton(frame, text="Hand Calc Report", variable=reportTypeVar, value="Hand Calc Report").grid(row=2, column=0, sticky="w")

    buttonRow = ttk.Frame(frame)
    buttonRow.grid(row=3, column=0, sticky="e", pady=(12, 0))

    def onOk() -> None:
        result["value"] = reportTypeVar.get()
        root.destroy()

    def onCancel() -> None:
        result["value"] = None
        root.destroy()

    okBtn = ttk.Button(buttonRow, text="OK", command=onOk)
    okBtn.grid(row=0, column=0, padx=(0, 8))

    cancelBtn = ttk.Button(buttonRow, text="Cancel", command=onCancel)
    cancelBtn.grid(row=0, column=1)

    root.protocol("WM_DELETE_WINDOW", onCancel)
    root.bind("<Return>", lambda _e: onOk())
    root.bind("<Escape>", lambda _e: onCancel())

    root.update_idletasks()
    w = root.winfo_width()
    h = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (w // 2)
    y = (root.winfo_screenheight() // 2) - (h // 2)
    root.geometry(f"{w}x{h}+{x}+{y}")

    okBtn.focus_set()
    root.mainloop()

    return result["value"]


def showCopyablePathWindow(pathToCopy: str, title: str = "Path"):
    """
    Shows a small window with a read-only, selectable path and a button that
    copies it to the clipboard and closes the window.
    """
    root = tk.Tk()
    root.title(title)
    root.resizable(False, False)

    frame = ttk.Frame(root, padding=12)
    frame.grid(row=0, column=0, sticky="nsew")

    ttk.Label(frame, text="Copy this path:").grid(row=0, column=0, sticky="w", pady=(0, 6))

    pathVar = tk.StringVar(value=pathToCopy)

    entry = ttk.Entry(frame, textvariable=pathVar, width=80)
    entry.grid(row=1, column=0, sticky="ew", pady=(0, 10))
    entry.state(["readonly"])

    buttonRow = ttk.Frame(frame)
    buttonRow.grid(row=2, column=0, sticky="e")

    def copyAndClose() -> None:
        root.clipboard_clear()
        root.clipboard_append(pathToCopy)
        root.update()  # ensures clipboard persists after window closes
        root.destroy()

    copyBtn = ttk.Button(buttonRow, text="Copy and Close", command=copyAndClose)
    copyBtn.grid(row=0, column=0)

    # Convenience: focus + select all
    root.update_idletasks()
    entry.focus_set()
    entry.selection_range(0, tk.END)

    # Enter copies, Esc closes
    root.bind("<Return>", lambda _e: copyAndClose())
    root.bind("<Escape>", lambda _e: root.destroy())
    root.protocol("WM_DELETE_WINDOW", root.destroy)

    # Center on screen
    root.update_idletasks()
    w = root.winfo_width()
    h = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (w // 2)
    y = (root.winfo_screenheight() // 2) - (h // 2)
    root.geometry(f"{w}x{h}+{x}+{y}")

    root.mainloop()



def checkIfFullCalc():
    '''if external is overridden to water it is a hand calc'''
    pm = get_current("Case")
    pm = pm.PatientModel
    exam = get_current("Examination")
    ss = pm.StructureSets[exam.Name]
    #Find external contour 
    
    for s in ss.RoiGeometries:
        if s.OfRoi.Type.lower() == 'external':
            external = s
        
    if hasattr(external.OfRoi.RoiMaterial, "OfMaterial"): 
        if  external.OfRoi.RoiMaterial.OfMaterial.Name.lower() == 'water':
            print("It is a hand calc")
            return False
    else:
        return True
    

def getStructuresInClinicalGoals():
    
    plan = get_current("Plan")
    
    clinicalGoalsIterable = plan.TreatmentCourse.EvaluationSetup.EvaluationFunctions
    
    roisInClinicalGoals = []
    
    for ii in clinicalGoalsIterable:
        if not ii.ForRegionOfInterest.Name in roisInClinicalGoals:
            roisInClinicalGoals.append(ii.ForRegionOfInterest.Name)
    
    return roisInClinicalGoals


def makeRoisVisibleForDvh():
    pat = get_current("Patient")
    pm = get_current("Case")
    pm = pm.PatientModel
    
    
    roisForDvh = getStructuresInClinicalGoals()
    
    
    for roi in pm.RegionsOfInterest:
        if roi.Name in roisForDvh:
            pat.SetRoiVisibility(RoiName = roi.Name, IsVisible=True)
        else:
            pat.SetRoiVisibility(RoiName = roi.Name, IsVisible=False)
    return

def getFileName():
    base= "\\\Client\F$\SHARING\Radiation Oncology Physics\Raystation Plan PDFs"
    
    
    case = get_current("Case")
    case = case.CaseName
    pat = get_current("Patient")
    plan = get_current("Plan")
    
    mrn = pat.PatientID
    planName = plan.Name
    
    out = os.path.join(base, mrn, case)
    if not os.path.exists(out):
        print(f"MAKING DIR {out}")
        os.makedirs(out)
    out = os.path.join(out, planName + ".pdf") 
    out + ".pdf"
        
    return out

def printAndSavePdf():
    selection = showReportTypeWindow(defaultFullReport=checkIfFullCalc())  # default behavior: Hand Calc Report
    if selection is None:
        return  # user canceled

    if selection == "Hand Calc Report":
        templateRst = HAND_CALC_REPORT_PATH
    else:
        templateRst = FULL_REPORT_PATH

    fname = getFileName()
    print(fname)

    pat = get_current("Patient")
    b = get_current("BeamSet")
    ui = get_current("ui")

    ui.ToolPanel.TabItem['ROIs'].Select()
    a = GenericPopup(
        title='Print PDF',
        message='Please select any additional ROIs for DVH and then click Okay to print your PDF.'
    )
    a.attributes('-topmost', True)
    a.showPopup()

    pat.Save()
    try:
        b.CreateReportFromTemplateFile(templateFileName=templateRst, filename=fname, ignoreWarnings=False)
    except:
        b.CreateReportFromTemplateFile(templateFileName=templateRst, filename=fname, ignoreWarnings=True)



if __name__ == "__main__":

    makeRoisVisibleForDvh()
    printAndSavePdf()
    

    