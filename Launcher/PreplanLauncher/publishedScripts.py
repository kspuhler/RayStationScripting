#Publish precontouring scripts here

import sys

sys.path.append("F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
sys.path.append("\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")


from Planning.PreplanScripts.CKProstate.CKProstatePrePlanContouring import CKProstatePrePlanContouring
from Planning.PreplanScripts.ProstateNodes4500.main import HaasProstateNodes4500

# Sample classes to choose from
class Alpha:
    def __init__(self):
        print("Alpha instance created!")

class Beta:
    def __init__(self):
        print("Beta instance created!")

class Gamma:
    def __init__(self):
        print("Gamma instance created!")

# Dictionary of user-friendly names to class references
sample = {
    "Option A (Alpha)": Alpha,
    "Option B (Beta)": Beta,
    "Option C (Gamma)": Gamma,
}

#publishedScripts = sample ###debug

publishedScripts = {"CK Prostate": CKProstatePrePlanContouring,
                    "JH Prostate 4500": HaasProstateNodes4500}