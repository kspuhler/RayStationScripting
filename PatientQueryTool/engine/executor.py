# PatientQueryTool/engine/executor.py
"""
PatientQueryTool - Index Executor (v1)

Builds one or more RayStation Filter dicts (fan-out for alias OR),
executes index queries via RayRepository, and returns either:
- raw patient info records (dicts), deduped by MRN, or
- MRN list only
"""

from PatientQueryTool.config.alias import PHYSICIAN_ALIAS


def expand_physician_alias(physician_key):
    return PHYSICIAN_ALIAS.get(physician_key, [physician_key])


def build_physician_alias_filter_dicts(base_filter, physician_key):
    filter_dicts = []

    for alias_token in expand_physician_alias(physician_key):
        filter_dict = dict(base_filter)
        filter_dict["Physician"] = alias_token
        filter_dicts.append(filter_dict)

    return filter_dicts


def execute_index_queries_to_records(ray_repository, filter_dicts, use_index_service=True):
    """
    Execute one or more index queries and return raw patient info records,
    deduped by MRN (PatientID). If duplicates occur, the first seen wins.
    """
    mrn_to_record = {}

    for filter_dict in filter_dicts:
        records = ray_repository.query_patient_info(filter_dict, use_index_service=use_index_service)

        for record in records:
            mrn = ray_repository.extract_mrn(record)
            if not mrn:
                continue

            if mrn not in mrn_to_record:
                mrn_to_record[mrn] = record

    # Return records in sorted MRN order for deterministic output
    return [mrn_to_record[mrn] for mrn in sorted(mrn_to_record.keys())]


def execute_index_queries_to_mrns(ray_repository, filter_dicts, use_index_service=True):
    """
    Execute one or more index queries and return sorted, deduped MRNs.
    """
    mrn_set = set()

    for filter_dict in filter_dicts:
        mrn_set |= ray_repository.query_mrns(filter_dict, use_index_service=use_index_service)

    return sorted(mrn_set)


def execute_physician_alias_query(ray_repository, base_filter, physician_key, use_index_service=True, return_records=False):
    """
    Convenience wrapper for:
      base_filter AND (Physician matches any alias token)

    If return_records=True, returns raw patient info dict records (deduped by MRN).
    Otherwise returns MRNs only.
    """
    filter_dicts = build_physician_alias_filter_dicts(base_filter, physician_key)

    if return_records:
        return execute_index_queries_to_records(ray_repository, filter_dicts, use_index_service=use_index_service)

    return execute_index_queries_to_mrns(ray_repository, filter_dicts, use_index_service=use_index_service)
