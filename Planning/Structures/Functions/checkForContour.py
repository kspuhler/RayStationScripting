# -*- coding: utf-8 -*-
"""
Created on Wed May  8 12:05:13 2024

@author: spuhlk01
"""

from connect import *
import sys
sys.path.append("\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
sys.path.append("F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")


def checkForContour(name, caseSensitive = False):
    case = get_current('Case')
    if not caseSensitive:
        name = name.lower()
        rois = [x.Name.lower() for x in case.PatientModel.RegionsOfInterest]
    
    elif caseSensitive == True:
        
        rois = [x.Name for x in case.PatientModel.RegionsOfInterest]
        print(name)
        print(rois)
    
    return name in rois
    
    