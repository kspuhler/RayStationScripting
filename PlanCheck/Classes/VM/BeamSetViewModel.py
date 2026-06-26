
import sys
sys.path.append("F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
sys.path.append("\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")

from PlanCheck.Classes.Model.BeamSetCheckModel import BeamSetCheckModel

# BeamSetViewModel.py
class BeamSetViewModel:
    def __init__(self, beamSetCheckModel):
        self.beamSetCheckModel = beamSetCheckModel
        self.getBeamsetInfo()
        self.getGenericBeamSetChecks()  
        self.getSpecificBeamSetChecks()
    

    def getBeamsetInfo(self):
        
            self.name = self.beamSetCheckModel.beamSet.DicomPlanLabel
            self.machine = self.beamSetCheckModel.beamSet.MachineReference['MachineName']
            self.genericBeamSetChecks = self.getGenericBeamSetChecks()
        

    def getGenericBeamSetChecks(self):
        out = "Generic BeamSet Checks: \n"

        self.genericBeamSetCheckInfo =  out + self.beamSetCheckModel.genericBeamSetCheckResults
        
    def getSpecificBeamSetChecks(self):
        out = "Specific BeamSet Checks: \n"
        self.specificBeamSetCheckInfo = out + self.beamSetCheckModel.specificBeamSetCheckResults

    def runBeamsetCheck(self):
        result = "Beamset Check Passed"
        
        try:
            self.beamSetCheckModel.runCollisionCheck()
        except NotImplementedError:
            result = "Collision Check Not Implemented"

        return f"Beamset {self.beamSetCheckModel.beamSet.DicomPlanLabel}: {result}"
