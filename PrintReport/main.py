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


def makeRoisVisibleForDvh():
    pat = get_current("Patient")
    pm = get_current("Case")
    pm = pm.PatientModel
    
    for roi in pm.RegionsOfInterest:
        if roi.Type.lower() in ["gtv", "ctv", "ptv", "organ"] and not any(x in roi.Name.lower() for x in ["shell", "ring"]):
            pat.SetRoiVisibility(RoiName = roi.Name, IsVisible=True)
        else:
            
            pat.SetRoiVisibility(RoiName = roi.Name, IsVisible=False)
    return

def getFileName():
    base= "\\\Client\F$\SHARING\Radiation Oncology Physics\Raystation Plan PDFs"
    
    pat = get_current("Patient")
    plan = get_current("Plan")
    mrn = pat.PatientID
    planName = plan.Name
    
    out = os.path.join(base, mrn)
    if not os.path.exists(out):
        print(f"MAKING DIR {out}")
        os.mkdir(out)
    out = os.path.join(out, planName + ".pdf") 
    out + ".pdf"
    
    return out

def printAndSavePdf():
    
    templateRst = "\\\Client\\F$\\SHARING\\Radiation Oncology Physics\\RayStation\\Report Templates\\Lean-and-mean.rst"
    fname = getFileName()
    print(fname)
    
    pat = get_current("Patient")
    b = get_current("BeamSet")
    pat.Save()
    try:
        b.CreateReportFromTemplateFile(templateFileName = templateRst, filename = fname, ignoreWarnings=False)
    except:
        b.CreateReportFromTemplateFile(templateFileName = templateRst, filename = fname, ignoreWarnings=True)
        


if __name__ == "__main__":

    makeRoisVisibleForDvh()
    printAndSavePdf()
    