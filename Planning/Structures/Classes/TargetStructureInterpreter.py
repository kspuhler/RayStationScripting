from connect import *

import re
import sys
sys.path.append("\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
sys.path.append("F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")

from RSutil.variables import OPT_STRUCTURE_COLOR


class TargetStructureInterpreter(object):
    
    def __init__(self):
        
        self.exam = get_current('Examination')
        self.pm = get_current('Case')
        self.pm = self.pm.PatientModel
        
        self.ss = self.pm.StructureSets[self.exam.Name]
        try:
            self.constructTargetDictionary()
        except:
            print("Failed to construct target dict!")
    def getAllTargets(self):
        #Returns all ptvs in the current structure set iff they have a contour
        tmp = [structure for structure in self.ss.RoiGeometries if structure.HasContours()] #All contoured structures
        targets = [structure.OfRoi.Name for structure in tmp if 'ptv' in structure.OfRoi.Name.lower() 
                   and not any(x in structure.OfRoi.Name.lower() for x in ['opt', 'crop', 'eval'])
                   and structure.OfRoi.Type.lower()=='ptv'] #All contours with PTV in name
        return targets
    
    def inferTargetDose(self, inputString):
        print(inputString)
        rx = re.findall(r'\d+(?:\.\d+)?', inputString)
        print(rx)
        rx = float(rx[0])
        if rx < 1000:
            rx *= 100
        return rx
    
    def constructTargetDictionary(self):
        targets    = self.getAllTargets()
        self.targetDict = {t : self.inferTargetDose(t) for t in targets} 
        self.targetDict = dict(sorted(self.targetDict.items(), key=lambda item: item[1], reverse=True))
        
    def doCrop(self):

        iterDict = iter(self.targetDict.items())
        prior = []
        for k, v in iterDict:
            
            if prior:
                name = 'z'+ k + '_opt'
                try:
                    self.pm.CreateRoi(Name=name, Color=OPT_STRUCTURE_COLOR, Type="Ptv", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)
                except:
                    pass
                print(k)
                print(prior)
                self.pm.RegionsOfInterest[name].SetAlgebraExpression(ExpressionA={ 'Operation': "Union", 'SourceRoiNames': [k], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, 
                                                                                                    ExpressionB={ 'Operation': "Union", 'SourceRoiNames': prior, 'MarginSettings': { 'Type': "Expand", 'Superior': 0.5, 'Inferior': 0.5, 'Anterior': 0.5, 'Posterior': 0.5, 'Right': 0.5, 'Left': 0.5 } }, 
                                                                                               ResultOperation="Subtraction", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })
                self.pm.RegionsOfInterest[name].UpdateDerivedGeometry(Examination=self.exam, Algorithm="Auto")         
            prior.append(k)
        
        
        
if __name__ == '__main__':
    a = TargetStructureInterpreter()
    print(a.targetDict)
    a.doCrop()