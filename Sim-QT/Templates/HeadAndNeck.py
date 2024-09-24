
try:
    from connect import *
except:
    pass

import sys

sys.path.append("\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
sys.path.append("F:\SHARING\Radiation Oncology Physics\RaystationScripting\Planning\Structures\Templates")


from Sim.Templates.Isocenters import Isocenters
from RSutil.functions import interpretCTSimOrientation
from Planning.Structures.Templates.StructureTemplate import StructureTemplate
from Planning.Structures.Templates.roi_list_templates import haasHeadAndNeck

class HeadAndNeck(Isocenters):
    
    def __init__(self, numberOfIsocenters, planName, beamSetName, structureTemplate):
        
        self.numberOfIsocenters = numberOfIsocenters
        
        super().__init__(numberOfIsocenters, planName, beamSetName)
    
    
    def addStructures(self, case, examination):
        structures = StructureTemplate(haasHeadAndNeck, self.case.PatientModel)
        structures.make_empty_rois()

                                                                                                                                                                  
    def addBeamsToBeamSet(self, beamNames = [], gantry = 0, collimator = 0):
        
                                    
            beam = self.beamSet.CreatePhotonBeam(BeamQualityId='6',  IsocenterData={ 'Position': { 'x': 0, 'y': 0, 'z': 0 }, 'NameOfIsocenterToRef': 'HN ISO', 'Name': 'HN ISO', 'Color': "255, 255, 128" }, 
                                          Name = '1 g0', GantryAngle = gantry, CollimatorAngle = collimator)
            
            beam.SetInitialJawPositions(X1=-5, X2 = 5, Y1 = -5, Y2 = 5)
            
        
if __name__ == "__main__":
    tmp = Pelvis(1, "Haastest", "Haastest")
    
    