from connect import *

import tkinter as tk
import sys
sys.path.append("\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
sys.path.append("F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")

from Planning.Structures.Classes.MakePTV import MakePTV
from Planning.Structures.Functions.checkForContour import checkForContour
from Planning.Structures.Templates.TemplatesForPTVMargins.ProstateCKMargins import ProstateCKMargins
from FrontEnd.GenericPopup import GenericPopup
from FrontEnd.CheckWithUserWindow import CheckWithUserWindowBoolean
from FrontEnd.DropdownMenuWindow import DropdownMenuWindow




class MakePTVProstateCK(MakePTV):
    
    '''
    Makes a PTV for the prostate CK plans. 
    
    To run:
        
        1. Run the fiducial check script.
        2. Make sure there is a structure called MDGTV, this is what will be expanded. 
        3. Create a PTV based on whether or not you want expanded margins.
        4. Verify your PTV. 
    
    '''
    
    
    def __init__(self, gtvName = 'MDGTV', fiducialBool = None, getMarginFromUser = True, margins = {'ProstateMargin': None}, templates = ProstateCKMargins):
        
        self.gtvName = gtvName
        self.fiducialBool = fiducialBool
        self.getMarginFromUser = getMarginFromUser
        self.margins = margins
        self.templates = templates
        super().__init__(getMarginFromUser, margins, templates)
        

        
    def preChecks(self):
        
        if not checkForContour(self.gtvName, caseSensitive=False):
            raise(Exception(f"Roi:{ii} not found!"))
        
        super().preChecks()
            
        
    def makePtv(self):
        try:   
            self.pm.CreateRoi(Name="PTV_CK", Color="Red", Type="Ptv", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)
        except:
            pass
        self.pm.RegionsOfInterest['PTV_CK'].SetAlgebraExpression(ExpressionA={ 'Operation': "Union", 'SourceRoiNames': [self.gtvName], 'MarginSettings': self.formattedMargins.get('ProstateMargin', {}) }, 
                                                                 ExpressionB={ 'Operation': "Union", 'SourceRoiNames': [], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, 
                                                                 ResultOperation="None", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })
        
        self.pm.UpdateDerivedGeometries(RoiNames=["PTV_CK"], Examination=self.exam, Algorithm="Auto", AreEmptyDependenciesAllowed=False)


    
if __name__ == "__main__":
    tmp = MakePTVProstateCK()