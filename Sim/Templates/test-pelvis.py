# -*- coding: utf-8 -*-
"""
Created on Wed Jan 28 10:20:36 2026

@author: spuhlk01
"""

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

class PelvisTest(Isocenters):
    
    def __init__(self, numberOfIsocenters, planName, beamSetName):
        
        self.numberOfIsocenters = numberOfIsocenters
        
        super().__init__(numberOfIsocenters, planName, beamSetName)
        try:
            self.case.BodySite = "Pelvis"
        except:
            pass
    
    def addStructures(self, case, examination):
        structures = StructureTemplate(prostNodes4500, self.case.PatientModel)
        structures.make_empty_rois()
        self.exam.RunDeepLearningSegmentationWithCustomRoiNames(ExaminationsAndRegistrations={self.exam.Name: None }, ModelAndRoiNames= {'RSL DLS Male Pelvic CT': {'GTVp': 'Prostate',  'Bladder': 'Bladder', 
                                                                                                                                                                    'GTVsv': 'SeminalVesicles', 'Rectum': 'Anorectum', 
                                                                                                                                                                    'Lt Femoral': 'Femur_Head_L', 'Rt Femoral': 'Femur_Head_R', 'Bowel': "BowelSpc"}})
        if not "MDGTV" in [x.Name for x in self.case.PatientModel.RegionsOfInterest]:
            gtv = case.PatientModel.CreateRoi(Name="MDGTV", Color="Red", Type="Gtv", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)
        gtv.SetAlgebraExpression(ExpressionA={ 'Operation': "Union", 'SourceRoiNames': ["GTVp"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, 
                                 ExpressionB={ 'Operation': "Union", 'SourceRoiNames': ["GTVsv"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, 
                                 ResultOperation="Union", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })
        
        if case.Physician.Name.lower() in ["jh", "haas", "jhaas"]:
            db = get_current("PatientDB")
            atlas = db.LoadTemplatePatientModel(templateName='ProstateNodes Haas Test')
            case.PatientModel.CreateStructuresFromAtlas(SourceTemplate=atlas, SourceExaminationsNames=["17622598", "12802972", "13490725", "12572656", "8957315", "1143702", 
                                                                                                                                                     "11912146", "16243828", "12541668", "10375426", "1473151", "12737576", 
                                                                                                                                                     "12775370", "11152963", "15210295", "12652739", "11303202", "14065197", 
                                                                                                                                                     "17496255", "2115637", "17548019", "12435874", "16333837", "9026878", 
                                                                                                                                                     "9535844", "12391953", "16302939", "12511634"], 
                                                        SourceRoiNames=["LtNode", "RtNode"], SourcePoiNames=[], AssociateStructuresByName=True, TargetExamination=examination, NrOfFusionAtlases=15)


                                                                                                                                                                  
    def addBeamsToBeamSet(self, beamNames = [], gantry = 0, collimator = 0):
        
            iso = self.case.PatientModel.StructureSets[self.exam.Name].RoiGeometries['GTVp'].GetCenterOfRoi()
                                    
            beam = self.beamSet.CreatePhotonBeam(BeamQualityId='6',  IsocenterData={ 'Position': { 'x': iso['x'], 'y': iso['y'], 'z': iso['z'] }, 'NameOfIsocenterToRef': 'Pelvis ISO', 'Name': 'Pelvis ISO', 'Color': "255, 255, 128" }, 
                                          Name = '1 g0', GantryAngle = gantry, CollimatorAngle = collimator)
            
            beam.SetInitialJawPositions(X1=-5, X2 = 5, Y1 = -5, Y2 = 5)


class ProstateCK(Isocenters):
    
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
    tmp = PelvisTest(1,'test','test')
    
    