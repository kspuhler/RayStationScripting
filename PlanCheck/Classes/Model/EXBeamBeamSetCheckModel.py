import numpy as np

import sys
sys.path.append("F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
sys.path.append("\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")

from PlanCheck.Classes.Model.VarianBeamSetCheckModel import VarianBeamSetCheckModel

class EXBeamSetCheckModel(VarianBeamSetCheckModel):
    
    def __init__(self, beamSet):
        super().__init__(beamSet)
        
    
    def runSpecificBeamSetChecks(self):
        super().runSpecificBeamSetChecks()
        self.checkJawPositions()
    
    def runSupportStructureCheck(self):
        
        roiNames = [x.Name for x in self.rois]
        
        couch = ['CouchInterior', 'CouchSurface','CouchRailRight_In', 
                 'CouchRailLeft_In','CouchRailRight_Out', 'CouchRailLeft_Out', 'Upper pallet', 'Lower pallet']
        
        for r in roiNames:
            if r in couch:
                self.specificBeamSetCheckResults += "***WARNING: Incorrect couch structures found for 21EX\n"
                return     
        return
    
    def checkJawPositions(self):
        jaws = ["X1", "X2", "Y1", "Y2"]        
        out = ''
        for b in self.beamSet.Beams:
            print(b.Name)
            if b.Segments:
                for s in b.Segments:
                    for idx, j in enumerate(list(s.JawPositions)):
                        print(idx)
                        print(j)
                        if np.abs(j) > 19.9:
                            out += f'****Jaw position > 19.9 for beam {b.Name}, segment {s.SegmentNumber}, jaw {jaws[idx]}****\n'
            else:
                print('debug')
                for idx, j in enumerate(list(b.InitialJawPositions)):
                    print(j)
                    if np.abs(j)>19.9:
                        out += f'****Jaw position > 19.9 for beam {b.Name}, jaw {jaws[idx]}****\n'
        if out:
            self.specificBeamSetCheckResults += out
                    