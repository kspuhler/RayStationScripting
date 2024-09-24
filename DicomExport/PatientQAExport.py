import os
from connect import *

from DicomExportBase import DicomExportBase


fPathBase   = '\\\Client\F$\SHARING\Radiation Oncology Physics\IMRT QA\\'


class PatientQAExport(DicomExportBase):

    def __init__(self, fPathBase):
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
    	self.case.ScriptableDicomExport(ExportFolderPath = self.exportPath, BeamSets = self.beamSets,   PhysicalBeamSetDoseForBeamSets = self.beamSets, IgnorePreConditionWarnings = True)

if __name__ == "__main__":
    tmp = PatientQAExport(fPathBase)

