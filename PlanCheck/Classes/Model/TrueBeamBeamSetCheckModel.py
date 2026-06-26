import sys
sys.path.append("F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
sys.path.append("\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")

from PlanCheck.Classes.Model.VarianBeamSetCheckModel import VarianBeamSetCheckModel

class TrueBeamBeamSetCheckModel(VarianBeamSetCheckModel):
    
    def __init__(self, beamSet):
        super().__init__(beamSet)
        
    def runSpecificBeamSetChecks(self):
        super().runSpecificBeamSetChecks()
        self.runBeamChecks()
    
    def runSupportStructureCheck(self):
        
        roiNames = [x.Name for x in self.rois]
        
        couch = ['CouchInterior', 'CouchSurface']
        railsIn = ['CouchRailRight_In', 'CouchRailLeft_In']
        railsOut = ['CouchRailRight_Out', 'CouchRailLeft_Out']
        radixact = ['Upper pallet', 'Lower pallet']
        
        couchCheck = True
        for c in couch:
            if not c in roiNames:
                couchCheck = False
        # Check if both elements of railsIn or both elements of railsOut are in rios
        foundRails = (all(r in roiNames for r in railsIn) and not any(r in roiNames for r in railsOut)) or \
             (all(r in roiNames for r in railsOut) and not any(r in roiNames for r in railsIn))
        
        if couchCheck and foundRails:
            self.specificBeamSetCheckResults += "Found appropriate couch structures for Truebeam\n"
            
        else:
            self.specificBeamSetCheckResults += "***WARNING: Did not find appropriate couoch structures for Truebeam\n"
        
        for r in roiNames:
            if r in radixact:
                self.specificBeamSetCheckResults += "***WARNING: Beamset is for Truebeam but appears to have Radixact couch \n"
                return
        return
    
    def runBeamChecks(self):
        beams = self.beamSet.Beams
        #VMAT Checks
        #Check if arc rotations are okay
        if self.type == 'DynamicArc': #VMAT Checks!
            if len(beams) > 1: #idgaf about arc directions if it's only one of them! 
                lastDir = None
                for idx, b in enumerate(beams):
                    if not lastDir:
                        lastDir = b.ArcRotationDirection
                    else:
                        if b.ArcRotationDirection == lastDir:
                            self.specificBeamSetCheckResults += f'***WARNING: Beams {idx} and {idx+1} have same arc direction!\n'
                        else:
                            lastDir = b.ArcRotationDirection
        return
        
        


            
            
            