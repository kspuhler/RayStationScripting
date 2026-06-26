from connect import *

import sys

sys.path.append("\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
sys.path.append("F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")

from RSutil.variables import TRUEBEAMS, RADIXACTS
from Planning.Structures.Classes.MakePTVProstateEBRT import MakePTVProstateEBRT
from FrontEnd import DropdownMenuWindow

case = get_current("Case")
plan = get_current("Plan")

if not case.Physician == 'JH':
    raise Exception("THIS IS ONLY FOR JON HAAS PLANS")




#Make PTV and targets
MakePTVProstateEBRT()


#Pause and ask user to contour Spc_Bowel
await_user_input("Please fill in geometry for Spc_Bowel structure and continue script")


#Make Opt structures



#Prompt user for machine TB or Radixact


#Create plan with default beams if TB

#Load clinical goals and optimization template
plan.TreatmentCourse.EvaluationSetup.ApplyClinicalGoalTemplate(Template=root.TemplateTreatmentOptimizations['JH IMRT Pelvis PRF'], AssociatedRoisAndPois={ 'PTV4500': "PTV4500", 'BowelBag': "Spc_Bowel", 'Rectum': "Rectum", 'Bladder - GTVp': "Bladder", 'Lt Femoral': "Lt Femoral", 'Rt Femoral': "Rt Femoral" })

plan.PlanOptimizations[0].ApplyOptimizationTemplate(Template=root.TemplateTreatmentOptimizations['JH_delete'], 
                                                    AssociatedRoisAndPois={ 'PTV_ltn': "", 'PTV_rtn': "", 'PTVp': "PTVp", 'MDGTV': "MDGTV", 'zzFalloffHigh': "", 'zzFallOffMid': "", 'zzRectumPost': "", 'Bladder-GTVp': "", 'zzFallOffLow': "", 'External': "External", 'Spc_Bowel': "", 'Rectum': "Rectum", 'PTV4500': "PTV4500" })

#Run optimizer

#Check for failing goals and finetune if needed


#Switch to plan eval tab and tell user script is done running 


# Script recorded 03 Apr 2025, 12:44:43

#   RayStation version: 14.0.0.3338
#   Selected patient: ...

from connect import *

case = get_current("Case")
plan = get_current("Plan")
beam_set = get_current("BeamSet")
examination = get_current("Examination")


# Unscriptable Action 'Save' Completed : SaveAction(...)

with CompositeAction('Add treatment plan'):

  retval_0 = case.AddNewPlan(PlanName="TB test", PlannedBy="", Comment="dnu", ExaminationName="CT 1", IsMedicalOncologyPlan=False, AllowDuplicateNames=False)

  retval_1 = retval_0.AddNewBeamSet(Name="TB test", ExaminationName="CT 1", MachineName="TrueBeamSN1106", Modality="Photons", TreatmentTechnique="VMAT", PatientPosition="HeadFirstSupine", NumberOfFractions=25, CreateSetupBeams=True, UseLocalizationPointAsSetupIsocenter=False, UseUserSelectedIsocenterSetupIsocenter=False, Comment="", RbeModelName=None, EnableDynamicTrackingForVero=False, NewDoseSpecificationPointNames=[], NewDoseSpecificationPoints=[], MotionSynchronizationTechniqueSettings={ 'DisplayName': None, 'MotionSynchronizationSettings': None, 'RespiratoryIntervalTime': None, 'RespiratoryPhaseGatingDutyCycleTimePercentage': None, 'MotionSynchronizationTechniqueType': "Undefined" }, Custom=None, ToleranceTableLabel="IMRT")

  # CompositeAction ends 


with CompositeAction('Set prescription'):

  with CompositeAction('Add prescription dose references'):

    # CompositeAction ends 


  # Unscriptable Action 'Set prescription' Completed : SetPrescriptionCompositeAction(...)

  retval_1.SetAutoScaleToPrimaryPrescription(AutoScale=True)

  # CompositeAction ends 


# Unscriptable Action 'Save' Completed : SaveAction(...)

with CompositeAction('Add beam (1 g180, beam set: TB test)'):

  retval_2 = beam_set.CreateArcBeam(ArcStopGantryAngle=179, ArcRotationDirection="Clockwise", BeamQualityId="6", GimbalPanAngle=0, GimbalTiltAngle=0, IsocenterData={ 'Position': { 'x': -0.6915256, 'y': -0.375, 'z': 5.486103 }, 'NameOfIsocenterToRef': "", 'Name': "TB test 1", 'Color': "98, 184, 234" }, Name="1 g180", Description="", GantryAngle=180, CouchRotationAngle=0, CouchPitchAngle=0, CouchRollAngle=0, CollimatorAngle=45)

  retval_2.SetBolus(BolusName="")

  # CompositeAction ends 


retval_1.CopyAndReverseBeam(BeamName="1 g180")

with CompositeAction('Edit beam (1 g181, beam set: TB test)'):

  beam_set.Beams['1 g181'].Name = "2 g179"

  # CompositeAction ends 


case.PatientModel.CreateStructuresFromTemplate(SourceTemplate=root.TemplatePatientModels['TB Couch Clinical - Rails In'], SourceExaminationName="CT 1", SourceRoiNames=["CouchRailLeft_In", "CouchSurface", "CouchRailRight_In", "CouchInterior"], SourcePoiNames=["UserOrigin", "Marker 1", "Marker 2", "Sim Iso", "D1.5cm"], AssociateStructuresByName=True, TargetExamination=examination, InitializationOption="AlignImageCenters")

# Unscriptable Action '3D translation (CouchInterior)' Completed : SetPrimaryShapeAction(...)

# Unscriptable Action '3D translation (CouchRailLeft_In, CouchSurface, CouchRailRight_In, CouchInterior)' Completed : SetPrimaryShapeAction(...)

# Unscriptable Action '3D translation (CouchRailLeft_In, CouchSurface, CouchRailRight_In, CouchInterior)' Completed : SetPrimaryShapeAction(...)

# Unscriptable Action '3D translation (CouchRailLeft_In, CouchSurface, CouchRailRight_In, CouchInterior)' Completed : SetPrimaryShapeAction(...)

plan.PlanOptimizations[0].ApplyOptimizationTemplate(Template=root.TemplateTreatmentOptimizations['JH_delete'], AssociatedRoisAndPois={ 'PTV_ltn': "PTV_ltn", 'PTV_rtn': "PTV_rtn", 'PTVp': "PTVp", 'MDGTV': "MDGTV", 'zzFalloffHigh': "zzFalloffHigh", 'zzFallOffMid': "zzFallOffMid", 'zzRectumPost': "zzRectumPost", 'Bladder-GTVp': "Bladder-GTVp", 'zzFallOffLow': "zzFallOffLow", 'External': "External", 'Spc_Bowel': "Spc_Bowel", 'Rectum': "Rectum", 'PTV4500': "PTV4500" })

plan.TreatmentCourse.EvaluationSetup.ApplyClinicalGoalTemplate(Template=root.TemplateTreatmentOptimizations['JH IMRT Pelvis PRF'], AssociatedRoisAndPois={ 'PTV4500': "PTV4500", 'BowelBag': "Spc_Bowel", 'Rectum': "Rectum", 'Bladder - GTVp': "Bladder-GTVp", 'Lt Femoral': "Lt Femoral", 'Rt Femoral': "Rt Femoral" })

# Unscriptable Action 'Modify optimization settings' Completed : PersistOptimizationSettingsAction(...)

retval_1.SetAutoScaleToPrimaryPrescription(AutoScale=False)

with CompositeAction('Set default grid'):

  retval_1.SetDefaultDoseGrid(VoxelSize={ 'x': 0.25, 'y': 0.25, 'z': 0.25 })

  beam_set.FractionDose.UpdateDoseGridStructures()

  # CompositeAction ends 


plan.PlanOptimizations[0].RunOptimization(ScalingOfSoftMachineConstraints=None)

with CompositeAction('Apply image set properties'):

  examination.EquipmentInfo.SetImagingSystemReference(ImagingSystemName="CT Sim Hospital")

  # Unscriptable Action 'Set laser export reference point' Completed : SetLaserExportReferencePointAction(...)

  # CompositeAction ends 


plan.PlanOptimizations[0].RunOptimization(ScalingOfSoftMachineConstraints=None)

# Unscriptable Action 'Persist fine-tuning optimization settings' Completed : PersistFineTuningOptimizationSettingsAction(...)

plan.PlanOptimizations[0].RunFineTuningOptimization(ClinicalGoalsToExplore=[plan.TreatmentCourse.EvaluationSetup.EvaluationFunctions[0], plan.TreatmentCourse.EvaluationSetup.EvaluationFunctions[1]], ConservationRois=[case.PatientModel.RegionsOfInterest['PTV4500'], case.PatientModel.RegionsOfInterest['MDGTV'], case.PatientModel.RegionsOfInterest['PTVp'], case.PatientModel.RegionsOfInterest['PTV_ltn'], case.PatientModel.RegionsOfInterest['PTV_rtn'], case.PatientModel.RegionsOfInterest['Bladder-GTVp'], case.PatientModel.RegionsOfInterest['Rectum'], case.PatientModel.RegionsOfInterest['Spc_Bowel']], OptimizationSpecs=[RaySearch.CorePlatform.Presentation.Actions.CoreORBIT.FineTuningOptimizationUtils+OptimizationRunSpecs])
