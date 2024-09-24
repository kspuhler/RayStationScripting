from connect import *

import sys
import tkinter as tk

sys.path.append("\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
sys.path.append("F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")

from Planning.Structures.Classes.MakePTVProstateCK import MakePTVProstateCK
from Planning.Structures.Functions.checkForContour import checkForContour
from Planning.Structures.Functions.makeRing import makeRing
from RSutil.variables import OPT_STRUCTURE_COLOR
from FrontEnd.DropdownMenuWindow import DropdownMenuWindow
from Launcher.ScriptObject import ScriptObject


class CKProstatePrePlanContouring(ScriptObject):
    
    '''
        This script will create a standard set of prostate CK contours for you. It will ask you at one point whether or not the fiducial check passed. 
        It will also pop up some info about making the PTV. Please look out for windows popping up, sometimes they are hidden in the background. Look on your Windows toolbar at bottom.
        
        This is what this script will do:
            
            1. It will crop the GTV from the Bladder.
            2. It will ask you if the fiducials passed. It will create the PTV based on your answer. Yes = Expanded Margin; No = Standard Margin
            3. It will crop the rectum to 1cm sup/inf from the PTV
            4. It will make rectum/bladder opt structures 5mm from PTV to control hotspots
            5. It will make 3 shells for you to use in optimizer.
    '''
    
    def __init__(self, verboseExecution=True, runPreChecks=True):
        
        super().__init__(verboseExecution=verboseExecution, runPreChecks=runPreChecks)
        
        tmp = MakePTVProstateCK(gtvName=self.gtvName)
        print('PTV done')
        del(tmp)
        
        self.cropBladder()
        self.cropRectum()
        self.makeBladderOpt()
        self.makeRectumOpt()
        
        #make shells
        #Shells

        for cm in  [0.2, 2, 8]:
            makeRing(cm, 'PTV_CK')


    
    def preChecks(self):
        #Check for ROI named mdgtv
        for name in ['mdgtv', 'MDGTV', 'mdGTV']:
            if checkForContour(name, caseSensitive = True):
                self.gtvName = name
        #Let user select GTV target if it cannot be found in contoured ROIs
        try:
            self.gtvName
        except AttributeError: 
                
            root = tk.Tk()
            root.withdraw()  # Hide the root window
                
            w = DropdownMenuWindow(root, [roi.OfRoi.Name for roi in self.pm.StructureSets[self.exam.Name].RoiGeometries], allow_multiple=False)
            w.grab_set()  # Make sure the dropdown window grabs focus
            root.wait_window(w)  # Wait for the dropdown window to close
            self.gtvName = w.get_selected_items()
            #TODO contour bladder and rectum using DL models if it they do not exist.
            
    def cropBladder(self): #Bladder-GTV
        self.pm.RegionsOfInterest['Bladder'].CreateAlgebraGeometry(Examination=self.exam, Algorithm="Auto", ExpressionA={ 'Operation': "Union", 'SourceRoiNames': ["Bladder"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, 
                                                                   ExpressionB={ 'Operation': "Union", 'SourceRoiNames': [self.gtvName], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ResultOperation="Subtraction", 
                                                                   ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })
        
    def cropRectum(self): #Rectum - (gtv + spacer)
        crop = [self.gtvName]
        if checkForContour("Spacer", caseSensitive=True):
            crop.append("Spacer")
        #Crop from gtv and Spacer
        self.pm.RegionsOfInterest['Rectum'].CreateAlgebraGeometry(Examination=self.exam, Algorithm="Auto", ExpressionA={ 'Operation': "Union", 'SourceRoiNames': ["Rectum"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, 
                                                                    ExpressionB={ 'Operation': "Union", 'SourceRoiNames': crop, 'MarginSettings': { 'Type': "Expand", 'Superior': 0.1, 'Inferior': 0.1, 'Anterior': 0.1, 'Posterior': 0.1, 'Right': 0.1, 'Left': 0.1 } }, 
                                                                    ResultOperation="Subtraction", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })
        #Crop 1cm info/sup
        self.pm.RegionsOfInterest['Rectum'].CreateAlgebraGeometry(Examination=self.exam, Algorithm="Auto", ExpressionA={ 'Operation': "Union", 'SourceRoiNames': ["Rectum"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, 
                                                                    ExpressionB={ 'Operation': "Union", 'SourceRoiNames': ["PTV_CK"], 'MarginSettings': { 'Type': "Expand", 'Superior': 1, 'Inferior': 1, 'Anterior': 9, 'Posterior': 9, 'Right': 9, 'Left': 9 } }, ResultOperation="Intersection", 
                                                                    ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })
        
    def makeBladderOpt(self):
        if checkForContour('zoptbladder'):
            self.pm.RegionsOfInterest['zOptBladder'].DeleteRoi()
        zBladder = self.pm.CreateRoi(Name="zOptBladder", Color=OPT_STRUCTURE_COLOR, Type="Organ", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)
        zBladder.SetAlgebraExpression(ExpressionA={ 'Operation': "Union", 'SourceRoiNames': ["PTV_CK"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0.5, 'Inferior': 0.5, 'Anterior': 0.5, 'Posterior': 0.5, 'Right': 0.5, 'Left': 0.5 } }, 
                                      ExpressionB={ 'Operation': "Union", 'SourceRoiNames': ["Bladder"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } },
                                      ResultOperation="Intersection", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })
        zBladder.UpdateDerivedGeometry(Examination=self.exam, Algorithm="Auto")
        
    def makeRectumOpt(self):
        if checkForContour('zoptrectum'):
            self.pm.RegionsOfInterest['zOptRectum'].DeleteRoi()
        zRectum = self.pm.CreateRoi(Name="zOptRectum", Color=OPT_STRUCTURE_COLOR, Type="Organ", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)
        zRectum.SetAlgebraExpression(ExpressionA={ 'Operation': "Union", 'SourceRoiNames': ["PTV_CK"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0.5, 'Inferior': 0.5, 'Anterior': 0.5, 'Posterior': 0.5, 'Right': 0.5, 'Left': 0.5 } }, 
                                      ExpressionB={ 'Operation': "Union", 'SourceRoiNames': ["Rectum"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } },
                                      ResultOperation="Intersection", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })
        zRectum.UpdateDerivedGeometry(Examination=self.exam, Algorithm="Auto")

                
        
if __name__ == "__main__":
    tmp = CKProstatePrePlanContouring()
        












