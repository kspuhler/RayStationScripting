try:
    from connect import *
except:
    pass


sys.path.append("\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")


from Sim.Templates.SimTemplate import SimTemplate
from Sim.Templates.Isocenters import Isocenters



class OpposedLats(Isocenters):
    
    def __init__(self, numberOfIsocenters, planName, beamSetName):
        super().__init__(numberOfIsocenters, planName, beamSetName)
        
    
    def addBeamsToBeamSet(self, beamNames = [], gantry = 90, collimator = 0):
        super().addBeamsToBeamSet(beamNames, gantry, collimator)

if __name__ == "__main__":
    tmp = OpposedLats(2, "test", "test")