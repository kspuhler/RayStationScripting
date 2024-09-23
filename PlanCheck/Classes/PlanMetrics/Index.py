from PlanMetricBaseClass import PlanMetricBaseClass



class IndexBaseClass(PlanMetricBaseClass):
#This is just a base class for GI/CI 
    def __init__(self):
        super.__init__()

    def calculate(target=None, isodoseLevel=None):
        pass
        ##TODO implement target.Size/isodoseLevel.Size

    
class GradientIndex(IndexBaseClass):
    def __init__(self):
        super().__init__() ##TODO calc with 50%IDL

class ConformalityIndex(IndexBaseClass):
    def __init__(self):
        super().__init__() ##TODO calc with 100%IDL

    
