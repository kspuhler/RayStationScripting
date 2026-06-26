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
        #self.makeMiscOptStructures()
        self.makeShells()
        
        
    def preChecks(self):
        #opt structures we will make
        try:
            self.pm.CreateRoi(Name="ADD_COUCH!",Color="White", Type="Support")
        except:
            pass
        for ii in ["Rectum", "Bladder", "PTV4500", "Bowel"]:
            if not checkForContour(ii):
                print(ii)

                print(f"Plan is missing a structure {ii}!")
                raise Exception(f"Plan is missing a structure {ii}!")
        if not checkForContour("Bladder-GTVp"):
            print("Blad-gtv")
            self.pm.CreateRoi(Name="Bladder-GTVp", Color="Yellow", Type="Organ")
            self.pm.RegionsOfInterest["Bladder-GTVp"].SetAlgebraExpression(ExpressionA={ 'Operation': "Union", 'SourceRoiNames': ['Bladder'], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, 
                                                                                                           ExpressionB={ 'Operation': "Union", 'SourceRoiNames': ["MDGTV"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0.0, 'Inferior': 0.0, 'Anterior': 0.0, 'Posterior': 0.0, 'Right': 0.0, 'Left': 0.0 } }, 
                                                                                                           ResultOperation="Subtraction", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })
                
           
    def makeIntersections(self):
        for ii in ["zXRectum", "zXBladder", "zXBowel"]:
            crop = ii[2:] #Get for example just Rectum from zXRectum
            if not checkForContour(ii):
                self.pm.CreateRoi(Name=ii, Color=OPT_STRUCTURE_COLOR, Type="Control")
        
            self.pm.RegionsOfInterest[ii].SetAlgebraExpression(ExpressionA={ 'Operation': "Union", 'SourceRoiNames': ["PTV4500"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, 
                                                                                                           ExpressionB={ 'Operation': "Union", 'SourceRoiNames': [crop], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, 
                                                                                                           ResultOperation="Intersection", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })
            self.pm.RegionsOfInterest[ii].UpdateDerivedGeometry(Examination=self.exam, Algorithm="Auto")
            
    def makeSubtractions(self):
        for ii in ["zZRectum", "zZBladder", "zZBowel"]:
            crop = ii[2:] #Get for example just Rectum from zXRectum
            if not checkForContour(ii):
                self.pm.CreateRoi(Name=ii, Color=OPT_STRUCTURE_COLOR, Type="Control")
        
            self.pm.RegionsOfInterest[ii].SetAlgebraExpression(ExpressionA={ 'Operation': "Union", 'SourceRoiNames': [crop], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, 
                                                                                                           ExpressionB={ 'Operation': "Union", 'SourceRoiNames': ["PTV4500"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0.3, 'Inferior': 0.3, 'Anterior': 0.3, 'Posterior': 0.3, 'Right': 0.3, 'Left': 0.3 } }, 
                                                                                                           ResultOperation="Subtraction", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })
            self.pm.RegionsOfInterest[ii].UpdateDerivedGeometry(Examination=self.exam, Algorithm="Auto")
        
    # def makeMiscOptStructures(self):
    #     if not checkForContour("zRectumGradient"):
    #         self.pm.CreateRoi(Name="zRectumGradient", Color=OPT_STRUCTURE_COLOR, Type="Control")
    #     self.pm.RegionsOfInterest["zRectumGradient"].SetAlgebraExpression(ExpressionA={ 'Operation': "Union", 'SourceRoiNames': ["zZRectum"], 'MarginSettings': { 'Type': "Contract", 'Superior': 0, 'Inferior': 0, 'Anterior': 1, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, 
    #                                                                  ExpressionB={ 'Operation': "Union", 'SourceRoiNames': ["MDGTV"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 8, 'Right': 0, 'Left': 0 } }, 
    #                                                                  ResultOperation="Intersection", ResultMarginSettings={ 'Type': "Contract", 'Superior': 3, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })

    #     self.pm.RegionsOfInterest["zRectumGradient"].UpdateDerivedGeometry(Examination=self.exam, Algorithm="Auto")
            
            
    def makeShells(self):
        for ii in ["Shell1", "zNTO"]:
            if not checkForContour(ii):
                self.pm.CreateRoi(Name=ii, Color="Lime", Type="Control")
        self.pm.RegionsOfInterest["Shell1"].SetAlgebraExpression(ExpressionA={ 'Operation': "Union", 'SourceRoiNames': ["PTV4500"], 'MarginSettings': { 'Type': "Expand", 'Superior': 1.2, 'Inferior': 1.2, 'Anterior': 1.2, 'Posterior': 1.2, 'Right': 1.2, 'Left': 1.2} }, 
                                                                     ExpressionB={ 'Operation': "Union", 'SourceRoiNames': ["PTV4500"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0.2, 'Inferior': 0.2, 'Anterior': 0.2, 'Posterior': 0.2, 'Right': 0.2, 'Left': 0.2} }, 
                                                                     ResultOperation="Subtraction", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })
        
        
        self.pm.RegionsOfInterest["zNTO"].SetAlgebraExpression(ExpressionA={ 'Operation': "Union", 'SourceRoiNames': ["PTV4500"], 'MarginSettings': { 'Type': "Expand", 'Superior': 5.5, 'Inferior': 5.5, 'Anterior': 5.5, 'Posterior': 5.5, 'Right': 5.5, 'Left': 5.5} }, 
                                                                     ExpressionB={ 'Operation': "Union", 'SourceRoiNames': ["PTV4500"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0.2, 'Inferior': 0.2, 'Anterior': 0.2, 'Posterior': 0.2, 'Right': 0.2, 'Left': 0.2} }, 
                                                                     ResultOperation="Subtraction", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })
        
 
        
        self.pm.RegionsOfInterest["Shell1"].UpdateDerivedGeometry(Examination=self.exam, Algorithm="Auto")
        self.pm.RegionsOfInterest["zNTO"].UpdateDerivedGeometry(Examination=self.exam, Algorithm="Auto")

        
if __name__ == "__main__":
    tmp = MakeProstateNodesOars()
        