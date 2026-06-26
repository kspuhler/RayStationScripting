import sys

sys.path.append("F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD\DicomExport")
sys.path.append("\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD\DicomExport")

from connect import *

from IntegrityExport import run_integrity_export
from ClearCalcExport import run_clearcalc_export


if __name__ == "__main__":
    run_integrity_export()
    run_clearcalc_export()