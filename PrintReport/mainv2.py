#Changelog 
#6.5.25 adding prompt for user to select additional structures like CIED

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
    ui = get_current("ui")
    
    ui.ToolPanel.TabItem['ROIs'].Select()
    a = GenericPopup(title='Print PDF', message='Please select any additional ROIs for DVH and then click Okay to print your PDF.')
    a.attributes('-topmost', True)
    a.showPopup()
    
    pat.Save()
    try:
        b.CreateReportFromTemplateFile(templateFileName = templateRst, filename = fname, ignoreWarnings=False)
    except:
        b.CreateReportFromTemplateFile(templateFileName = templateRst, filename = fname, ignoreWarnings=True)
        


if __name__ == "__main__":

    makeRoisVisibleForDvh()
    printAndSavePdf()
    