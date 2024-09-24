try:
    from connect import *
except:
    pass

import tkinter as tk
import sys
sys.path.append("\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
sys.path.append("F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")

from Planning.Structures.Classes.MakePTV import MakePTV
from Planning.Structures.Functions.checkForContour import checkForContour
from Planning.Structures.Functions.fiducialAutoContour import fiducialAutoContour
from Planning.Structures.Templates.TemplatesForPTVMargins.ProstateNodesEBRT import ProstateNodesTemplates
from FrontEnd.GenericPopup import GenericPopup
from FrontEnd.CheckWithUserWindow import CheckWithUserWindowBoolean
from FrontEnd.DropdownMenuWindow import DropdownMenuWindow


class MakePTVProstateEBRT(MakePTV):
    
    '''
    This script will make the PTVs associated with a normal prostate and nodes EBRT plan.
    
    The script can handle the default margins on JH and TC PRFs automatically.    
    
    To run:
        1. Make sure there are contours: MDGTV, LtNode, RtNode.
        2. Run script.
        3. Verify PTVs: PTVp, PTV_ltv, PTV_rtn, PTV4500.
    
    '''
      
    def __init__(self,getMarginFromUser = True, margins = {'ProstateMargin': None, 'NodeMargin': None}, templates = ProstateNodesTemplates):
        self.getMarginFromUser = getMarginFromUser
        self.margins = margins
        self.templates = templates
        super().__init__(getMarginFromUser, margins, templates)


    def preChecks(self):
        for ii in ["MDGTV", "LtNode", "RtNode"]:
            if not checkForContour(ii, caseSensitive=False):
                raise(Exception(f"Roi:{ii} not found!"))
                return
        super().preChecks()
        
    
    def makePtv(self):

        for ii in ["PTVp", "PTV_ltn", "PTV_rtn", "PTV4500"]: #Make PTV ROIs that do not exist
            if not checkForContour(ii, caseSensitive=True):
                self.pm.CreateRoi(Name=ii, Color="Pink", Type="ptv", TissueName="", RbeCellTypeName=None, RoiMaterial=None)
         
        print(self.margins.get('ProstateMargin', {}))
        self.pm.RegionsOfInterest['PTV4500'].Color = "Red"
        self.pm.RegionsOfInterest['PTVp'].SetAlgebraExpression(ExpressionA={ 'Operation': "Union", 'SourceRoiNames': ["MDGTV"], 'MarginSettings': self.formattedMargins.get('ProstateMargin', {})}, 
                                                                 ExpressionB={ 'Operation': "Union", 'SourceRoiNames': [], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, 
                                                                 ResultOperation="None", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })
        print('ccc')
        self.pm.RegionsOfInterest['PTV_ltn'].SetAlgebraExpression(ExpressionA={ 'Operation': "Union", 'SourceRoiNames': ["LtNode"], 'MarginSettings': self.formattedMargins.get('NodeMargin', {})}, 
                                                                 ExpressionB={ 'Operation': "Union", 'SourceRoiNames': [], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, 
                                                                 ResultOperation="None", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })
        
        self.pm.RegionsOfInterest['PTV_rtn'].SetAlgebraExpression(ExpressionA={ 'Operation': "Union", 'SourceRoiNames': ["RtNode"], 'MarginSettings': self.formattedMargins.get('NodeMargin', {})},                                                              
                                                                 ExpressionB={ 'Operation': "Union", 'SourceRoiNames': [], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, 
                                                                 ResultOperation="None", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })
        
        self.pm.RegionsOfInterest['PTV4500'].SetAlgebraExpression(ExpressionA={ 'Operation': "Union", 'SourceRoiNames': ["PTVp", "PTV_ltn", "PTV_rtn"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, 
                                                                 ExpressionB={ 'Operation': "Union", 'SourceRoiNames': [], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, 
                                                                 ResultOperation="None", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })

        self.pm.UpdateDerivedGeometries(RoiNames=["PTVp", "PTV_ltn", "PTV_rtn", "PTV4500"], Examination=self.exam, Algorithm="Auto", AreEmptyDependenciesAllowed=False)
        
if __name__ == "__main__":
    MakePTVProstateEBRT()
