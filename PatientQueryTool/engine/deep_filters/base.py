# PatientQueryTool/engine/deep_filters/base.py

class DeepFilterBase(object):
    """
    Deep filters run after a patient is loaded and can traverse cases/plans/etc.
    AND semantics are applied at the deep_executor level.
    """
    def is_match(self, ray_repository, patient, patient_info_record):
        raise NotImplementedError