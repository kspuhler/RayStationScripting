from connect import *

import re
import sys
sys.path.append("\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
sys.path.append("F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")

from RSutil.variables import OPT_STRUCTURE_COLOR
from Launcher.ScriptObject import ScriptObject
from Planning.Structures.Functions.checkForContour import checkForContour


class TargetStructureInterpreter(ScriptObject):
    
    def __init__(self, verboseExecution=False):
        
        super().__init__(verboseExecution=verboseExecution)
        self.ss = self.pm.StructureSets[self.exam.Name]
        try:
            self.constructTargetDictionary()
        except:
            print("Failed to construct target dict!")
            
    
    def preChecks(self):
        if not checkForContour('external'):
            ext = self.pm.CreateRoi(Name="External", Color="Green", Type="External", TissueName="", RbeCellTypeName=None, RoiMaterial=None) ##TODO CHANGE BACK TO EXTERNAL
            ext.CreateExternalGeometry(Examination=self.exam, ThresholdLevel=-250)
    
    def getAllTargets(self):
        #Returns all ptvs in the current structure set iff they have a contour
        tmp = [structure for structure in self.ss.RoiGeometries if structure.HasContours()] #All contoured structures
        targets = [structure.OfRoi.Name for structure in tmp if 'ptv' in structure.OfRoi.Name.lower() 
                   and not any(x in structure.OfRoi.Name.lower() for x in ['opt', 'crop', 'eval'])
                   and structure.OfRoi.Type.lower()=='ptv'] #All contours with PTV in name
        return targets
    
    def inferTargetDose(self, inputString):
        rx = re.findall(r'\d+(?:\.\d+)?', inputString)
        rx = float(rx[0])
        if rx < 1000:
            rx *= 100
        return rx

    def constructTargetDictionary(self):
        targets    = self.getAllTargets()
        self.targetDict = {t : self.inferTargetDose(t) for t in targets} 
        self.targetDict = dict(sorted(self.targetDict.items(), key=lambda item: item[1], reverse=True))

            
    def doCrop(self):
        #This function 
        iterDict = iter(self.targetDict.items())
        prior = []
        for k, v in iterDict:
            
            if prior:
                name = 'z'+ k + '_opt'
                try: #Make the structure $name if it doesn't exist
                    self.pm.CreateRoi(Name=name, Color=OPT_STRUCTURE_COLOR, Type="Control", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)
                except:
                    pass

                self.pm.RegionsOfInterest[name].SetAlgebraExpression(ExpressionA={ 'Operation': "Union", 'SourceRoiNames': [k], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, 
                                                                     ExpressionB={ 'Operation': "Union", 'SourceRoiNames': prior, 'MarginSettings': { 'Type': "Expand", 'Superior': 0.5, 'Inferior': 0.5, 'Anterior': 0.5, 'Posterior': 0.5, 'Right': 0.5, 'Left': 0.5 } }, 
                                                                                               ResultOperation="Subtraction", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })
                self.pm.RegionsOfInterest[name].UpdateDerivedGeometry(Examination=self.exam, Algorithm="Auto")
                
            prior.append(k)
    
    def makeEvalStructure(self, roiName):
        #Makes an eval contour and then checks if it actually needs to exist by determining whether or ot it has the same RoiGeometry as the original structure
        evalRoiName = str(roiName) + "_eval"  
        print(roiName)
        print(evalRoiName)
        try:
            self.pm.CreateRoi(Name=evalRoiName, Color=self.ss.RoiGeometries[roiName].OfRoi.Color, Type="Ptv", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)
        except:
            pass
        
        self.pm.RegionsOfInterest[evalRoiName].SetAlgebraExpression(ExpressionA={ 'Operation': "Union", 'SourceRoiNames': [roiName], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, 
                                                             ExpressionB={ 'Operation': "Union", 'SourceRoiNames': ["External"], 'MarginSettings': { 'Type': "Contract", 'Superior': 0.3, 'Inferior': 0.3, 'Anterior': 0.3, 'Posterior': 0.3, 'Right': 0.3, 'Left': 0.3} }, 
                                                             ResultOperation="Intersection", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })
        
        self.pm.RegionsOfInterest[evalRoiName].UpdateDerivedGeometry(Examination=self.exam, Algorithm="Auto")
        
        if self.ss.RoiGeometries[evalRoiName].GetRoiVolume() == self.ss.RoiGeometries[roiName].GetRoiVolume():
            self.pm.RegionsOfInterest[evalRoiName].DeleteRoi()




        
        
if __name__ == '__main__':
    a = TargetStructureInterpreter()
    a.doCrop()
    for ii in a.targetDict.keys():
        a.makeEvalStructure(ii)
        
        



