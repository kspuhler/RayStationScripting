try:
    from connect import *
except:
    pass

import re
import sys
sys.path.append("F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
sys.path.append("\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")

from PlanCheck.Classes.Model.BeamSetCheckModel import BeamSetCheckModel

class VarianBeamSetCheckModel(BeamSetCheckModel):
    
    def __init__(self, beamSet):
        super().__init__(beamSet)
    
    
    def runGenericBeamSetChecks(self): #ovferload generic checks for varian specific instances
        super().runGenericBeamSetChecks()
        #self.checkFieldNames()
        
    
    def runSpecificBeamSetChecks(self):  
        self.runSupportStructureCheck()
        self.checkMinMonitorUnits()
        self.checkForCouchKicks()
        
        
    def checkForCouchKicks(self):
        beams = self.beamSet.Beams
        for b in beams:
            if b.CouchRotationAngle != 0:
                self.specificBeamSetCheckResults += f'***Couch kick of {b.CouchRotationAngle} for beam {b.Name}\n'
        
        
    def checkForSetupFields(self):
        try: #Check if there is a general setupbeams elements
            sb= None
        except: #TODO
            pass
        
    def checkMinMonitorUnits(self, minMu = 10.0):
        for b in self.beamSet.Beams:
            if b.BeamMU<minMu:
                self.specificBeamSetCheckResults += f'***Beam {b.Name} has fewer than {minMu} MUs***'
        
    def checkFieldNames(self):
        beams = self.beamSet.Beams
        
        basePattern = r'^(\d+)\s*_*\s*[gG]\s*_*\s*'
        wrong = [] 
        
        for b in beams:
            gantryStart =  str(int(round(b.GantryAngle)))            
            if not b.ArcStopGantryAngle: #isn't vmat'   
                match = basePattern + rf'{gantryStart}$'
            elif b.ArcStopGantryAngle:
                gantryStop = str(int(round(b.ArcStopGantryAngle)))
                match = basePattern + rf'{gantryStart}-{gantryStop}$'
            
            #Do the actual check
            if not re.match(match, b.Name):
                wrong.append(b.Name)
        
        if wrong: #If any wrong beam names found
            self.genericBeamSetCheckResults += f"Please verify beam names for {', '.join(str(x) for x in wrong)}\n"
        
        
    def displayRx(self):
        #overload generic rx display and include beam energies
        super().displayRx()
        energies = []
        
        for b in self.beamSet.Beams:
            if not b.BeamQualityId in energies:
                energies.append(b.BeamQualityId)
                
        
        energiesFormatted = ', '.join(str(item) for item in energies)
        self.genericBeamSetCheckResults += f'Energies employed: {energiesFormatted}\n' 

        
        