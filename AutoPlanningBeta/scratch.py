# Script recorded 19 Feb 2026, 14:33:39

#   RayStation version: 14.0.0.3338
#   Selected patient: ...

from connect import *

plan = get_current("Plan")
db = get_current("PatientDB")

template = db.LoadTemplateClinicalGoals(templateName = 'TC Lung 200x30 PRF', lockMode = "Read")



plan.TreatmentCourse.EvaluationSetup.ApplyClinicalGoalTemplate(Template=template) #AssociatedRoisAndPois={ 'PTV6000': "", 'SpinalCord': "SpinalCord", 'Cord+5mm': "", 'Lungs': "Lungs", 'Esophagus': "Esophagus", 'Heart': "Heart", 'Brachial Plex_R': "", 'Brachial Plex_L': "" })
