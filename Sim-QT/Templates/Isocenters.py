try:
    from connect import *
except:
    pass


sys.path.append("\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")


from Sim.Templates.SimTemplate import SimTemplate
from RSutil.functions import interpretCTSimOrientation


class Isocenters(SimTemplate):
    
    
    """"Makes a plan with N isocenters/beamSets. N can also equal 1"""
    def __init__(self, numberOfIsocenters, planName, beamSetName):
        
        self.numberOfIsocenters = numberOfIsocenters
        
        self.colors = ["255, 255, 128", "128, 230, 255", "255, 128, 253", "255, 156, 128", "128, 255, 128"]
        
        super().__init__(planName, beamSetName)
        self.addBeamsToBeamSet()
           
    
    def addBeamsToBeamSet(self, beamNames = [], gantry = 0, collimator = 0):
        
        for idx in range(self.numberOfIsocenters):
            if len(beamNames) == 0:
                bName = str(idx + 1) + ' g' + str(gantry)
            else:
                bName = beamNames[idx]
            
            try: 
                isoColor = self.colors[idx]
            except:
                isoColor = self.colors[0]
            
            beam = self.beamSet.CreatePhotonBeam(BeamQualityId='6',  IsocenterData={ 'Position': { 'x': 0, 'y': 0, 'z': 0 }, 'NameOfIsocenterToRef': bName + ' ISO', 'Name': bName + ' ISO', 'Color': isoColor }, 
                                          Name = bName, GantryAngle = gantry, CollimatorAngle = collimator)
            beam.SetInitialJawPositions(X1=-5, X2 = 5, Y1 = -5, Y2 = 5)
            
        
if __name__ == "__main__":
    tmp = Isocenters(2, "test", "test")

        
        