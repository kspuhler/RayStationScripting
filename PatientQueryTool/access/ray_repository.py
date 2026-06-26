# PatientQueryTool/access/ray_repository.py
"""
PatientQueryTool - Access Layer (RayStation Repository)

Wraps RayStation PatientDB.QueryPatientInfo(...) and provides helpers to:
- return raw patient info records (dicts)
- extract MRN-equivalent identifier (PatientID)
"""

from connect import *


class RayRepository(object):
    def __init__(self):
        self.patient_db = get_current("PatientDB")

    def query_patient_info(self, filter_dict, use_index_service=True):
        return self.patient_db.QueryPatientInfo(Filter=filter_dict, UseIndexService=use_index_service)

    def extract_mrn(self, patient_info_record):
        return patient_info_record.get("PatientID")

    def query_mrns(self, filter_dict, use_index_service=True):
        mrn_set = set()

        for record in self.query_patient_info(filter_dict, use_index_service):
            mrn = self.extract_mrn(record)
            if mrn:
                mrn_set.add(mrn)
        return mrn_set
    
    def load_patient_from_record(self, patient_info_record):
        #Load a patient from the query+patient_info record
        self.patient_db.LoadPatient(PatientInfo=patient_info_record)
        return get_current("Patient")
