import os
import sys


sys.path.append("F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD\DicomExport")
sys.path.append("\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD\DicomExport")

from connect import *

from DicomExportBase import DicomExportBase


#Get filepath to export

fPathBaseIntegrity   = '\\\Client\F$\SHARING\Radiation Oncology Physics\Raystation Export Check\Raystation\\'


class IntegrityExport(DicomExportBase):

    def __init__(self, fPathBase = fPathBaseIntegrity):
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
        try:
            self.case.ScriptableDicomExport(ExportFolderPath = self.exportPath, BeamSets = self.beamSets, IgnorePreConditionWarnings = True, RtRadiationsForBeamSets = self.beamSets) 
  
        except:     
            self.case.ScriptableDicomExport(ExportFolderPath = self.exportPath, BeamSets = self.beamSets, IgnorePreConditionWarnings = True)
        

if __name__ == "__main__":
    tmp = IntegrityExport(fPathBaseIntegrity)