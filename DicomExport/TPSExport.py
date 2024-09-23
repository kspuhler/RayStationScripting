# -*- coding: utf-8 -*-
"""
Created on Thu Apr 11 10:21:20 2024

@author: spuhlk01
"""

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
from RSutil.variables import VARIAN_MACHINES, CYBERKNIFE_LI, CYBERKNIFE_NYC, RADIXACTS, RS_UTIL_ARIA_CONNECTION, RS_UTIL_PRECISION_CONNECTION_LI, RS_UTIL_PRECISION_CONNECTION_NYC
from FrontEnd.GenericPopup import GenericPopup


#Get filepath to export

fPathBaseRV   = '\\\Varimgwcdcpvm01\va_data$\Raystation'


class TPSExport(DicomExportBase):

    def __init__(self, fPathBase = fPathBaseRV):
        super().__init__(fPathBase)
        
    def assembleFilePath(self):
        self.exportPath = self.fPath
            
    def chooseDataToExport(self):
        self.beamSets    = [bs.BeamSetIdentifier() for bs in self.plan.BeamSets]
        
    def inferExportTarget(self):
        self.exportTarget = None
        
        for bs in self.plan.BeamSets:
            
            if not self.exportTarget:
                if bs.MachineReference['MachineName'] in VARIAN_MACHINES:
                    if self.plan.Review:
                        if self.plan.Review.ApprovalStatus == 'Approved':
                            w = GenericPopup(title='FAILURE', message='PLEASE DO NOT PUSH APPROVED PLANS TO ARIA!\n UNAPPROVE AND RE-RUN THE SCRIPT!')
                            w.showPopup()   
                            sys.exit(0)
                    self.exportTarget = 'ARIA'
                    self.connection = RS_UTIL_ARIA_CONNECTION
                elif bs.MachineReference['MachineName'] in RADIXACTS:
                    self.exportTarget = 'RAYGATEWAY'
                elif bs.MachineReference['MachineName'] in CYBERKNIFE_LI: 
                    self.exportTarget = 'N1000'
                    self.connection = RS_UTIL_PRECISION_CONNECTION_LI
                elif bs.MachineReference['MachineName'] in CYBERKNIFE_NYC: 
                    self.exportTarget = 'N1000'
                    self.connection = RS_UTIL_PRECISION_CONNECTION_NYC       
    
    def editPoiVisibility(self, boolean) -> None:
        poiNames = [x.Name for x in self.case.PatientModel.PointsOfInterest]
        for p in poiNames:
            self.patient.SetPoiVisibility(PoiName=p, IsVisible=boolean)
    
    def runExport(self) -> None:
        self.chooseDataToExport()
        self.inferExportTarget()
        self.editPoiVisibility(False)
        if self.exportTarget == 'ARIA':
            self.case.ScriptableDicomExport(Connection = self.connection, RtStructureSetsForExaminations  = [self.exam.Name],
                                     BeamSets = self.beamSets, Examinations = [self.exam.Name], PhysicalBeamSetDoseForBeamSets = self.beamSets,
                                     TreatmentBeamDrrImages = self.beamSets, SetupBeamDrrImages = self.beamSets, IgnorePreConditionWarnings = True)            
        elif  self.exportTarget == 'N1000':
            self.case.ScriptableDicomExport(Connection = self.connection, RtStructureSetsForExaminations  = [self.exam.Name],
                                     BeamSets = self.beamSets, Examinations = [self.exam.Name], PhysicalBeamSetDoseForBeamSets = self.beamSets,
                                     TreatmentBeamDrrImages = None, SetupBeamDrrImages = None, IgnorePreConditionWarnings = True, 
                                     RtRadiationsForBeamSets = self.beamSets, RtRadiationSetForBeamSets = self.beamSets)
            
        elif self.exportTarget == 'RAYGATEWAY': 
            for ii in self.beamSets:
                self.case.ScriptableDicomExport(RayGatewayTitle = 'Raygateway', RtStructureSetsForExaminations  = [self.exam.Name],
                                     BeamSets = [ii], Examinations = [self.exam.Name], PhysicalBeamSetDoseForBeamSets = [ii],
                                     TreatmentBeamDrrImages = [ii], SetupBeamDrrImages = [ii], IgnorePreConditionWarnings = True)
                
        self.editPoiVisibility(True)    



        
if __name__ == "__main__":
    tmp = TPSExport(fPathBaseRV)