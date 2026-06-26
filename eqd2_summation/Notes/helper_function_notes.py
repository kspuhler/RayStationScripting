from connect import get_current

case = get_current('Case')


# Hybrid Deformable Registration - Correlation coefficient similarity measure
case.PatientModel.CreateHybridDeformableRegistrationGroup(
    RegistrationGroupName="HybridDefReg (3)", 
    ReferenceExaminationName="CT 2", 
    TargetExaminationNames=["MAR"], 
    ControllingRoiNames=["Brain", "Brainstem"], 
    ControllingPoiNames=[], 
    FocusRoiNames=["Brain", "Brainstem"], 
    AlgorithmSettings={ 
        'NumberOfResolutionLevels': 3, 
        'InitialResolution': { 'x': 0.5, 'y': 0.5, 'z': 0.5 }, 
        'FinalResolution': { 'x': 0.25, 'y': 0.25, 'z': 0.25 }, 
        'InitialGaussianSmoothingSigma': 2, 
        'FinalGaussianSmoothingSigma': 0.333333333333333, 
        'InitialGridRegularizationWeight': 400, 
        'FinalGridRegularizationWeight': 400, 
        'ControllingRoiWeight': 0.5, 
        'ControllingPoiWeight': 0.1, 
        'MaxNumberOfIterationsPerResolutionLevel': 1000, 
        'ImageSimilarityMeasure': "CorrelationCoefficient", 
        'DeformationStrategy': "Default", 
        'ConvergenceTolerance': 1E-05 
    }
)

# Hybrid Deformable Registration - Mutual Information similarity measure
case.PatientModel.CreateHybridDeformableRegistrationGroup(
    RegistrationGroupName="HybridDefReg (3)", 
    ReferenceExaminationName="CT 2", 
    TargetExaminationNames=["BRAIN - 3/31"], 
    ControllingRoiNames=["Brain", "Brainstem"], 
    ControllingPoiNames=[], 
    FocusRoiNames=["Brain", "Brainstem"], 
    AlgorithmSettings={ 
        'NumberOfResolutionLevels': 3, 
        'InitialResolution': { 'x': 0.5, 'y': 0.5, 'z': 0.5 }, 
        'FinalResolution': { 'x': 0.25, 'y': 0.25, 'z': 0.25 }, 
        'InitialGaussianSmoothingSigma': 2, 
        'FinalGaussianSmoothingSigma': 0.333333333333333, 
        'InitialGridRegularizationWeight': 2000, 
        'FinalGridRegularizationWeight': 2000, 
        'ControllingRoiWeight': 0.5, 
        'ControllingPoiWeight': 0.1, 
        'MaxNumberOfIterationsPerResolutionLevel': 1000, 
        'ImageSimilarityMeasure': "MutualInformation", 
        'DeformationStrategy': "Default", 
        'ConvergenceTolerance': 1E-05 
    }
)

# Hybrid Deformable Registration - Correlation coefficient similarity measure - 2 Deformations
case.PatientModel.CreateHybridDeformableRegistrationGroup(
    RegistrationGroupName="HybridDefReg (3)", 
    ReferenceExaminationName="CT 2", 
    TargetExaminationNames=["CT 1", "BRAIN - 3/31"], 
    ControllingRoiNames=[], 
    ControllingPoiNames=[], 
    FocusRoiNames=[], 
    AlgorithmSettings={ 
        'NumberOfResolutionLevels': 3, 
        'InitialResolution': { 'x': 0.5, 'y': 0.5, 'z': 0.5 }, 
        'FinalResolution': { 'x': 0.25, 'y': 0.25, 'z': 0.25 }, 
        'InitialGaussianSmoothingSigma': 2, 
        'FinalGaussianSmoothingSigma': 0.333333333333333, 
        'InitialGridRegularizationWeight': 400, 
        'FinalGridRegularizationWeight': 400, 
        'ControllingRoiWeight': 0.5, 
        'ControllingPoiWeight': 0.1, 
        'MaxNumberOfIterationsPerResolutionLevel': 1000, 
        'ImageSimilarityMeasure': "CorrelationCoefficient", 
        'DeformationStrategy': "Default", 
        'ConvergenceTolerance': 1E-05 
    }
)

# Calculate EQD2 dose
TreatmentPlans['Brain3000'].BeamSets['Brain3000'].CreateEQD2Dose(Priorities=[5], AlphaBetas=[3], Rois=[case.PatientModel.RegionsOfInterest['External']])

  TreatmentPlans['Brain3000'].BeamSets['Brain3000'].CreateEQD2Dose(Priorities=[5, 1], AlphaBetas=[3, 2], Rois=[case.PatientModel.RegionsOfInterest['External'], case.PatientModel.RegionsOfInterest['Brain']])

  TreatmentPlans['Brain_3000cGy'].BeamSets['Brain_3000cGy'].CreateEQD2Dose(Priorities=[5, 1], AlphaBetas=[3, 2], Rois=[case.PatientModel.RegionsOfInterest['External'], case.PatientModel.RegionsOfInterest['Brain']])

  beam_set.CreateEQD2Dose(Priorities=[5, 1, 2], AlphaBetas=[3, 2, 10], Rois=[case.PatientModel.RegionsOfInterest['External'], case.PatientModel.RegionsOfInterest['Brain'], case.PatientModel.RegionsOfInterest['GTV']])


# Deform dose
case.MapDose(FractionEvaluationIndex=0, DoseDistribution=case.TreatmentDelivery.FractionEvaluations[0].DoseOnExaminations[2].DoseEvaluations[0], StructureRegistration=case.StructureRegistrations['HybridDefReg2'], ReferenceDoseGrid=None)




#Fraction (Nominal) dose
case.TreatmentPlans['Brain3000'].BeamSets['Brain3000'].FractionDose

# Evaluation doses
dose_1 = case.TreatmentDelivery.FractionEvaluations[0].DoseOnExaminations[1].DoseEvaluations[0]

# Check for the type of evaluation dose
dose = patient.Cases[2].TreatmentDelivery.FractionEvaluations[0].DoseOnExaminations[0].DoseEvaluations[1]
if ONLY exist(dose.EQD2OfRois):
    # EQD2 dose
if ONLY exist(dose.OfDoseDistribution):
    # Deformed dose
if exist(dose.EQD2OfRois) and exist(dose.OfDoseDistribution)
    # Deformed and EQD2 dose
else:
    # SUm dose

# Generic Raystation provided evaluation dose summation
DOSE_NAME ='test'
FX_NR = 0
dose_1 = case.TreatmentDelivery.FractionEvaluations[0].DoseOnExaminations[1].DoseEvaluations[0]
dose_2 = case.TreatmentDelivery.FractionEvaluations[0].DoseOnExaminations[1].DoseEvaluations[1]
summed_dose = case.CreateSummedDose(DoseName=DOSE_NAME, FractionNumber=FX_NR, DoseDistributions=[dose_1, dose_2], Weights=[1, 1])

# Sum two nominal doses
retval_0 = case.CreateSummedDose(
    DoseName="Summed dose 1", 
    FractionNumber=0, 
    DoseDistributions=[TreatmentPlans['Brain3000'].BeamSets['Brain3000'].FractionDose, beam_set.FractionDose], 
    Weights=[1, 1]
)

# Sum two evaluation doses
retval_0 = case.CreateSummedDose(
    DoseName="Summed dose 1", 
    FractionNumber=0, 
    DoseDistributions=[case.TreatmentDelivery.FractionEvaluations[0].DoseOnExaminations[3].DoseEvaluations[0], 
                       case.TreatmentDelivery.FractionEvaluations[0].DoseOnExaminations[3].DoseEvaluations[1]
    ], 
    Weights=[1, 1]
)

# Sum a nominal and evaluation dose
retval_0 = case.CreateSummedDose(
    DoseName="ZZZDELETE", 
    FractionNumber=0, 
    DoseDistributions=[TreatmentPlans['Brain3000'].BeamSets['Brain3000'].FractionDose, case.TreatmentDelivery.FractionEvaluations[0].DoseOnExaminations[3].DoseEvaluations[6]], 
    Weights=[1, 1])


# Add new plan and beamset

  retval_0 = case.AddNewPlan(PlanName="SumPlan", PlannedBy="", Comment="", ExaminationName="CT 3", IsMedicalOncologyPlan=False, AllowDuplicateNames=False)

  retval_1 = retval_0.AddNewBeamSet(Name="SumPlan", ExaminationName="CT 3", MachineName="TrueBeamSN1106", Modality="Photons", TreatmentTechnique="VMAT", PatientPosition="HeadFirstSupine", NumberOfFractions=1, CreateSetupBeams=True, UseLocalizationPointAsSetupIsocenter=False, UseUserSelectedIsocenterSetupIsocenter=False, Comment="", RbeModelName=None, EnableDynamicTrackingForVero=False, NewDoseSpecificationPointNames=[], NewDoseSpecificationPoints=[], MotionSynchronizationTechniqueSettings={ 'DisplayName': None, 'MotionSynchronizationSettings': None, 'RespiratoryIntervalTime': None, 'RespiratoryPhaseGatingDutyCycleTimePercentage': None, 'MotionSynchronizationTechniqueType': "Undefined" }, Custom=None, ToleranceTableLabel="3D PLAN")

 

