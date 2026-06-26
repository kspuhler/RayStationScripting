from connect import *

case = get_current("Case")
exam_name = get_current("Examination").Name

if not case.PatientModel.StructureSets[exam_name].RoiGeometries[38].HasContours():
	print("External does not have contours")
else:
	print("External has contours!")