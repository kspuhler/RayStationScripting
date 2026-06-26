import sys
sys.path.append("\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
sys.path.append("F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")

from AutoPlanningBeta.Classes.Optimizer.OptimizerBase import OptimizerBase

class TrueBeamOptimizer(OptimizerBase):
    
    _defaults = {**OptimizerBase._defaults,
                 "gantrySpacing": 2.0
                 }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        
    
    def setOptimizationParameters(self):
        super().setOptimizationParameters()
        #Makes the VMAT gantry sampling = 2.0deg
        for idx, b in enumerate(self.bs.Beams):
            try:
                self.plan.PlanOptimizations[0].OptimizationParameters.TreatmentSetupSettings[0].BeamSettings[idx].ArcConversionPropertiesPerBeam.EditArcBasedBeamOptimizationSettings(CreateDualArcs=False, 
                                                                                                                                                                                  FinalGantrySpacing=self.gantrySpacing, 
                                                                                                                                                                                  MaxArcDeliveryTime=90, 
                                                                                                                                                                                  BurstGantrySpacing=None, 
                                                                                                                                                                                  MaxArcMU=None)
            except:
                pass
        return
        
#testing

class RadixactOptimizer(OptimizerBase):
    
    _defaults = {}
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
    def setOptimizationParameters(self):
        super().setOptimizationParameters()
        pass
    
class CyberknifeOptimizer(OptimizerBase):
    
    _defaults = {**OptimizerBase._defaults,
                 "maxIterations": 250,
                 "prepPhaseIterations": 100,
                 "maxNodes": 60,
                 "maxSegments": 90,
                 "maxDirections": 90,
                 "muPenalty": 10,
                 "maxSegmentMu": 500}
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def setOptimizationParameters(self):
        super().setOptimizationParameters()
        for idx, b in enumerate(self.bs.Beams):
            try:
                self.plan.PlanOptimizations[0].OptimizationParameters.TreatmentSetupSettings[0].BeamSettings[0].CyberKnifePropertiesPerBeam.EditCyberKnifeBeamOptimizationSettings(MaxNumberOfNodes=self.maxNodes, 
                                                                                                                                                                               MaxNumberOfSegments=self.maxSegments,
                                                                                                                                                                               MaxNumberOfBeamDirections=self.maxDirections,
                                                                                                                                                                               NumberOfCandidateBeamDirections = 1000,
                                                                                                                                                                               MuReductionWeight=self.muPenalty,
                                                                                                                                                                               MaxTotalMu = None,
                                                                                                                                                                               MaxSegmentMu=self.maxSegmentMu)
            except:
                pass

if __name__=="__main__":
    a = TrueBeamOptimizer(clinicalGoalTemplate="KS Script CG Load Test", optimizationTemplate = "KS Script Opt Load Test")