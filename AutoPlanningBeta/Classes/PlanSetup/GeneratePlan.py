import tkinter as tk
from tkinter import ttk

import sys
sys.path.append("\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
sys.path.append("F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")

from RSutil.variables import TRUEBEAMS, ACCURAY_MACHINES
from Planning.Structures.Functions.checkForContour import checkForContour


from connect import *


class GeneratePlan(object):
    
    
    _defaults = {'numberOfBeamSets': 1,
                 'planName': None,
                 'beamSetNames': None, #LIST
                 'beamTemplate': None,
                 'modality': 'Photons',
                 'machineName': None,
                 'makeSetupBeams': True,
                 'isoPlacement': "setup", #target, setup
                 'targetNameForIsocenter': None, #name of target to put isocenter in
                 'isStereotactic': False, #controls grid size
                 'treatmentTechnique': None,
                 'synchrony': False,
                 'position': 'HeadFirstSupine'}
    
    def __init__(self, *args, **kwargs):
        
        self.switchRsUi()
        
        self.patient = get_current("Patient")
        self.case = get_current("Case")
        self.planToCopy = get_current("Plan")
        self.exam = get_current("Examination")
        
        attributes = self._defaults.copy()
        attributes.update(kwargs)
        self._process_kwargs(attributes)
        
        
    
    def _process_kwargs(self, attributes):
        for key, value in attributes.items():
            if key in self._defaults:
                setattr(self, key, value)
            else:
                setattr(self, key, value)
                print(f"Warning: Unknown attribute '{key}'")
        return
    
    def _check_kwargs(self):
        
        if self.numberOfBeamSets > 1:
            if not isinstance(self.beamSetNames, list):
                print(f'DEBUG: GeneratePlan requires a list for parameter beamSetNames')
            if not len(self.beamSetNames) == self.numberOfBeamSets:
                print(f'DEBUG: GeneratePlan object did not receive correct number of names of beamsets, overwriting to default names.')
                self.beamSetNames = [f"Beamset_{x+1}" for x in range(self.numberOfBeamSets)]
                
        if self.isoPlacement.lower() == "target":
            if not self.targetNameForIsocenter:
                print("You need to name the target for the isocenter and also Karl forgot to implement user selection.")
            elif self.targetNameForIsocenter and not checkForContour(self.targetNameForIsocenter):
                print(f"Selected structure for iso placement {self.targetNameForIsocenter} does not seem to exist. Placing iso at localization point")
                self.isoPlacement = "setup"
                
                
    def switchToGeneratedPlan(self):
        self.patient.Save()
        self.case.TreatmentPlans[self.planName].SetCurrent()
        return
        
    def generatePlan(self, numFractions):

        if not isinstance(self.beamSetNames, list):
            print(f'DEBUG: GeneratePlan requires a list for parameter beamSetNames')
        
        self.case.AddNewPlan(PlanName = self.planName,
                             PlannedBy = '',
                             Comment = '',
                             ExaminationName = self.exam.Name,
                             IsMedicalOncologyPlan = False,
                             AllowDuplicateNames = False)
        
        self.switchToGeneratedPlan()
        self.newPlan = get_current("Plan")
        
        #Make beamsets
        if not self.treatmentTechnique.lower() == "cyberknife":
            createdBeamSets = 0
            while createdBeamSets < self.numberOfBeamSets:
                bs = self.newPlan.AddNewBeamSet(Name = self.beamSetNames[createdBeamSets],
                                                ExaminationName = self.exam.Name,
                                                MachineName = self.machineName,
                                                Modality = self.modality,
                                                TreatmentTechnique = self.treatmentTechnique,
                                                PatientPosition = self.position,
                                                NumberOfFractions = numFractions[createdBeamSets],
                                                CreateSetupBeams = self.makeSetupBeams)
                
        elif self.treatmentTechnique.lower == "cyberknife":
            createdBeamSets = 0
            while createdBeamSets < self.numberOfBeamSets:
                bs = self.newPlan.AddNewBeamSet(Name=self.beamSetNames[createdBeamSets], 
                                              ExaminationName=self.exam.Name, 
                                              MachineName=self.machineName, 
                                              Modality="Photons", 
                                              TreatmentTechnique=self.treatmentTechnique, 
                                              PatientPosition=self.position, 
                                              NumberOfFractions=numFractions[createdBeamSets], 
                                              CreateSetupBeams=True,
                                              UseLocalizationPointAsSetupIsocenter=False, 
                                              UseUserSelectedIsocenterSetupIsocenter=False, 
                                              Comment="", 
                                              RbeModelName=None, 
                                              EnableDynamicTrackingForVero=False, 
                                              NewDoseSpecificationPointNames=[], 
                                              NewDoseSpecificationPoints=[], 
                                              MotionSynchronizationTechniqueSettings={ 'DisplayName': "Fiducial with InTempo", 
                                                                                      'MotionSynchronizationSettings': [{ 'RespiratoryMotionCompensationTechnique': "Tracking", 
                                                                                                                         'RespiratorySignalSource': "DualImagers" }, 
                                                                                                                        { 'RespiratoryMotionCompensationTechnique': "IntervalImaging", 'RespiratorySignalSource': "DualImagers" }], 
                                                                                      'RespiratoryIntervalTime': None, 
                                                                                      'RespiratoryPhaseGatingDutyCycleTimePercentage': None, 'MotionSynchronizationTechniqueType': "FiducialWithInTempo" }, 
                                                                                      Custom=None, ToleranceTableLabel=None)
                
            
        #dose grid
        if self.isStereotactic:
            bs.SetDefaultDoseGrid(VoxelSize = {'x':0.12, 'y':0.12, 'z': 0.12})
        else:
            bs.SetDefaultDoseGrid(VoxelSize = {'x':0.25, 'y':0.25, 'z': 0.25})
        
        
        self.loadAndProcessBeamTemplate(bs)
        
        createdBeamSets+=1
        
            
    def processIsocenter(self):
        pass
            
    def loadAndProcessBeamTemplate(self, bs):
        
        if self.isoPlacement.lower() == "setup":
            iso = self.case.PatientModel.StructureSets[self.exam.Name].LocalizationPoiGeometry.Point
        elif self.isoPlacement.lower() == "target": 
            iso = self.case.PatientModel.StructureSets[self.exam.Name].RoiGeometries[self.targetNameForIsocenter].GetCenterOfRoi()
        
        if self.treatmentTechnique.lower() == 'vmat':
            db = get_current("PatientDB")
        
            BeamTemplate = db.LoadTemplateBeamList(templateName = self.beamTemplate, lockMode = "Read")
        
            #delete this

        

            for beam in BeamTemplate.TreatmentSetups[0].Beams:

                beamID = bs.CreateArcBeam(ArcStopGantryAngle=beam.ArcStopGantryAngle, 
                                              ArcRotationDirection=beam.ArcRotationDirection, 
                                              BeamQualityId=beam.BeamQualityId, 
                                              IsocenterData={ 'Position': { 'x': iso['x'], 'y': iso['y'], 'z': iso['z'] }, 'NameOfIsocenterToRef': 'ISO', 'Name': 'ISO', 'Color': "255, 255, 128" }, 
                                              Name=beam.Name, 
                                              Description="", 
                                              GantryAngle=beam.GantryAngle, 
                                              CouchRotationAngle=beam.CouchRotationAngle, 
                                              CollimatorAngle=beam.InitialCollimatorAngle)
               
                


            
        elif self.treatmentTechnique.lower() ==  "tomohelical":
           print("CREATING TOMO BEAM") 
           beam = bs.CreatePhotonBeam(BeamQualityId="6", 
                                CyberKnifeCollimationType="Undefined", 
                                CyberKnifeNodeSetName=None, 
                                CyberKnifeRampVersion=None, 
                                CyberKnifeAllowIncreasedPitchCorrection=None, 
                                GimbalPanAngle=0, 
                                GimbalTiltAngle=0, 
                                IsocenterData={ 'Position': { 'x': iso['x'], 'y': iso['y'], 'z': iso['z'] }, 'NameOfIsocenterToRef': 'ISO', 'Name': 'ISO', 'Color': "255, 255, 128" }, 
                                Name="1", 
                                Description="", 
                                GantryAngle=0, 
                                CouchRotationAngle=0, 
                                CouchPitchAngle=0, 
                                CouchRollAngle=0, 
                                CollimatorAngle=0)
           beam.SetBolus(BolusName="")
           beam.BeamMU = 0

        elif self.treatmentTechnique.lower() == "cyberknife":
            print("MAKING CK BEAM")
             
            


        
        
            
    def switchRsUi(self):
        #move user view to contouring window
        ui = get_current("ui")
        ui.TitleBar.Navigation.MenuItem["Plan design"].Button.Click()

        
        
if __name__ == '__main__':
    a = GeneratePlan(planName = 'test', 
                     beamSetNames = ['test'],
                     machineName = 'TrueBeamSN1106',
                     treatmentTechnique = 'VMAT',
                     beamTemplate = 'kds 2 arc 0 90 col')
    a.generatePlan(numFractions = [25])