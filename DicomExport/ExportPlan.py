# -*- coding: utf-8 -*-
"""
Created on Wed Mar 27 13:09:41 2024

@author: spuhlk01

this script will identify the correct rv export (Aria/Precision) and push accordingly

it will also push integrity and second calc checks
"""


import os
import sys

sys.path.append("F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD\\")
sys.path.append("\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD\\")

try:
    from connect import *
except ModuleNotFoundError:
    pass

from DicomExport.DicomExportBase import DicomExportBase
from DicomExport.SecondCalcExport import SecondCalcExport
from DicomExport.IntegrityExport import IntegrityExport
from DicomExport.AriaExport import AriaExport

from RSutil.variables import RS_UTIL_ARIA_CONNECTION
 



#Get filepath to export

fPathBase   = '\\\Varimgwcdcpvm01\va_data$\Raystation'


        
if __name__ == "__main__":
    IntegrityExport()
    SecondCalcExport()
    AriaExport()
    