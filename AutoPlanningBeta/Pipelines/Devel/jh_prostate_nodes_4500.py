
#'F:\\SHARING\\Radiation Oncology Physics\\RaystationScriptingPROD\\AutoPlanningBeta\\Pipelines\\Devel'

import sys
sys.path.append("\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
sys.path.append("F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")



from connect import *


from Planning.Structures.Functions.croppingShortcuts import *

from AutoPlanningBeta.Pipelines.Pipeline import Pipeline

from RSutil.CommonLibrary.Classes.RsNavigator import RsNavigator



class JH_Prostate_Nodes_4500(Pipeline):
    
    _REQUISITE_CONTOURS = ["MDGTV", "LtNode", "RtNode"]
    
    _PARAMS = {**Pipeline._PARAMS,
               'PROTOCOL_NAME': "JH_ProstLN_180x25",
              'NUM_BEAMSETS': 1,
              'PLAN_NAME': 'ProstLN4500',
              'BEAM_SET_NAMES': ['ProstLN4500'],
              'BEAM_TEMPLATE': 'SCRIPT TEMPLATE: 3 ARC FULL',
              'STRUCTURE_TEMPLATE': {'Name': "PLAN TEMPLATE: JH ProstLN 4500", 
                                     'Structures': ["PTV4500", "Bladder", "Rectum", "Lt Femoral", "Rt Femoral", "PTVn", "PTVp", "Bowel", "Bladder - GTVp", "Spacer", 
                                                    "zXRectum", "zXBladder", "zXBowel", "zZRectum", "zZBladder", "zZBowel", "Shell1", "zNTO", "zRectum50"]},
              'TARGET': ["PTV4500"],
              'TOTAL_DOSE': [4500],
              'PERCENT_VOL':[95],
              'FRACTIONS': [25],  
              'CLINICAL_GOAL_TEMPLATE': "JH IMRT Pelvis PRF",
              'OPTIMIZATION_TEMPLATE': "SCRIPT TEMPLATE: JH PROSTATE LN TB"
              }
    
    def __init__(self):
        super().__init__()
        
        self.contouring_workspace()
        self.plan_generation()
        self.optimization_workspace()
        
    def contouring_workspace(self):
        super().contouring_workspace()
        crop_spacer_from_rectum()
        await_user_input('''Review ROIs before proceeding!\n 
                         Proposed ROI steps are: \n .
                         1. Manually correct Bowel\n 
                         2.Check rectum/spacer overlap. \n 
                         3. Make Rectum 50: which is meant to be a posterior section of rectum to control 50% IDL \n
                         4. Fix couch contour. \n\n 
                         Script will automatically update all derived ROIs when you continue.''')
                         
        del self.ss
        
    def optimization_workspace(self):
        super().optimization_workspace()
        self.optimizer.runOptimization()
        
    
        




def main():
    
    a = JH_Prostate_Nodes_4500()


if __name__ == '__main__':
    main()
    
    
    
