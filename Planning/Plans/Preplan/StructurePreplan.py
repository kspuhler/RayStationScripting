# -*- coding: utf-8 -*-
"""
Created on Mon Apr  1 15:45:56 2024

@author: spuhlk01
"""



class StructurePreplan(object):
    
    
    TARGETS = []
    OARS    = [] 
    
    def __init__(self, patientModel, exam):
        
        self.pm   = patientModel
        self.exam = exam

        self.structureLists()
        self.structureCheck()
    
    
    def makeRing(self, structure, distance, thickness = 4):
        
        ringName = "zzRing" + str(int(distance)) + "mm"
        
        #distance and thickness in mm converted to cm
        distance = distance/10
        thickness = thickness/10
        
        outter = distance + thickness/2
        inner  = distance - thickness/2
        
        
        
        ring = self.pm.CreateRoi(Name=ringName, Color="Fuchsia", Type="Control", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)

        ring.SetAlgebraExpression(ExpressionA={ 'Operation': "Union", 'SourceRoiNames': [structure], 'MarginSettings': { 'Type': "Expand", 'Superior': outter, 'Inferior': outter, 'Anterior': outter, 'Posterior': outter, 'Right': outter, 'Left': outter } }, ExpressionB={ 'Operation': "Union", 'SourceRoiNames': [structure], 'MarginSettings': { 'Type': "Expand", 'Superior': inner, 'Inferior': inner, 'Anterior': inner, 'Posterior': inner, 'Right': inner, 'Left': inner } }, ResultOperation="Subtraction", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })

        ring.UpdateDerivedGeometry(Examination = self.exam, Algorithm="Auto")
    
    def structureLists(self):
        rois = [ii for ii in self.pm.RegionsOfInterest] 
        self.targetsList = [ii.Name for ii in rois if ii.Type.lower() in ['gtv','ctv','itv','ptv']]
        self.oarsList    = [ii.Name for ii in rois if ii.Type.lower() == 'organ']
    
    def structureCheck(self):
        rois = [ii for ii in self.pm.RegionsOfInterest] 
        self.targetChecks()
        self.oarChecks()
        self.structureLists()
    
    def targetChecks(self):
        for ii in self.TARGETS:
            if not ii in self.targetsList:
              self.pm.CreateRoi(Name=ii, Color="Red", Type="Ptv", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)
    
    def oarChecks(self):
        for ii in self.OARS:
            if not ii in self.oarsList:
              self.pm.CreateRoi(Name=ii, Color="White", Type="Organ", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)
    
    def makeOptStructures(self):
        pass
        
        

    

class ProstNodes4500StructurePreplan(StructurePreplan):
    
    
    TARGETS = ["PTV4500", "PTVp", "PTVn"]
    RINGS   = [5, 20, 50]
    
    def __init__(self, patientModel, exam):
        super().__init__(patientModel, exam)
        self.makePTV()
        #self.makeOptStructures()
        
                
    def makePTV(self):
        print("TARGETS: ")
        print(self.targetsList)
        if 'MDGTV' in self.targetsList and 'MDGTV' in self.targetsList:
            ptvp = self.pm.RegionsOfInterest['PTVp'].SetAlgebraExpression(ExpressionA={ 'Operation': "Union", 'SourceRoiNames': ["MDGTV"], 
                                                                                       'MarginSettings': { 'Type': "Expand", 'Superior': 0.7, 'Inferior': 0.7, 'Anterior': 0.7, 'Posterior': 0.5, 'Right': 0.7, 'Left': 0.7 } }, 
                                                                          ExpressionB={ 'Operation': "Union", 'SourceRoiNames': [], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ResultOperation="None", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })
        elif 'jhgtv' in [x.lower() for x in self.targetsList]:
            ptvp = self.pm.RegionsOfInterest['PTVp'].SetAlgebraExpression(ExpressionA={ 'Operation': "Union", 'SourceRoiNames': ["JHGTV"], 
                                                                                       'MarginSettings': { 'Type': "Expand", 'Superior': 0.7, 'Inferior': 0.7, 'Anterior': 0.7, 'Posterior': 0.5, 'Right': 0.7, 'Left': 0.7 } }, 
                                                                          ExpressionB={ 'Operation': "Union", 'SourceRoiNames': [], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ResultOperation="None", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })
        else:
            pass
            #TODO Error handling for unable to find the 
            
            
        ptvn = self.pm.RegionsOfInterest['PTVn'].SetAlgebraExpression(ExpressionA={ 'Operation': "Union", 'SourceRoiNames': ["LtNode", "RtNode"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0.7, 'Inferior': 0.7, 'Anterior': 0.7, 'Posterior': 0.7, 'Right': 0.7, 'Left': 0.7 } }, 
                                                                      ExpressionB={ 'Operation': "Union", 'SourceRoiNames': [], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ResultOperation="None", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })

        
        ptv4500 = self.pm.RegionsOfInterest['PTV4500'].SetAlgebraExpression(ExpressionA={ 'Operation': "Union", 'SourceRoiNames': ["PTVp", "PTVn"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0.0, 'Inferior': 0.0, 'Anterior': 0.0, 'Posterior': 0.0, 'Right': 0.0, 'Left': 0.0 } }, 
                                                                      ExpressionB={ 'Operation': "Union", 'SourceRoiNames': [], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ResultOperation="None", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })
        
        ptvp.UpdateDerivedGeometry(Examination=self.exam, Algorithm="Auto")
        ptvn.UpdateDerivedGeometry(Examination=self.exam, Algorithm="Auto")
        ptv4500.UpdateDerivedGeometry(Examination = self.exam, Algorithm = "Auto")
        
    def makeOptStructures(self):
        pass
        
    
    def makeOptStructures(self):
        for ii in self.RINGS:
            self.makeRing("PTV4500", ii)
        
        