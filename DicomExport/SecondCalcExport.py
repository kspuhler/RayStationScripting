# -*- coding: utf-8 -*-
"""
Created on Tue Mar 19 11:20:37 2024

@author: spuhlk01
"""

import os
import sys

sys.path.append("F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD\DicomExport")
sys.path.append("\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD\DicomExport")

from connect import *

from DicomExportBase import DicomExportBase


#Get filepath to export

fPathBaseSecondCalc   = '\\\Client\F$\SHARING\Radiation Oncology Physics\Second MU Check DICOM export\\'


class SecondCalcExport(DicomExportBase):

    def __init__(self, fPathBase = fPathBaseSecondCalc):
        super().__init__(fPathBase)

    def assembleFilePath(self):
        self.exportPath = os.path.join(self.fPath, self.mrn)
        print(self.exportPath)
        if not os.path.exists(self.exportPath):
            os.makedirs(self.exportPath)
    
    def chooseDataToExport(self):
        self.beamSets    = [bs.BeamSetIdentifier() for bs in self.plan.BeamSets]

    def runExport(self):
    	self.chooseDataToExport()
    	self.case.ScriptableDicomExport(ExportFolderPath = self.exportPath, RtStructureSetsForExaminations  = [self.exam.Name],
                                     BeamSets = self.beamSets, IgnorePreConditionWarnings = True, ExportAsBdspDose = True)

if __name__ == "__main__":
    tmp = SecondCalcExport(fPathBaseSecondCalc)