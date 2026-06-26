import sys
sys.path.append("\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
sys.path.append("F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")

from connect import *
from Planning.Structures.Functions.croppingShortcuts import *


from AutoPlanningBeta.Pipelines.Pipeline import Pipeline

class CK_Prostate_3625(Pipeline):
    
    _REQUISITE_CONTOURS = ["MDGTV"]
    
    _PARAMS = {**Pipeline._PARAMS,
               'PROTOCOL_NAME': "CK Prostate MLC 725x5",
              'NUM_BEAMSETS': 1,
              'PLAN_NAME': 'Prost725x5',
              'BEAM_SET_NAMES': ['Prost725x5'],
              'BEAM_TEMPLATE': None,
              'STRUCTURE_TEMPLATE': {'Name': "PLAN TEMPLATE: CK Prostate MLC 725x5", 
                                     'Structures': ["zNTO", "Testes", "Rectum", "Bladder", "Large Bowel", "Small Bowel",  "PTV3625", "zOptBladder", "zOptRectum", 
                                                    "zOptLBowel", "zOptSBowel", "PTV_CK_Ring_0.2cm", "PTV_CK_Ring_2cm", "PTV_CK_Ring_5cm"]},
              'ISO_PLACEMENT': "target",
              'STEREOTACTIC': True,
              'TARGET': ["PTV3625"],
              'TOTAL_DOSE': [3625],
              'PERCENT_VOL':[95],
              'FRACTIONS': [5],  
              'CLINICAL_GOAL_TEMPLATE': "Prostate CK 725x5 MLC",
              'OPTIMIZATION_TEMPLATE': "SCRIPT TEMPLATE: CK PROSTATE 725x5"
              } 
    
    _MACHINES = ['C0363','C0480']
    
    def __init__(self):
        super().__init__()
        print('subclass')
        self.contouring_workspace()
        print(self.machine_name)
        self.plan_generation()
        self.optimization_workspace()
        self.close_out()
        return
        
    def optimization_workspace(self):
        
        super().optimization_workspace()
        await_user_input('''Please set DNE structures before optimizing''')
        
    def contouring_workspace(self):
        print('contours')
        cropXfromY(x='Bladder', y=['MDGTV'])
        cropXfromY(x='Rectum', y=['MDGTV'])

        
        super().contouring_workspace()

        #Crop rectum
        crop_spacer_from_rectum()

        #Crop rectum 8 slices from ptv
        self.case.PatientModel.RegionsOfInterest['Rectum'].CreateAlgebraGeometry(Examination=self.exam, Algorithm="Auto", ExpressionA={ 'Operation': "Union", 'SourceRoiNames': ["Rectum"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, 
                                                                        ExpressionB={ 'Operation': "Union", 'SourceRoiNames': ["PTV3625"], 'MarginSettings': { 'Type': "Expand", 'Superior': 1.1, 'Inferior': 1.1, 'Anterior': 3, 'Posterior': 12, 'Right': 5, 'Left': 5 } }, ResultOperation="Intersection", 
                                                                        ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })
        await_user_input('''Before moving on: \n
                         1. Inspect rectum and bladder contours.\n
                         2. Contour testes. \n
                         3. Contour large and small bowel.
                         4. Verify zZDNEPosterior \n
                         Then resume script in scripting tab.''')
                             
        del self.ss

    def plan_generation(self):
        self.ui.switch_tab('Plan setup')
        
        
        plan = self.case.AddNewPlan(PlanName=self._PARAMS['PLAN_NAME'], 
                                   PlannedBy="", 
                                   Comment="", 
                                   ExaminationName=self.exam.Name, 
                                   IsMedicalOncologyPlan=False, AllowDuplicateNames=False)
        bs = plan.AddNewBeamSet(Name=self._PARAMS['BEAM_SET_NAMES'][0], 
                                          ExaminationName=self.exam.Name, 
                                          MachineName=self.machine_name, 
                                          Modality="Photons", 
                                          TreatmentTechnique="CyberKnife", 
                                          PatientPosition="HeadFirstSupine", 
                                          NumberOfFractions=self._PARAMS['FRACTIONS'][0], 
                                          CreateSetupBeams=True,
                                          UseLocalizationPointAsSetupIsocenter=False, 
                                          UseUserSelectedIsocenterSetupIsocenter=False, 
                                          Comment="", RbeModelName=None, 
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
        
        bs.SetDefaultDoseGrid(VoxelSize = {'x':0.12, 'y':0.12, 'z': 0.12})
        iso_center = self.case.PatientModel.StructureSets[self.exam.Name].RoiGeometries[self._PARAMS["TARGET"][0]].GetCenterOfRoi()
        beam = bs.CreatePhotonBeam(BeamQualityId="6 FFF", 
                                   CyberKnifeCollimationType="MLC", 
                                   CyberKnifeNodeSetName="body mlc", 
                                   CyberKnifeRampVersion=self.ck_ramp, 
                                   CyberKnifeAllowIncreasedPitchCorrection=True, 
                                   GimbalPanAngle=0, 
                                   GimbalTiltAngle=0, 
                                   IsocenterData={ 'Position': iso_center, 'NameOfIsocenterToRef': "", 'Name': "Prost725x5 1", 'Color': "98, 184, 234" }, 
                                   Name="ck", 
                                   Description="", 
                                   GantryAngle=0, 
                                   CouchRotationAngle=0, 
                                   CouchPitchAngle=0, 
                                   CouchRollAngle=0, 
                                   CollimatorAngle=0)

        beam.SetBolus(BolusName="")

        bs.Beams['ck'].BeamMU = 0
        
        bs.PatientSetup.MotionSynchronization.ImagingProperties[0].SelectTrackedTarget(TrackedTargets=[x.Name for x in self.case.PatientModel.PointsOfInterest if x.Type == "Marker"], DisplayROI="", SpineROI="")
        self.patient.Save()
        self.case.TreatmentPlans[self._PARAMS['PLAN_NAME']].SetCurrent()
        self.set_rx()


import traceback

def main():
    try:
        a = CK_Prostate_3625()
    except Exception:
        traceback.print_exc()
        raise


if __name__ == '__main__':
    main()
    