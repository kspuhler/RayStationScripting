"""
Created on Wed Aug 14 10:11:08 2024.

@author: santoj14

A breast-specific extension of the FiF calculator for RS that emulates the 
functionality of EZFluence
"""

import sys

from PyQt5.QtWidgets import QMessageBox
from connect import *


sys.path.append("F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD\BreastFiF")
sys.path.append("\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD\BreastFif")

class FieldinField():
    """
    A base class for interacting with the native RS field in field calculator.
    
    Extends its capabilites in order to better accomodate Breast FiF planning in RayStation. 
    """
    
    def __init__(self, *args):
        
        self.examination = get_current("Examination")
        self.case        = get_current("Case")
        self.beam_set    = get_current("BeamSet")
        self.treatment_plan = get_current("Plan")

        self.PatientModel = self.case.PatientModel
        self.StructureSet = self.PatientModel.StructureSets
        self.Contours     = self.StructureSet[self.examination.Name].RoiGeometries
        self.Plans        = self.case.TreatmentPlans

        self.num_segments = []
        
    
    def run_fif(self, *args, **kwargs):
        """Run the native RS Fif calculator from this UI with the user-defined parameters."""
        self.get_segmentation_settings()
        print("using ",self.num_segments," per beam")
        self.beam_set.RunAutomaticFieldInFieldPlanning(NumberOfSubfieldsPerBeam=self.num_segments, 
                                                  DoseTargetVolume=args[0], 
                                                  TargetCoveragePushPercent=50, 
                                                  DoseTargetConformMargin=0, 
                                                  DoseTargetVolumeStrategy="UseExistingROI", 
                                                  ExposePrescriptionPoint=False, 
                                                  PrescriptionPointExposureMargin=1, 
                                                  KeepAuxiliaryRois=True)
        
        self.complete_message()
        
        
    def get_segmentation_settings(self,*args, **kwargs):
        """Get the segmentation settings for the native RS FiF calculator."""
        plan_opt = self.treatment_plan.PlanOptimizations[0]
        seg_settings = plan_opt.OptimizationParameters.TreatmentSetupSettings[0].SegmentConversion
        
        return [seg_settings.MinSegmentMUPerFraction,
                seg_settings.MinSegmentArea,
                seg_settings.MinNumberOfOpenLeafPairs,
                seg_settings.MinLeafEndSeparation
                ]
        
    def set_segmentation_settings(self, *args, **kwargs):
        """
        Set the segmentation settings for the native RS FiF calculator.
        
        The arguments assume the following order for the parameters;      
        Min segment MU per fraction,
        Min segment area,
        Min number of open leaf pairs,
        Min leaf end separation
        """
        plan_opt = self.treatment_plan.PlanOptimizations[0]
        seg_settings = plan_opt.OptimizationParameters.TreatmentSetupSettings[0].SegmentConversion
        
        print('============These are the settings before you changed them================')
        print('Min Segment MU per fraction:', seg_settings.MinSegmentMUPerFraction)
        print('Min Segment Area:', seg_settings.MinSegmentArea)
        print('Min Number of open leaf pairs:', seg_settings.MinNumberOfOpenLeafPairs)
        print('Min leaf end separation:',seg_settings.MinLeafEndSeparation)
        
        seg_settings.MinSegmentMUPerFraction =  args[0]
        seg_settings.MinSegmentArea =           args[1]
        seg_settings.MinNumberOfOpenLeafPairs = args[2]
        seg_settings.MinLeafEndSeparation =     args[3]
        
        print('============These are the new settings ================')
        print('Min Segment MU per fraction:', seg_settings.MinSegmentMUPerFraction)
        print('Min Segment Area:', seg_settings.MinSegmentArea)
        print('Min Number of open leaf pairs:', seg_settings.MinNumberOfOpenLeafPairs)
        print('Min leaf end separation:',seg_settings.MinLeafEndSeparation)
        
        
        
    def complete_message(self, *args, **kwargs):
        """Popup to let you know you're done."""
        msg = 'Field-in-Field calculator is done executing.\nYou can now X-out the window.\nDon\'t forget to save your work'
        scriptComplete = QMessageBox()
        scriptComplete.setIcon(QMessageBox.Information)
        scriptComplete.setWindowTitle("Script Complete")
        scriptComplete.setText(msg)
        scriptComplete.exec_()
        
        