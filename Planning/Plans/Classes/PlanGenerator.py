# -*- coding: utf-8 -*-
"""
Created on Wed Sep 18 13:30:19 2024

@author: spuhlk01
"""

#Author KDS
#Main classes for generating plans

from connect import * 
import re

import os
import sys


sys.path.append("\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
sys.path.append("F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")


from RSutil.functions import interpretCTSimOrientation
from RSutil.variables import ALL_MACHINES, TRUEBEAMS, RADIXACTS
from Launcher.ScriptObject import ScriptObject
from Planning.BeamTemplates.SetupBeams import SetupBeams
from Planning.Plans.Preplan.MachinePreplan import TrueBeamPrePlan
from Planning.Structures.Classes.TargetStructureInterpreter import TargetStructureInterpreter
from Planning.Structures.Functions.returnRoisOfType import returnRoisOfType
from FrontEnd.PlanGeneratorFrontEnd.PlanGeneratorFrontEnd import PlanGeneratorFrontEnd


class PlanGenerator(ScriptObject):

    def __init__(self, simPlan = None, verboseExecution = False, runPreChecks = True, *args, **kwargs) -> None:
        
        super().__init__(verboseExecution=verboseExecution, runPreChecks=runPreChecks)
        self.machine       = None  # Placeholder for selected machine
        self.rx            = None  # Placeholder for Rx value
        self.fractions     = None  # Placeholder for Fractions value
        self.planName      = None
        self.targetOptions = self.getTargetROIs()  # Populate options for target dropdown
        
        self.launchWindow()
        self.generatePlan()
        
    def getTargetROIs(self):
        default = ["No PTVs found in structure set"]
        check = returnRoisOfType(["ptv", "ctv", "gtv"])
        
        if check:
            return check
        else:
            return default
        
    
    def preChecks(self):
        pass
    
    def launchWindow(self):
    # Launch the PlanGeneratorFrontEnd window with ALL_MACHINES and other options
        app = PlanGeneratorFrontEnd(ALL_MACHINES, self.targetOptions, self)
        app.mainloop()
            
    def copySimToPlanBeamset(self):
        
        #get iso coordinates from sim
        tmpBeams = self.plan.BeamSets['SIM'].Beams #TODO: Multiiso currenlty only works for one iso
        tmpIso   = tmpBeams[0].Isocenter.Position
        x = tmpIso['x']
        y = tmpIso['y']
        z = tmpIso['z']
        
    def generatePlan(self):
        # Logic for generating plan
        if self.machine and self.rx and self.fractions and self.planName:
                print(f"Generating plan {self.planName} for machine: {self.machine}, Rx: {self.rx}, Fractions: {self.fractions}")
                newPlan = self.case.AddNewPlan(PlanName=self.planName, PlannedBy="", Comment="", ExaminationName=self.exam.Name, IsMedicalOncologyPlan=False, AllowDuplicateNames=False)
                
                bs = newPlan.AddNewBeamSet(Name=self.planName, ExaminationName=self.exam.Name, MachineName=self.machine, Modality="Photons", TreatmentTechnique="VMAT", PatientPosition=interpretCTSimOrientation(self.exam), 
                                           NumberOfFractions=self.fractions, CreateSetupBeams=True, UseLocalizationPointAsSetupIsocenter=False, UseUserSelectedIsocenterSetupIsocenter=False, Comment="", 
                                           RbeModelName=None, EnableDynamicTrackingForVero=False, NewDoseSpecificationPointNames=[], NewDoseSpecificationPoints=[], 
                                           MotionSynchronizationTechniqueSettings={ 'DisplayName': None, 'MotionSynchronizationSettings': None, 'RespiratoryIntervalTime': None, 
                                                                                   'RespiratoryPhaseGatingDutyCycleTimePercentage': None, 'MotionSynchronizationTechniqueType': "Undefined" }, 
                                           Custom=None, ToleranceTableLabel="IMRT")
                newPlan.TreatmentPhases[0].DeliveryBeamSets[0].AddRoiPrescriptionDoseReference(RoiName=self.target, DoseVolume=self.coverageLevel, PrescriptionType = "DoseAtVolume", DoseValue=self.rx)
                
                self.machinePrePlanCall(bs)
                

        else:
                print("Missing input for plan generation")
                sys.exit()
        
    def machinePrePlanCall(self, bs):
        if self.machine in TRUEBEAMS:
            TrueBeamPrePlan(self.case, self.exam, bs)
                
        
                
                

        
        
    #Setters from front end
    def setTarget(self, target):
        # Set the target selected from the window
        self.target = target
        print(f"Selected target: {self.target}")
        
    def setRxAndCoverageLevel(self, rx, coverageLevel):
        # Set the Rx and Coverage Level values from the window
        self.rx = rx
        # Handle percentage sign
        if coverageLevel is not None:
            coverageLevel = coverageLevel.replace('%', '').strip()
            try:
                self.coverageLevel = float(coverageLevel)
            except ValueError:
                print("Invalid coverage level value. Keeping the default.")
        else:
            self.coverageLevel = 95  # Default if empty
        print(f"Rx: {self.rx}, Coverage Level: {self.coverageLevel}")

    def setFractions(self, fractions):
        # Set the Fractions value from the window
        self.fractions = fractions
        print(f"Fractions: {self.fractions}")

    def setPlanName(self, planName):
        # Set the Plan Name from the window
        self.planName = planName
        print(f"Plan Name: {self.planName}")
    
    def setMachine(self, machine):
        # Set the machine selected from the window
        self.machine = machine
        print(f"Selected machine: {self.machine}")

        
        


        

if __name__ == '__main__':
    from connect import *
    tmp = PlanGenerator()
    


