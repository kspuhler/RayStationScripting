# PatientQueryTool/engine/deep_executor.py
"""
PatientQueryTool - Deep Executor (v2)

Takes candidate patient records (from index pass), loads each patient, applies
one or more deep filters (AND), and returns the refined list of matches.

This module:
- owns per-patient exception isolation
- does NOT define clinical logic (that lives in deep_filters/)
"""

def execute_deep_filters(
    ray_repository,
    candidate_records,
    deep_filters,
    return_records=False,
    ):
    
    matched_records = []
    matched_mrns = []

    for record in candidate_records:
        mrn = ray_repository.extract_mrn(record)

        try:
            patient = ray_repository.load_patient_from_record(record)

            is_match = True
            for deep_filter in deep_filters:
                if not deep_filter.is_match(ray_repository, patient, record):
                    is_match = False
                    break

            if not is_match:
                continue

            if return_records:
                matched_records.append(record)
            else:
                if mrn:
                    matched_mrns.append(mrn)

        except Exception as e:
            # v2: do not die on one bad patient
            # later: replace with logging
            print("Deep filter error for PatientID {}: {}".format(mrn, e))
            continue

    return matched_records if return_records else matched_mrns