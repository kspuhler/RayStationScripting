#DO NOT EDIT


import sys
sys.path.append("\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
sys.path.append("F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")


from Planning.Structures.Classes.AutoSegmentationTemplate import TamAbdomenTemplate, TamHeadAndNeckTemplate


availableTemplates = {
    "Tam Head and Neck": TamHeadAndNeckTemplate,
    "Tam Abdomen": TamAbdomenTemplate   
            }
