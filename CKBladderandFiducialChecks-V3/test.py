# -*- coding: utf-8 -*-
"""
Created on Thu Jun 19 13:40:39 2025

@author: santoj14
"""

import sys

sys.path.append("F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD\CKBladderandFiducialChecks-V3")
sys.path.append("\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD\CKBladderandFiducialChecks-V3")

from JustFiducialContouring import CKsimulation

f = CKsimulation()
f.createFiducialROI()
f.findFiducials()
f.deleteFiducialROI()
