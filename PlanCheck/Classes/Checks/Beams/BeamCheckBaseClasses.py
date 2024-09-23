#Author KDS
#Basic 
from CheckerBaseClass import CheckerBaseClass


class BeamCheckBaseClass(CheckerBaseClass):

    
    #This is a base class from which more specific checks for TB/21, CK and Radixact beamsets will inherit 

    def __init__(self) -> None:
        super().__init__()  


    def getMU(self) -> float:
        pass #get MUs for beam

    def getRefDose(self) -> float:
        pass #get reference doses for beam

    
    def checkMU(self) -> None:
        pass



class CKBeamCheck(BeamCheckBaseClass):

    #Base class from CyberKnife beam checks

    def __init__(self) -> None:
        super().__init__()  

    #TODO talk to Owen and Matt about things to include

class RadixactBeamCheck(BeamCheckBaseClass):

    def __init__(self) -> None:
        super().__init__()
            



class VarianBeamCheck(BeamCheckBaseClass):

    #Base class for Varian beam checks

    def __init__(self) -> None:
        super().__init__()  

    def checkFieldName(self) -> bool:
        isGoodFieldName = False

        #TODO: Get field start and stop angles 

        return isGoodFieldName


