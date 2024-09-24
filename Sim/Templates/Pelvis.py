# -*- coding: utf-8 -*-
"""
Created on Thu Feb  8 15:20:02 2024

@author: spuhlk01
"""

try:
    from connect import *
except:
    pass

import sys

sys.path.append("\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
sys.path.append("F:\SHARING\Radiation Oncology Physics\RaystationScripting\Planning\Structures\Templates")


from Sim.Templates.Isocenters import Isocenters
from RSutil.functions import interpretCTSimOrientation
from Planning.Structures.Templates.StructureTemplate import StructureTemplate
from Planning.Structures.Templates.roi_list_templates import prostNodes4500 as prostNodes4500
from Planning.Structures.Templates.roi_list_templates import prostSBRT as prostSBRT

class Pelvis(Isocenters):
    
    """"Makes a plan with N isocenters/beamSets. N can also equal 1"""
    def __init__(self, numberOfIsocenters, planName, beamSetName):
        
        self.numberOfIsocenters = numberOfIsocenters
        
        super().__init__(numberOfIsocenters, planName, beamSetName)
    
    
    def addStructures(self, case, examination):
        structures = StructureTemplate(prostNodes4500, self.case.PatientModel)
        structures.make_empty_rois()
        self.exam.RunDeepLearningSegmentationWithCustomRoiNames(ExaminationsAndRegistrations={self.exam.Name: None }, ModelAndRoiNames= {'RSL DLS Male Pelvic CT': {'GTVp': 'Prostate',  'Bladder': 'Bladder', 
                                                                                                                                                                     'GTVsv': 'SeminalVesicles', 'Rectum': 'Anorectum', 
                                                                                                                                                                    'Lt Femoral': 'Femur_Head_L', 'Rt Femoral': 'Femur_Head_R'}})
        
        gtv = case.PatientModel.CreateRoi(Name="MDGTV", Color="Red", Type="Gtv", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)
        gtv.SetAlgebraExpression(ExpressionA={ 'Operation': "Union", 'SourceRoiNames': ["GTVp"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ExpressionB={ 'Operation': "Union", 'SourceRoiNames': ["GTVsv"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ResultOperation="Union", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })

    
        

                                                                                                                                                                  
    def addBeamsToBeamSet(self, beamNames = [], gantry = 0, collimator = 0):
        
            iso = self.case.PatientModel.StructureSets[self.exam.Name].RoiGeometries['GTVp'].GetCenterOfRoi()
                                    
            beam = self.beamSet.CreatePhotonBeam(BeamQualityId='6',  IsocenterData={ 'Position': { 'x': iso['x'], 'y': iso['y'], 'z': iso['z'] }, 'NameOfIsocenterToRef': 'Pelvis ISO', 'Name': 'Pelvis ISO', 'Color': "255, 255, 128" }, 
                                          Name = '1 g0', GantryAngle = gantry, CollimatorAngle = collimator)
            
            beam.SetInitialJawPositions(X1=-5, X2 = 5, Y1 = -5, Y2 = 5)


class ProstateCK(Isocenters):
    
    """"Makes a plan with N isocenters/beamSets. N can also equal 1"""
    def __init__(self, numberOfIsocenters, planName, beamSetName):
        
        self.numberOfIsocenters = numberOfIsocenters
        
        super().__init__(numberOfIsocenters, planName, beamSetName)
    
    
    def addStructures(self, case, examination):
        structures = StructureTemplate(prostSBRT, self.case.PatientModel)
        structures.make_empty_rois()
        self.exam.RunDeepLearningSegmentationWithCustomRoiNames(ExaminationsAndRegistrations={self.exam.Name: None }, ModelAndRoiNames= {'RSL DLS Male Pelvic CT': {'GTVp': 'Prostate',  'Bladder': 'Bladder', 
                                                                                                                                                                     'GTVsv': 'SeminalVesicles', 'Rectum': 'Anorectum'}})
        try:
            gtv = case.PatientModel.CreateRoi(Name="GTV_CK", Color="Red", Type="Gtv", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)
            gtv.SetAlgebraExpression(ExpressionA={ 'Operation': "Union", 'SourceRoiNames': ["GTVp"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ExpressionB={ 'Operation': "Union", 'SourceRoiNames': ["GTVsv_CK"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ResultOperation="Union", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })
        except:
            pass
    
        

                                                                                                                                                                  
    def addBeamsToBeamSet(self, beamNames = [], gantry = 0, collimator = 0):
        
            iso = self.case.PatientModel.StructureSets[self.exam.Name].RoiGeometries['GTVp'].GetCenterOfRoi()
                                    
            beam = self.beamSet.CreatePhotonBeam(BeamQualityId='6',  IsocenterData={ 'Position': { 'x': iso['x'], 'y': iso['y'], 'z': iso['z'] }, 'NameOfIsocenterToRef': 'Pelvis ISO', 'Name': 'Pelvis ISO', 'Color': "255, 255, 128" }, 
                                          Name = '1 g0', GantryAngle = gantry, CollimatorAngle = collimator)
            
            beam.SetInitialJawPositions(X1=-5, X2 = 5, Y1 = -5, Y2 = 5)
                        
        
if __name__ == "__main__":
    tmp = ProstateCK(1, "Haastestjhv", "Haastestjhv")
    
    