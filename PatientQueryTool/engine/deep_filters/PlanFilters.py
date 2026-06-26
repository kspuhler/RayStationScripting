import sys

sys.path.append(r"\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
sys.path.append(r"F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")

from PatientQueryTool.engine.deep_filters.base import DeepFilterBase



class HasPlanNameFilter(DeepFilterBase):
    
    def __init__(self, plan_name, approval = True):
        if not isinstance(plan_name, list):
            plan_name = [plan_name]
        
        self.plan_name = plan_name
        self.approval = approval
        
    def is_match(self, ray_repository, patient, patient_info_record):
        
        for case in patient.Cases:
            for plan in case.TreatmentPlans:
                if plan.Name not in self.plan_name:
                    continue
                
                if self.approval:
                    try:
                        if plan.Review.ApprovalStatus == "Approved":
                            print('appproved')
                            return True
                    except:
                        continue            
        return False
    
class HasPlanWithFractionationFilter(DeepFilterBase):
    
    def __init__(self, fractions=None, dose_per_fraction=None):
        pass

class HasPlanOnMachineFilter(DeepFilterBase):
    def __init__(self, machine_name):
        pass
    
class HasPlanTechniqueFilter(DeepFilterBase):
    def __init__(self, technique):
        pass