from connect import *
exam = get_current('Examination')

exam.RunDeepLearningSegmentationWithCustomRoiNames(ExaminationsAndRegistrations={exam.Name: None }, ModelAndRoiNames= {'RSL DLS Male Pelvic CT': {'Bladder': 'Bladder', 'Rectum': 'Anorectum'} })