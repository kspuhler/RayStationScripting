#DO NOT EDIT


import sys
sys.path.append("\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
sys.path.append("F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")

import tkinter as tk

from Planning.Structures.Classes.AutoSegmentationTemplate import TamAbdomenTemplate, TamHeadAndNeckTemplate
from Planning.Structures.Templates.StructureTemplate import StructureTemplate
from Planning.Structures.Templates.roi_list_templates import tailor1A, tailor1B, tailor2A, tailor2B


class KarlDebugDNU(object):
    def __init__(self):
        pass

availableTemplates = {
    "Tam Head and Neck": TamHeadAndNeckTemplate,
    "Tam Abdomen": TamAbdomenTemplate,   
    "Tailor Protocols": None
            }

breastTailorTrial = {'Arm1A': StructureTemplate(tailor1A),
                     'Arm1B': StructureTemplate(tailor1B),
                     'Arm2A': StructureTemplate(tailor2A),
                     'Arm2B': StructureTemplate(tailor2B)
                    }