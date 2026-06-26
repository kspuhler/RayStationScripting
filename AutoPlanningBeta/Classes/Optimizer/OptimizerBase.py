import sys
sys.path.append("\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
sys.path.append("F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")

from AutoPlanningBeta.Functions.structure_alias import user_prompt_for_missing_structures


try:
    from connect import *
except:
    pass

class OptimizerBase(object):
    
    #default parameters that can be replaced in kwargs
    _defaults = {"userPromptBeforeOpt": False,
                "autoRunOptimization": False,
                "autoRunReduceOarDose":False,
                "automaticFineTune": False,
                "clinicalGoalTemplate":None,
                "optimizationTemplate": None,
                "maxIterations": 80,
                "optimizationTolerance": 0,
                "prepPhaseIterations": 20 #number of iterations before intermediate dose
                }
    
    def __init__(self, *args, tk_root = None, **kwargs):
        
        #self.switchRsUi()
        
        self.plan = get_current("Plan")
        self.bs = get_current("BeamSet")
        case = get_current("Case")
        self.pm = case.PatientModel
        self.db = get_current("PatientDB")
        self.tk_root = tk_root

       # plan.PlanOptimizations[0].ApplyOptimizationTemplate(Template=db.TemplateTreatmentOptimizations['KS Script Opt Load Test'], AssociatedRoisAndPois={ 'External': "External" })

       # plan.TreatmentCourse.EvaluationSetup.ApplyClinicalGoalTemplate(Template=db.TemplateTreatmentOptimizations['KS Script CG Load Test'], AssociatedRoisAndPois={ 'External': "External" })

        #processing kwargs
        
        attributes = self._defaults.copy()
        attributes.update(kwargs)
        self._process_kwargs(attributes)
        
        self.setOptimizationParameters()

        
        
   # def getCorrectIndexForBeamSetOptimization(self):
   #     for idx, ii in self.plan.PlanOptimizations:
    
    def _process_kwargs(self, attributes):
        for key, value in attributes.items():
            if key in self._defaults:
                setattr(self, key, value)
            else:
                setattr(self, key, value)
                print(f"Warning: Unknown attribute '{key}'")
        return
    
    def loadOptimizationTemplate(self):
        
        #Load template name, prompt user for one if cannot find or load it
         if not self.optimizationTemplate:
             print(f"Need to hard code clinical goals for the time being")
             #TODO implement user specified
             pass
         else: #Load user specified template
             try:
                 optTemplate = self.db.LoadTemplateOptimizationFunctions(templateName = self.optimizationTemplate, lockMode = "Read")
                 print(f"Loaded opt template {self.optimizationTemplate}")
             except:
                 print(f"Debug 1: Failed to load OPTIMIZATION TEMPLATE: {self.optimizationTemplate}")
                
             try:
                 self.plan.PlanOptimizations[0].ApplyOptimizationTemplate(Template=optTemplate)
             except:
                 print(f"Debug 2: Failed to load OPTIMIZATION TEMPLATE: {self.optimizationTemplate}")    
         return
        
    
    def loadClinicalGoals(self, templateName=None):

         if not self.clinicalGoalTemplate:
             print(f"Need to hard code optimization goals for the time being")
             #TODO implement user specified
             pass
         else: #Load user specified template
             try:
                 cgTemplate = self.db.LoadTemplateClinicalGoals(templateName = self.clinicalGoalTemplate, lockMode = "Read")
                 alias = user_prompt_for_missing_structures(cgTemplate, structures=None, parent = self.tk_root)
                 print(f"Loaded cg template {self.clinicalGoalTemplate}")
             except:
                 print(f"Debug 1: Failed to load CLINICAL GOAL TEMPLATE: {self.clinicalGoalTemplate}")   
             try:
                 self.plan.TreatmentCourse.EvaluationSetup.ApplyClinicalGoalTemplate(Template=cgTemplate, AssociatedRoisAndPois= alias)
             except:
                 print(f"Debug 2: Failed to load CLINICAL GOAL TEMPLATE: {self.clinicalGoalTemplate}")    
         return

    def setOptimizationParameters(self):
        self.plan.PlanOptimizations[0].OptimizationParameters.Algorithm.MaxNumberOfIterations = self.maxIterations
        self.plan.PlanOptimizations[0].OptimizationParameters.Algorithm.OptimalityTolerance = self.optimizationTolerance
        self.plan.PlanOptimizations[0].OptimizationParameters.DoseCalculation.IterationsInPreparationsPhase = self.prepPhaseIterations
    
    def setProtectStructures(self):
        pass

    def checkClinicalGoals(self):
        #Determine which clinical goals fail and pass to the fine tune method
        pass
    
    def runOptimization(self):
        self.plan.PlanOptimizations[0].RunOptimization()
    
    def runFineTune(self):
        self.checkClinicalGoals()
        pass
    
    def switchRsUi(self):
        #move user view to contouring window
        ui = get_current("ui")      
        ui.TitleBar.Navigation.MenuItem["Optimization"].Button.Click()
    



#class RadixactOptimizer(Optimizer):
    
    
#UNIT TEST

if __name__=="__main__":
    a = OptimizerBase(clinicalGoalTemplate="KS Script CG Load Test", optimizationTemplate = "KS Script Opt Load Test")
    a.setOptimizationParameters()
    a.loadOptimizationTemplate()
    a.loadClinicalGoals()
    

