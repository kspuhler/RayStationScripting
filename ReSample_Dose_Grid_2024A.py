# RayStation 2023B-2024A (Python 3.8)
# Source = currently selected plan in UI
# Target = existing plan by name (first beam set)

from connect import *

TARGET_PLAN_NAME = "test"   # <-- change to your target plan's name
TARGET_BEAMSET_INDEX = 0       # use 0 (first) or change if needed

patient = get_current("Patient")
case    = get_current("Case")
source_plan = get_current("Plan")  # <- CURRENTLY SELECTED plan in the UI

# Get target plan + beam set
target_plan = next(p for p in case.TreatmentPlans if p.Name == TARGET_PLAN_NAME)
target_bs = target_plan.BeamSets[TARGET_BEAMSET_INDEX]

# Resample source Total Dose onto target plan's grid
resampled_dose = source_plan.TreatmentCourse.TotalDose.GetTransformedAndResampledDoseValues(
    DoseGrid=target_plan.GetTotalDoseGrid()
)

# Write resampled dose into target beam set FractionDose
target_bs.FractionDose.SetDoseValues(Dose=resampled_dose, CalculationInfo=target_plan.Name)

print(f"Resampled Total Dose from '{source_plan.Name}' -> '{target_plan.Name}' (BS index {TARGET_BEAMSET_INDEX}).")
