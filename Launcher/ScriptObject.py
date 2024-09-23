from connect import *

import tkinter as tk
import sys
sys.path.append("\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
sys.path.append("F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")

from FrontEnd.GenericPopup import GenericPopup


class ScriptObject(object):
    
    def __init__(self, verboseExecution=True, runPreChecks=True, inferPhysician=True):
        self.verboseExecution = verboseExecution
        self.runPreChecks = runPreChecks

        if self.verboseExecution:
            self.showInfo()
        
        self.getCurrent()
        
        if self.runPreChecks:
            self.preChecks()
        
        if inferPhysician:
            self.determinePhysician()
        
    def showInfo(self):
        w = GenericPopup(title='Script Execution Info', message=self.__doc__)
        w.showPopup()
        
    def determinePhysician(self):
        
        self.physician = None
        
        for ii in ['JH', 'JL', 'TC', 'AS', 'MT', 'JK']:
            if ii.lower() == self.case.Physician.Name.lower():
                self.physician = ii
                print(f"Physician is: {self.physician}")
                return
        print(f"Physician cannot be determined and was set to default value None.")
        
        
    def preChecks(self):
        raise NotImplementedError
                
    def getCurrent(self):
        try:
            self.plan = get_current('Plan')
        except:
            print("Failed to load plan.")        
        try:
            self.exam = get_current('Examination')
        except:
            print("Failed to load exam.")       
        try:
            self.case = get_current('Case')
        except:
            print("Failed to load case.")            
        try:
            self.pm   = self.case.PatientModel
        except:
            print("Failed to load patient model.")         
        try:
            self.bs   = get_current("BeamSet")
        except:
            print("Failed to load beamset")