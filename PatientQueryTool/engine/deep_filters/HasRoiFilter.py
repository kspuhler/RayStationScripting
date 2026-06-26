import sys

sys.path.append(r"\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
sys.path.append(r"F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")

from PatientQueryTool.engine.deep_filters.base import DeepFilterBase



class HasRoiFilter(DeepFilterBase):
    def __init__(self, roi_name):
        self.roi_name = roi_name

    def is_match(self, ray_repository, patient, patient_info_record):
        for case in patient.Cases:
            for examination in case.Examinations:
                ss = case.PatientModel.StructureSets[examination.Name]
                for roi_geom in ss.RoiGeometries:
                    if roi_geom.OfRoi.Name == self.roi_name:
                        return True
                        print('has roi!')
        return False
    
class HasSIBFilter(DeepFilterBase):
    def __init__(self):
        pass
    
    def is_match(self, ray_repository, patient, patient_info_record):
        pass