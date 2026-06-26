# PatientQueryTool/main.py
from connect import *

import sys
sys.path.append(r"\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
sys.path.append(r"F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")

from PatientQueryTool.access.ray_repository import RayRepository
from PatientQueryTool.engine.executor import execute_physician_alias_query
from PatientQueryTool.engine.deep_executor import execute_deep_filters
from PatientQueryTool.engine.deep_filters.PlanFilters import HasPlanNameFilter
from PatientQueryTool.engine.deep_filters.HasRoiFilter import HasRoiFilter


def run():
    ray_repository = RayRepository()

    base_filter = {"BodySite": "Brain"}
    candidate_records = execute_physician_alias_query(
        ray_repository=ray_repository,
        base_filter=base_filter,
        physician_key="Carpenter",
        use_index_service=True,
        return_records=True,
    )

    print("Index candidates:", len(candidate_records))
    


    deep_filters = [
        HasPlanNameFilter(plan_name="Brain", approval=True),
        HasRoiFilter(roi_name="Brain"),
    ]

    mrns = execute_deep_filters(
        ray_repository=ray_repository,
        candidate_records=candidate_records,
        deep_filters=deep_filters,
        return_records=False,
    )

    print("Final matches:", len(mrns))
    for mrn in mrns:
        print(mrn)


run()