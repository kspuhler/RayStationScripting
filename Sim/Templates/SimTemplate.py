#Author KDS
try:
    from connect import *
except:
    pass

from datetime import datetime


import os
import sys



sys.path.append("\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
sys.path.append("F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")

from RSutil.functions import genUniqueName
from RSutil.functions import interpretCTSimOrientation



class SimTemplate(object):


    def __init__(self, planName = "SIM", beamSetName = "SIM") -> None:
        
        self.case        = get_current("Case")
        self.exam        = get_current("Examination")
        
        self.planName    = planName
        self.beamSetName = beamSetName
        
        self.generatePlan()
        self.addBeamSet()
        self.addStructures(self.case, self.exam)
        
 
    def addStructures(self, case, examination):
        pass

    def generatePlan(self):
        planNames = [x.Name for x in self.case.TreatmentPlans]
        self.planName = genUniqueName(planNames, self.planName)
        self.case.AddNewPlan(PlanName=self.planName, PlannedBy="", Comment="", ExaminationName=self.exam.Name)
        
        if not "External" in [x.Name for x in self.case.PatientModel.RegionsOfInterest]:
             retval_0 = self.case.PatientModel.CreateRoi(Name="External", Color="Green", Type="External", TissueName="", RbeCellTypeName=None, RoiMaterial=None)
             retval_0.CreateExternalGeometry(Examination=self.exam, ThresholdLevel=-250)
             
        
        for tx in self.case.TreatmentPlans:
            if tx.Name == self.planName:
                self.plan = tx
        
        if False:
            if not 'UserOrigin' in [x.Name for x in self.case.PatientModel.PointsOfInterest]:
                self.case.PatientModel.CreatePoi(Examination = self.exam, Point = {'x': 0, 'y': 0, 'z': 0} , Name='UserOrigin', Color="Green", VisualizationDiameter=1, Type="Isocenter")
                     
        
    def addBeamSet(self):
        beamSets = [x.DicomPlanLabel for x in self.plan.BeamSets]
        self.beamSetName = genUniqueName(beamSets, self.beamSetName)
        self.beamSet = self.plan.AddNewBeamSet(Name=self.beamSetName, ExaminationName=self.exam.Name, MachineName="21EX", Modality="Photons", TreatmentTechnique="Conformal", PatientPosition=interpretCTSimOrientation(self.exam), NumberOfFractions=99, CreateSetupBeams=False, 
                           UseLocalizationPointAsSetupIsocenter=False, UseUserSelectedIsocenterSetupIsocenter=False, Comment="", Custom=None, ToleranceTableLabel=None)
        


    def addBeamsToBeamSet(self):
        raise NotImplementedError





