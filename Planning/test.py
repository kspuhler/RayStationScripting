# -*- coding: utf-8 -*-
"""
Created on Thu Mar 14 11:34:39 2024

@author: spuhlk01
"""

# Script recorded 14 Mar 2024, 11:34:15

#   RayStation version: 14.0.0.3338
#   Selected patient: ...

from connect import *

case = get_current("Case")
beam_set = get_current("BeamSet")


# Unscriptable Action 'Save' Completed : SaveAction(...)

with CompositeAction('Add treatment plan'):

  retval_0 = case.AddNewPlan(PlanName="ProstNodes4500", PlannedBy="", Comment="", ExaminationName="CT 1", IsMedicalOncologyPlan=False, AllowDuplicateNames=False)

  retval_1 = retval_0.AddNewBeamSet(Name="ProstNodes4500", ExaminationName="CT 1", MachineName="TrueBeamSN1106", Modality="Photons", TreatmentTechnique="VMAT", PatientPosition="HeadFirstSupine", NumberOfFractions=25, CreateSetupBeams=True, UseLocalizationPointAsSetupIsocenter=False, UseUserSelectedIsocenterSetupIsocenter=False, Comment="", RbeModelName=None, EnableDynamicTrackingForVero=False, NewDoseSpecificationPointNames=[], NewDoseSpecificationPoints=[], MotionSynchronizationTechniqueSettings={ 'DisplayName': None, 'MotionSynchronizationSettings': None, 'RespiratoryIntervalTime': None, 'RespiratoryPhaseGatingDutyCycleTimePercentage': None, 'MotionSynchronizationTechniqueType': "Undefined" }, Custom=None, ToleranceTableLabel="IMRT")

  # CompositeAction ends 


with CompositeAction('Set prescription'):

  with CompositeAction('Add prescription dose references'):

    # CompositeAction ends 


  # Unscriptable Action 'Set prescription' Completed : SetPrescriptionCompositeAction(...)

  retval_1.SetAutoScaleToPrimaryPrescription(AutoScale=True)

  # CompositeAction ends 


# Unscriptable Action 'Save' Completed : SaveAction(...)

retval_1.CopyBeamsFromBeamSet(BeamSetToCopyFrom=beam_set, BeamsToCopy=[])





# Script recorded 14 Mar 2024, 14:02:22

#   RayStation version: 14.0.0.3338
#   Selected patient: ...

from connect import *

beam_set = get_current("BeamSet")


beam_set.CopyAndReverseBeam(BeamName="1 g180")

with CompositeAction('Edit beam (1 g181, beam set: KDS_HAAS_TEST)'):

  beam_set.Beams['1 g181'].Name = "2 g179"

  # CompositeAction ends 
