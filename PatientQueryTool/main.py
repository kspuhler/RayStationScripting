# PatientQueryTool/main.py
import sys

sys.path.append(r"\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
sys.path.append(r"F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")

from PatientQueryTool.access.ray_repository import RayRepository
from PatientQueryTool.engine.executor import execute_physician_alias_query

try:
    from connect import *
except:
    pass


def run():
    ray_repository = RayRepository()

    base_filter   = {'Gender': 'Male'}      # add AND constraints here, e.g. {"Gender": "Female"}
    physician_key = "Haas"

    records = execute_physician_alias_query(
        ray_repository=ray_repository,
        base_filter=base_filter,
        physician_key=physician_key,
        use_index_service=True,
        return_records=True,
    )

    print("Matches:", len(records))
    # for record in records:
    #     print(record["PatientID"], record.get("Physician"), record.get("DisplayName"))
    ray_repository.patient_db.LoadPatient(PatientInfo=records[0])
    
run()
