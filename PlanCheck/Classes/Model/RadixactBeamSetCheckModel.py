import sys
sys.path.append("F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
sys.path.append("\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")

from PlanCheck.Classes.Model.BeamSetCheckModel import BeamSetCheckModel

class RadixactBeamSetCheckModel(BeamSetCheckModel):
    
    def __init__(self, beamSet):
        super().__init__(beamSet)
        self.runSupportStructureCheck()
        
    def runSpecificBeamSetChecks(self):
        #Checks synchrony info
        if not self.checkForMotionTracking():
            self.specificBeamSetCheckResults += "Synchrony: OFF.\n"
        elif self.checkForMotionTracking():
            tmp = "Synchrony: ON. "
            if self.calculateGantryPeriod()>30.0:
                tmp += f"***GANTRY PERIOD {self.calculateGantryPeriod()}***\n"
            self.specificBeamSetCheckResults += tmp
    
    def runSupportStructureCheck(self):
        roiNames = [x.Name for x in self.rois]
        
        # Structure lists for different machines

        radixact = ['Upper pallet', 'Lower pallet']
        truebeamStructures = ['CouchInterior', 'CouchSurface', 'CouchRailRight_In', 'CouchRailLeft_In', 
                              'CouchRailRight_Out', 'CouchRailLeft_Out']
        
        # Check for Radixact structures
        radixactCheck = True
        for r in radixact:
            if r not in roiNames:
                radixactCheck = False
        
        # Check for Truebeam structures and ensure none are present in Radixact
        for structure in truebeamStructures:
            if structure in roiNames:
                self.specificBeamSetCheckResults += f"***WARNING: Found Truebeam structure {structure} in Radixact beamset\n"
                return  # Exit after finding the first conflicting structure
    
        # If Radixact structures are not found, add a warning
        if not radixactCheck:
            self.specificBeamSetCheckResults += "***WARNING: Did not find appropriate Radixact structures\n"
        else:
            self.specificBeamSetCheckResults += "Radixact beamset has valid structures\n"
            
        # Check if Truebeam structures exist and conflict with the expected Radixact structures
        for structure in truebeamStructures:
            if structure in roiNames:
                self.specificBeamSetCheckResults += f"***WARNING: Found Truebeam structure {structure} in Radixact beamset\n"
                return  # Exit after finding the first conflicting structure
        return

    def checkForMotionTracking(self):
        if self.beamSet.PatientSetup.MotionSynchronization:
            return True #do shit to process whether motiont racking is good to go
            
        else:
            return False
    def calculateGantryPeriod(self):
        b = self.beamSet.Beams[0] #only one beam bc radixact
        period = b.BeamMU*51 
        return period
        
        