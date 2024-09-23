try:
    from connect import *
except:
    pass


import sys
sys.path.append("\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
sys.path.append("F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")

from Launcher.ScriptObject import ScriptObject

from Planning.Structures.Functions.checkForContour import checkForContour
from Planning.Structures.Templates.deepLearningSegmentationDictionaries import TamHeadAndNeck, TamAbdomen

class AutoSegmentationTemplate(ScriptObject):
    '''takes a dictionary of kv pairs '''
    DL_MODEL_NAMES = ['RSL DLS ' + x for x in ['Breast CT', 'Head and Neck CT', 'Male Pelvic CT', 'Thorax-Abdomen CT']]
    def __init__(self, roisToContour, deepLearningModel, verboseExecution=False, runPreChecks=True):
        
        self.roisToContour = roisToContour
        
        super().__init__(verboseExecution=verboseExecution, runPreChecks=runPreChecks)
        
        self.deepLearningModel = deepLearningModel
        self.exam.RunDeepLearningSegmentationWithCustomRoiNames(ExaminationsAndRegistrations={self.exam.Name: None }, ModelAndRoiNames= self.assembleRoiDictForDeepLearningCall())
        self.makeDerivedStructures()
        
        if self.toCopy:
            for ii in self.toCopy:
                deleteRoi = ii[0]
                keepRoi   = ii[1]
                self.pm.RegionsOfInterest[keepRoi].CreateAlgebraGeometry(Examination=self.exam, Algorithm="Auto", ExpressionA={ 'Operation': "Union", 'SourceRoiNames': [deleteRoi], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, 
                                                                       ExpressionB={ 'Operation': "Union", 'SourceRoiNames': [], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, 
                                                                       ResultOperation="None", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })
                self.pm.RegionsOfInterest[deleteRoi].DeleteRoi()
    
    def preChecks(self):
        if not self.deepLearningModel in self.DL_MODEL_NAMES:
            raise Exception("You have provided an invalid deep learning model name!")
            
        #Handle pre-existing structures 
        self.toCopy = [] #list of tuples (s (1), s) where we will copy s(1) to s then delete s(1)
        
        for s in list(self.roisToContour.keys()):
            if checkForContour(s):
                if self.pm.StructureSets[self.exam.Name].RoiGeometries[s].HasContours():
                    pass #whatever we should do if it is already contoured on the scan
                else:
                    tup = (f"{s} (1)", s)
                    print(tup)
                    self.toCopy.append(tup)
                    
                    
        
    
    def assembleRoiDictForDeepLearningCall(self):
        print(self.roisToContour)
        dlDictionary = {self.deepLearningModel: self.roisToContour}
        return dlDictionary
    
    def makeDerivedStructures(self):
        pass
        
    

class TamHeadAndNeckTemplate(AutoSegmentationTemplate):
    
    def __init__(self, roisToContour = TamHeadAndNeck, deepLearningModel = 'RSL DLS Head and Neck CT'):
        self.roisToContour = roisToContour
        self.deepLearningModel = deepLearningModel
        super().__init__(roisToContour = roisToContour, deepLearningModel=deepLearningModel)
        
    def makeDerivedStructures(self):
        if not checkForContour("Cord+5mm"):
            cord5mm = self.pm.CreateRoi(Name="Cord+5mm", Color="Fuchsia", Type="Organ", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)
            cord5mm.SetAlgebraExpression(ExpressionA={ 'Operation': "Union", 'SourceRoiNames': ["SpinalCord"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0.5, 'Inferior': 0.5, 'Anterior': 0.5, 'Posterior': 0.5, 'Right': 0.5, 'Left': 0.5 } }, ExpressionB={ 'Operation': "Union", 'SourceRoiNames': [], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ResultOperation="None", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })

        else:
            try:
                cord5mm = self.pm.RegionsOfInterest['Cord+5mm'].SetAlgebraExpression(ExpressionA={ 'Operation': "Union", 'SourceRoiNames': ["SpinalCord"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0.5, 'Inferior': 0.5, 'Anterior': 0.5, 'Posterior': 0.5, 'Right': 0.5, 'Left': 0.5 } }, 
                                                                                     ExpressionB={ 'Operation': "Union", 'SourceRoiNames': [], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, 
                                                                                     ResultOperation="None", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })
            except:
                print("Cannot create spinal cord PRV!")


        cord5mm.UpdateDerivedGeometry(Examination=self.exam, Algorithm="Auto")
        
class TamAbdomenTemplate(AutoSegmentationTemplate):
    
    def __init__(self, roisToContour = TamAbdomen, deepLearningModel = 'RSL DLS Thorax-Abdomen CT'):
        self.roisToContour = roisToContour
        self.deepLearningModel = deepLearningModel
        super().__init__(roisToContour = roisToContour, deepLearningModel=deepLearningModel)
    
    def makeDerivedStructures(self):
        if not checkForContour("Cord+5mm"):
            cord5mm = self.pm.CreateRoi(Name="Cord+5mm", Color="Fuchsia", Type="Organ", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)
            cord5mm.SetAlgebraExpression(ExpressionA={ 'Operation': "Union", 'SourceRoiNames': ["SpinalCord"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0.5, 'Inferior': 0.5, 'Anterior': 0.5, 'Posterior': 0.5, 'Right': 0.5, 'Left': 0.5 } }, 
                                         ExpressionB={ 'Operation': "Union", 'SourceRoiNames': [], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, 
                                         ResultOperation="None", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })

        else:
            try:
                cord5mm = self.pm.RegionsOfInterest['Cord+5mm'].SetAlgebraExpression(ExpressionA={ 'Operation': "Union", 'SourceRoiNames': ["SpinalCord"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0.5, 'Inferior': 0.5, 'Anterior': 0.5, 'Posterior': 0.5, 'Right': 0.5, 'Left': 0.5 } }, 
                                                                                     ExpressionB={ 'Operation': "Union", 'SourceRoiNames': [], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, 
                                                                                     ResultOperation="None", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })
            except:
                print("Cannot create spinal cord PRV!")


        cord5mm.UpdateDerivedGeometry(Examination=self.exam, Algorithm="Auto")
        
        if not checkForContour("Lungs"):
            lungs = self.pm.CreateRoi(Name="Lungs", Color="Fuchsia", Type="Organ", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)
            lungs.SetAlgebraExpression(ExpressionA={ 'Operation': "Union", 'SourceRoiNames': ["Lung_L", "Lung_R"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, 
                                       ExpressionB={ 'Operation': "Union", 'SourceRoiNames': [], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, 
                                       ResultOperation="None", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })
        else:
            try:
                lungs = self.pm.RegionsOfInterest['Lungs'].SetAlgebraExpression(ExpressionA={ 'Operation': "Union", 'SourceRoiNames': ["Lung_L", "Lung_R"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, 
                                                                                ExpressionB={ 'Operation': "Union", 'SourceRoiNames': [], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, 
                                                                                ResultOperation="None", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })
            except: 
                print("Cannot create Lungs!")
            lungs.UpdateDerivedGeometry(Examination=examination, Algorithm="Auto")
            
        if not checkForContour("Kidneys"):
            kidneys = self.pm.CreateRoi(Name="Kidneys", Color="Fuchsia", Type="Organ", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)
            kidneys.SetAlgebraExpression(ExpressionA={ 'Operation': "Union", 'SourceRoiNames': ["Kidney_L", "Kidney_R"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, 
                                           ExpressionB={ 'Operation': "Union", 'SourceRoiNames': [], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, 
                                           ResultOperation="None", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })
        else:
            try:
                kidneys = self.pm.RegionsOfInterest['Kidneys'].SetAlgebraExpression(ExpressionA={ 'Operation': "Union", 'SourceRoiNames': ["Kidney_L", "Kidney_R"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, 
                                                                                    ExpressionB={ 'Operation': "Union", 'SourceRoiNames': [], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, 
                                                                                    ResultOperation="None", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })
            except: 
                print("Cannot create Kidneys!")
            kidneys.UpdateDerivedGeometry(Examination=examination, Algorithm="Auto")
            
        self.pm.UpdateDerivedGeometries(RoiNames=["Kidneys", "Lungs"], Examination=self.exam, Algorithm="Auto", AreEmptyDependenciesAllowed=False)
            

        
        


if __name__ == '__main__':
    tmp = TamHeadAndNeckTemplate()

