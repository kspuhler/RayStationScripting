# PlanCheckViewModel.py

import sys
sys.path.append("F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
sys.path.append("\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")

#Models
from PlanCheck.Classes.Model.PlanCheckModel import PlanCheckModel
from PlanCheck.Classes.Model.BeamSetFactoryClass import BeamSetFactoryClass
from PlanCheck.Classes.Model.BeamSetCheckModel import BeamSetCheckModel
#VM
from PlanCheck.Classes.VM.BeamSetViewModel import BeamSetViewModel

from connect import *


# PlanCheckViewModel.py
class PlanCheckViewModel:
    def __init__(self, planCheckModel):
        self.planCheckModel = planCheckModel
        self.beamSetViewModels = [
            BeamSetViewModel(beamSetCheckModel) 
            for beamSetCheckModel in self.planCheckModel.getBeamSetCheckModels()
        ]
    
    def runPlanChecks(self):
        # include other plan-level checks here
        return f"Approval Status: {'Approved' if self.planCheckModel.approved else '***NOT APPROVED***'}"
    
    def getBeamsetViewModels(self):
        return self.beamSetViewModels
    
    def getRoiAlerts(self):
        # Call the checkForRoiAlerts method from PlanCheckModel
        return self.planCheckModel.checkForRoiAlerts()  
    
    def getRoiOverrides(self):
        #Call the PlancheckModel checks for roi overrides
        formattedOutput = ''
        
        tmp = self.planCheckModel.checkForOverrides() #List of names of overridden rois
        
        formattedOutput += f'The following ROIs are overriden: {", ".join(tmp)}\n'
        print(formattedOutput)
        print("DEBUG:")
        print([x.Name.lower() for  x in self.planCheckModel.rois])
        if 'external' in [x.lower() for x in tmp]:
            if any('couch' in x.Name.lower() or 'rail' in x.Name.lower() for x in self.planCheckModel.rois):
                formattedOutput+=f'***WARNING***: External is overriden and couch structures are used!\n'
        
        return formattedOutput
            