"""
Export data for Clear Calc 2nd Check software.

JPS 3/14/2025
"""

import os
import sys

sys.path.append("F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD\DicomExport")
sys.path.append("\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD\DicomExport")

from connect import *

from DicomExportBase import DicomExportBase


#Get filepath to export

fPathBaseSecondCalc   = '\\\Client\F$\SHARING\Radiation Oncology Physics\Second MU Check DICOM export\\'


class ClearCalcExport(DicomExportBase):
    """A class that contains all the tidbits for an automatic export for use with Clear Calc.
    
    Just modified the original
    """       
         
    def __init__(self, fPathBase = fPathBaseSecondCalc):
        super().__init__(fPathBase)

    def assembleFilePath(self):
        """Put a filepath together."""
        self.exportPath = os.path.join(self.fPath, self.mrn+"_ClearCalc")
        print(self.exportPath)
        if not os.path.exists(self.exportPath):
            os.makedirs(self.exportPath)
    
    def chooseDataToExport(self):
        """Choose all the data to export."""
        self.beamSets    = [bs.BeamSetIdentifier() for bs in self.plan.BeamSets]

    def runExport(self):
        """Run the native export method in RS."""
        self.chooseDataToExport()
        try:
            
            self.case.ScriptableDicomExport(ExportFolderPath = self.exportPath,
                                        Examinations = [self.exam.Name],
                                        RtStructureSetsForExaminations  = None,
                                        RtStructureSetsReferencedFromBeamSets  = self.beamSets,
                                        BeamSets = self.beamSets, 
                                        PhysicalBeamSetDoseForBeamSets = self.beamSets,
                                        IgnorePreConditionWarnings = True, 
                                        ExportAsBdspDose = True,
                                        RtRadiationsForBeamSets = self.beamSets, 
                                        RtRadiationSetForBeamSets = self.beamSets)
            print('CK Pushed!')
        except:
            self.case.ScriptableDicomExport(ExportFolderPath = self.exportPath,
                                        Examinations = [self.exam.Name],
                                        RtStructureSetsForExaminations  = [self.exam.Name],
                                        BeamSets = self.beamSets, 
                                        PhysicalBeamSetDoseForBeamSets = self.beamSets,
                                        IgnorePreConditionWarnings = True, 
                                        ExportAsBdspDose = True)
            
def run_clearcalc_export():
    tmp = ClearCalcExport()


if __name__ == "__main__":
    tmp = ClearCalcExport(fPathBaseSecondCalc)