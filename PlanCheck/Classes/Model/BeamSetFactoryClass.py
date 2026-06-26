#Creates beamset-specific checker for CK/21/TB/Radx
#Author: KDS

#Receives beamset from PlanCheckModel()

import sys
sys.path.append("F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
sys.path.append("\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")

from RSutil.variables import CYBERKNIFES, RADIXACTS, EX, TRUEBEAMS
from PlanCheck.Classes.Model.CKBeamSetCheckModel import CKBeamSetCheckModel
from PlanCheck.Classes.Model.RadixactBeamSetCheckModel import RadixactBeamSetCheckModel
from PlanCheck.Classes.Model.EXBeamBeamSetCheckModel import EXBeamSetCheckModel
from PlanCheck.Classes.Model.TrueBeamBeamSetCheckModel import TrueBeamBeamSetCheckModel

from connect import *

class BeamSetFactoryClass(object):
    @staticmethod
    def createBeamSet(beamSet):
        machine = beamSet.MachineReference['MachineName']
        
        if machine in CYBERKNIFES:
            return CKBeamSetCheckModel(beamSet)
        elif machine in RADIXACTS:
            return RadixactBeamSetCheckModel(beamSet)
        elif machine in EX:
            return EXBeamSetCheckModel(beamSet)
        elif machine in TRUEBEAMS:
            return TrueBeamBeamSetCheckModel(beamSet)
        else:
            raise ValueError(f"Cannot ascertain machine for {beamSet.DicomPlanLabel}")
    
    