#Make optimization structures for EBRT prostate and nodes

try:
    from connect import *
except:
    pass

import tkinter as tk
import sys
sys.path.append("\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
sys.path.append("F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")

from RSutil.variables import OPT_STRUCTURE_COLOR

from Launcher.ScriptObject import ScriptObject 
from Planning.Structures.Functions.checkForContour import checkForContour


class MakeProstateNodesOars(ScriptObject):
    
    def __init__(self, verboseExecution=False, runPreChecks=True, inferPhysician=False):
        super().__init__(verboseExecution, runPreChecks, inferPhysician)
        self.makeIntersections()
        self.makeSubtractions()
        self.makeMiscOptStructures()
        self.makeShells()
        
        
    def preChecks(self):
        #opt structures we will make
        try:
            self.pm.CreateRoi(Name="ADD_COUCH!",Color="White", Type="Support")
        except:
            pass
        for ii in ["Rectum", "Bladder-GTVp", "PTV4500", "BowelBag"]:
            if not checkForContour(ii):
                raise Exception(f"Plan is missing a structure {ii}!")
                
           
    def makeIntersections(self):
        for ii in ["zXRectum", "zXBladder", "zXBowelBag"]:
            crop = ii[2:] #Get for example just Rectum from zXRectum
            if not checkForContour(ii):
                self.pm.CreateRoi(Name=ii, Color=OPT_STRUCTURE_COLOR, Type="Control")
        
            self.pm.RegionsOfInterest[ii].SetAlgebraExpression(ExpressionA={ 'Operation': "Union", 'SourceRoiNames': ["PTV4500"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, 
                                                                                                           ExpressionB={ 'Operation': "Union", 'SourceRoiNames': [crop], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, 
                                                                                                           ResultOperation="Intersection", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })
            self.pm.RegionsOfInterest[ii].UpdateDerivedGeometry(Examination=self.exam, Algorithm="Auto")
            
    def makeSubtractions(self):
        for ii in ["zZRectum", "zZBladder", "zZBowelBag"]:
            crop = ii[2:] #Get for example just Rectum from zXRectum
            if not checkForContour(ii):
                self.pm.CreateRoi(Name=ii, Color=OPT_STRUCTURE_COLOR, Type="Control")
        
            self.pm.RegionsOfInterest[ii].SetAlgebraExpression(ExpressionA={ 'Operation': "Union", 'SourceRoiNames': [crop], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, 
                                                                                                           ExpressionB={ 'Operation': "Union", 'SourceRoiNames': ["PTV4500"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0.3, 'Inferior': 0.3, 'Anterior': 0.3, 'Posterior': 0.3, 'Right': 0.3, 'Left': 0.3 } }, 
                                                                                                           ResultOperation="Subtraction", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })
            self.pm.RegionsOfInterest[ii].UpdateDerivedGeometry(Examination=self.exam, Algorithm="Auto")
        
    def makeMiscOptStructures(self):
        if not checkForContour("zOptRectum"):
            self.pm.CreateRoi(Name="zOptRectum", Color=OPT_STRUCTURE_COLOR, Type="Control")
        self.pm.RegionsOfInterest["zOptRectum"].SetAlgebraExpression(ExpressionA={ 'Operation': "Union", 'SourceRoiNames': ["zZRectum"], 'MarginSettings': { 'Type': "Contract", 'Superior': 0, 'Inferior': 0, 'Anterior': 1, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, 
                                                                     ExpressionB={ 'Operation': "Union", 'SourceRoiNames': ["MDGTV"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 8, 'Right': 0, 'Left': 0 } }, 
                                                                     ResultOperation="Intersection", ResultMarginSettings={ 'Type': "Contract", 'Superior': 3, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })

        self.pm.RegionsOfInterest["zOptRectum"].UpdateDerivedGeometry(Examination=self.exam, Algorithm="Auto")

            
            
    def makeShells(self):
        for ii in ["Shell1", "Shell2", "Shell3"]:
            if not checkForContour(ii):
                self.pm.CreateRoi(Name=ii, Color="Lime", Type="Control")
        self.pm.RegionsOfInterest["Shell1"].SetAlgebraExpression(ExpressionA={ 'Operation': "Union", 'SourceRoiNames': ["PTV4500"], 'MarginSettings': { 'Type': "Expand", 'Superior': 1.5, 'Inferior': 1.5, 'Anterior': 1.5, 'Posterior': 1.5, 'Right': 1.5, 'Left': 1.5} }, 
                                                                     ExpressionB={ 'Operation': "Union", 'SourceRoiNames': ["PTV4500"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0.1, 'Inferior': 0.1, 'Anterior': 0.1, 'Posterior': 0.1, 'Right': 0.1, 'Left': 0.1} }, 
                                                                     ResultOperation="Subtraction", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })
        
        
        self.pm.RegionsOfInterest["Shell2"].SetAlgebraExpression(ExpressionA={ 'Operation': "Union", 'SourceRoiNames': ["PTV4500"], 'MarginSettings': { 'Type': "Expand", 'Superior': 4.4, 'Inferior': 4.4, 'Anterior': 4.4, 'Posterior': 4.4, 'Right': 4.4, 'Left': 4.4} }, 
                                                                     ExpressionB={ 'Operation': "Union", 'SourceRoiNames': ["PTV4500"], 'MarginSettings': { 'Type': "Expand", 'Superior': 1.5, 'Inferior': 1.5, 'Anterior': 1.5, 'Posterior': 1.5, 'Right': 1.5, 'Left': 1.5} }, 
                                                                     ResultOperation="Subtraction", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })
        
        self.pm.RegionsOfInterest["Shell3"].SetAlgebraExpression(ExpressionA={ 'Operation': "Union", 'SourceRoiNames': ["PTV4500"], 'MarginSettings': { 'Type': "Expand", 'Superior': 5.5, 'Inferior': 5.5, 'Anterior': 5.5, 'Posterior': 5.5, 'Right': 5.5, 'Left': 5.5} }, 
                                                                     ExpressionB={ 'Operation': "Union", 'SourceRoiNames': ["PTV4500"], 'MarginSettings': { 'Type': "Expand", 'Superior': 4.5, 'Inferior': 4.5, 'Anterior': 4.5, 'Posterior': 4.5, 'Right': 4.5, 'Left': 4.5} }, 
                                                                     ResultOperation="Subtraction", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })
        
        self.pm.RegionsOfInterest["Shell1"].UpdateDerivedGeometry(Examination=self.exam, Algorithm="Auto")
        self.pm.RegionsOfInterest["Shell2"].UpdateDerivedGeometry(Examination=self.exam, Algorithm="Auto")
        self.pm.RegionsOfInterest["Shell3"].UpdateDerivedGeometry(Examination=self.exam, Algorithm="Auto")
        
if __name__ == "__main__":
    tmp = MakeProstateNodesOars()
        