#do not edit

class Cyberknife_Tracking_Base(object):
    
    self.dict_to_pass = None
    
    def __init__(self):
        pass
    
    def set_tracking_targets(self):
        pass
    
    def get_dict(self):
        return self.dict_to_pass
    
    
class Fiducial_In__Tempo(Cyberknife_Tracking_Base)


in_tempo = { 'DisplayName': "Fiducial with InTempo", 
            'MotionSynchronizationSettings': [{ 'RespiratoryMotionCompensationTechnique': "Tracking", 'RespiratorySignalSource': "DualImagers" }, 
                                             { 'RespiratoryMotionCompensationTechnique': "IntervalImaging", 'RespiratorySignalSource': "DualImagers" }], 
            'RespiratoryIntervalTime': None, 
            'RespiratoryPhaseGatingDutyCycleTimePercentage': None, 
            'MotionSynchronizationTechniqueType': "FiducialWithInTempo" }

  #retval_1 = retval_0.AddNewBeamSet(Name="ck", ExaminationName="CT 1", MachineName="C0480", Modality="Photons", TreatmentTechnique="CyberKnife", PatientPosition="HeadFirstSupine", NumberOfFractions=4, CreateSetupBeams=True, UseLocalizationPointAsSetupIsocenter=False, UseU
#  serSelectedIsocenterSetupIsocenter=True, Comment="", RbeModelName=None, EnableDynamicTrackingForVero=False, NewDoseSpecificationPointNames=[], NewDoseSpecificationPoints=[], MotionSynchronizationTechniqueSettings={ 'DisplayName': "Lung with Respiratory", 'MotionSynchronizationSettings': [{ 'RespiratoryMotionCompensationTechnique': "Tracking", 'RespiratorySignalSource': "DualImagers" }, { 'RespiratoryMotionCompensationTechnique': "Realtime", 'RespiratorySignalSource': "ExternalMarker" }], 'RespiratoryIntervalTime': None, 'RespiratoryPhaseGatingDutyCycleTimePercentage': None, 'MotionSynchronizationTechniqueType': "LungWithRespiratory" }, Custom=None, ToleranceTableLabel=None)

spine_tracking = { 'DisplayName': "Lung with Respiratory", 
                  'MotionSynchronizationSettings': [{ 'RespiratoryMotionCompensationTechnique': "Tracking", 'RespiratorySignalSource': "DualImagers" }, 
                                                    { 'RespiratoryMotionCompensationTechnique': "Realtime", 'RespiratorySignalSource': "ExternalMarker" }], 
                  'RespiratoryIntervalTime': None, 'RespiratoryPhaseGatingDutyCycleTimePercentage': None, 
                  'MotionSynchronizationTechniqueType': "LungWithRespiratory" }


