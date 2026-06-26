

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
        3. Verify PTVs: PTVp, PTVN, PTV4500.
    
    '''
      
    def __init__(self,getMarginFromUser = True, margins = {'ProstateMargin': None, 'NodeMargin': None}, templates = ProstateNodesTemplates):
        self.getMarginFromUser = getMarginFromUser
        self.margins = margins
        self.templates = templates
        super().__init__(getMarginFromUser, margins, templates)


    def preChecks(self):
        
        if self.getMarginFromUser:
            self.openMarginWindow()
        

     
        for ii in ["MDGTV","CTV prostate", "CTVprostate"]:
            if checkForContour(ii, caseSensitive=False):
                self.prostate = ii
                print(f"Making prostate expansion from {self.prostate}")
        if checkForContour("LtNode") and checkForContour("RtNode"):
            #^We have contoured Lt and Rt node on this scan, otherwise we skip to avoid deleting Todd's CTV node
            try:
                self.pm.CreateRoi(Name="CTV nodes", Color="Cyan", Type="ctv", TissueName="", RbeCellTypeName=None, RoiMaterial=None)
            except:
                pass
            
            self.pm.RegionsOfInterest["CTV nodes"].SetAlgebraExpression(ExpressionA={ 'Operation': "Union", 'SourceRoiNames': ["LtNode", "RtNode"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 }}, 
                                                                     ExpressionB={ 'Operation': "Union", 'SourceRoiNames': [], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, 
                                                                     ResultOperation="None", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })
        
        elif checkForContour("CTV nodes"): #Todd did this one so we are going to try to delete Lt Node, Rt Node and set CTV nodes equal to itself to remove ROI derived status 
            self.pm.RegionsOfInterest['CTV nodes'].CreateAlgebraGeometry(Examination=self.exam, Algorithm="Auto", ExpressionA={ 'Operation': "Union", 'SourceRoiNames': ["CTV nodes"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, 
                                                                         ExpressionB={ 'Operation': "Union", 'SourceRoiNames': [], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, 
                                                                         ResultOperation="None", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })
        
    
    def makePtv(self):

        for ii in ["PTVp", "PTVn", "PTV4500"]: #Make PTV ROIs that do not exist
            if not checkForContour(ii, caseSensitive=True):
                self.pm.CreateRoi(Name=ii, Color="Pink", Type="ptv", TissueName="", RbeCellTypeName=None, RoiMaterial=None)
         
        print(self.margins.get('ProstateMargin', {}))
        self.pm.RegionsOfInterest['PTV4500'].Color = "Red"
        self.pm.RegionsOfInterest['PTVp'].SetAlgebraExpression(ExpressionA={ 'Operation': "Union", 'SourceRoiNames': [self.prostate], 'MarginSettings': self.formattedMargins.get('ProstateMargin', {})}, 
                                                                 ExpressionB={ 'Operation': "Union", 'SourceRoiNames': [], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, 
                                                                 ResultOperation="None", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })
        print('ccc')
        self.pm.RegionsOfInterest['PTVn'].SetAlgebraExpression(ExpressionA={ 'Operation': "Union", 'SourceRoiNames': ["CTV nodes"], 'MarginSettings': self.formattedMargins.get('NodeMargin', {})}, 
                                                                 ExpressionB={ 'Operation': "Union", 'SourceRoiNames': [], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, 
                                                                 ResultOperation="None", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })
        
        
        self.pm.RegionsOfInterest['PTV4500'].SetAlgebraExpression(ExpressionA={ 'Operation': "Union", 'SourceRoiNames': ["PTVp", "PTVn"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, 
                                                                 ExpressionB={ 'Operation': "Union", 'SourceRoiNames': [], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, 
                                                                 ResultOperation="None", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })

        self.pm.UpdateDerivedGeometries(RoiNames=["PTVp", "PTVn", "PTV4500"], Examination=self.exam, Algorithm="Auto", AreEmptyDependenciesAllowed=False)
        
if __name__ == "__main__":
    MakePTVProstateEBRT()
