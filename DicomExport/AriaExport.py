# -*- coding: utf-8 -*-
"""
Created on Tue Mar 19 12:04:15 2024

@author: spuhlk01
"""


import os
import sys

sys.path.append("F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
sys.path.append("\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")

try:
    from connect import *
except:
    pass

from DicomExport.DicomExportBase import DicomExportBase
#from RSUtil.variables import *


#Get filepath to export

fPathBaseRV   = '\\\Varimgwcdcpvm01\va_data$\Raystation'


class AriaExport(DicomExportBase):

    def __init__(self, fPathBase = fPathBaseRV):
        super().__init__(fPathBase)
        
    def assembleFilePath(self):
        self.exportPath = self.fPath
            
    def chooseDataToExport(self):
        self.beamSets    = [bs.BeamSetIdentifier() for bs in self.plan.BeamSets]
    
    def runExport(self):
    	self.chooseDataToExport()
    	self.case.ScriptableDicomExport(Connection = {'Node': '10.185.196.46', 'Port': 51408, 'CalledAE': 'VMSFSDRAYSTATION', 'CallingAE' : 'RAYSTATION_SSCP' }, RtStructureSetsForExaminations  = [self.exam.Name],
                                     BeamSets = self.beamSets, Examinations = [self.exam.Name], PhysicalBeamSetDoseForBeamSets = self.beamSets,
                                     TreatmentBeamDrrImages = self.beamSets, SetupBeamDrrImages = self.beamSets, IgnorePreConditionWarnings = True)



        
if __name__ == "__main__":
    tmp = AriaExport(fPathBase)