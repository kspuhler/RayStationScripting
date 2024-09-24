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
    def __init__(self, templateDictionary, verboseExecution=False, runPreChecks=True):
        
        
        self.templateDictionary = templateDictionary
        super().__init__(verboseExecution=verboseExecution, runPreChecks=runPreChecks)     
        self.exam.RunDeepLearningSegmentationWithCustomRoiNames(ExaminationsAndRegistrations={self.exam.Name: None }, ModelAndRoiNames= self.templateDictionary)
        self.makeDerivedStructures()
        
        if self.toCopy: #workaround for preexisting structures, implemented in self.preChecks() but run copying occurs after new ROIs/geometries are made of course
            for ii in self.toCopy:
                deleteRoi = ii[0]
                keepRoi   = ii[1]
                self.pm.RegionsOfInterest[keepRoi].CreateAlgebraGeometry(Examination=self.exam, Algorithm="Auto", ExpressionA={ 'Operation': "Union", 'SourceRoiNames': [deleteRoi], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, 
                                                                       ExpressionB={ 'Operation': "Union", 'SourceRoiNames': [], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, 
                                                                       ResultOperation="None", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })
                self.pm.RegionsOfInterest[deleteRoi].DeleteRoi()
    
    def preChecks(self):
        

        #get list of rois we will contour from the dictionary
       
        self.roisToContour = [key for subdict in self.templateDictionary.values() for key in subdict.keys()]
        
        
        self.toCopy = [] #list of tuples (s (1), s) where we will copy s(1) to s then delete s(1)
        for s in self.roisToContour:
            if checkForContour(s):
                if self.pm.StructureSets[self.exam.Name].RoiGeometries[s].HasContours():
                    pass #whatever we should do if it is already contoured on the scan
                else:
                    tup = (f"{s} (1)", s)
                    print(tup)
                    self.toCopy.append(tup)
                    
    def makeDerivedStructures(self):
        pass

if __name__ == "__main__":
    tmp = AutoSegmentationTemplate(templateDictionary=TamAbdomen)
                    
                    