#Author KDS
#Base class for all checks to derive from

class CheckerBaseClass(object):

    TOLERANCE = None

    def __init__(self) -> None:
        #code
        pass

    def check(self, *args, **kwargs) -> bool:
        pass

    def getTolerance(self):
        pass

if __name__ == '__main__': #Test Builds of Classes
    from PlanCheck.Classes.Checks.Beams.BeamCheckBaseClasses import BeamCheckBaseClass  
    a = BeamCheckBaseClass()