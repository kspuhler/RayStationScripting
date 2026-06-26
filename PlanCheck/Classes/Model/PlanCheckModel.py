#Author KDS
#Implements a number of checks common to all plan checks, as well as some overridable methods

try:
    from connect import *
except:
    pass

import sys
sys.path.append("F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
sys.path.append("\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")

from Planning.Structures.Functions.checkForContour import checkForContour
from PlanCheck.Classes.Model.BeamSetFactoryClass import BeamSetFactoryClass



class PlanCheckModel(object):

    def __init__(self) -> None:
        
        self.getPlanInfo()
        self.checkApprovalStatus()
        self.createBeamSetCheckModels()
        
        
        
    def getPlanInfo(self):
        self.case = get_current("Case")        
        self.rois = self.case.PatientModel.RegionsOfInterest        
        self.plan = get_current("Plan") #Treatment plan, not beamsets
                
        #Patient demographic stuff
        patient = get_current("Patient")
        self.patName  = patient.Name
        self.mrn      = patient.PatientID
        
    def createBeamSetCheckModels(self):
        """Creates a BeamSetCheckModel for each beamset in the plan."""
        self.beamSetCheckModels = [
            BeamSetFactoryClass.createBeamSet(b)
            for b in self.plan.BeamSets
        ]
        
    def getBeamSetCheckModels(self):
        """Returns the list of BeamSetCheckModel instances."""
        return self.beamSetCheckModels

        
    def getTargets(self): ##TODO: List of target structures and their associated rx
        pass
    
    def checkApprovalStatus(self):
        self.approved = True
        if self.plan.Review:
            if self.plan.Review.ApprovalStatus == 'Approved':
                return
            else:
                self.approved = False
        else:
            self.approved = False
        return
    
    def checkForRoiAlerts(self):

        # checkDict key = what the script will call it, vals = [list of names possibly used]
        checkDict = {'CIED': ['CIED', 'PaceMaker', 'Pace_Maker', "Pace Maker"],
                     'KDS Test ROI': ['aaa2']}

        outList = []

        # Loop through the checkDict
        for k, v in checkDict.items():
            # For each term in the list of values, check if it's in roiList
            if any(val in [roi.Name for roi in self.rois] for val in v):
                # If a match is found, append the key to the output list
                outList.append(k)

        return outList
    
    def checkForOverrides(self):
        #Check for Rois with material overrides
        overridden = []
        for r in self.rois:
            if 'couch' in r.Name.lower(): #just skip over the couch structures
                continue
            
            if r.RoiMaterial: #if it is overridden
                overridden.append(r.Name)
        
        return overridden 
                
            
            

            
if __name__ == "__main__":
    pass