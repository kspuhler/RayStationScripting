

# Script recorded 01 Oct 2024, 12:00:07

#   RayStation version: 14.0.0.3338
#   Selected patient: ...
try:
 from connect import *
except:
    pass

import tkinter as tk
import sys
sys.path.append("\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
sys.path.append("F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")

from Launcher.ScriptObject import ScriptObject
from FrontEnd.DropdownMenuWindow import DropdownMenuWindow


class CopyToNewExam(ScriptObject):
    '''Still in testing, please double check all results and let Karl know of issues \n
     This script will copy the ROIs and POIs from your PRIMARY exam to one of your choosing\n
    It will not copy external ROI\n
    Copying beamset is not yet implemented but will be soon\n
    ***Make sure you have correct primary exam selected!***'''
    
    def __init__(self,  runPreChecks=False):
        super().__init__(self, runPreChecks=runPreChecks)
        self.selectionDiaglogue()
        self.assembleRoiListToCopy()
        self.assemblePoiListToCopy()
        if len(self.roiListToCopy) > 0:
            self.copyRois()
        else:
            print("No ROIs to copy")
        if len(self.poiListToCopy) > 0:
            self.copyPois()
        else:
            print("No POIs to copy")
            
    def selectionDiaglogue(self):
        #Get all CT exam names other than the primary and then spawn a dropdown menu with their names
        allCtExams = [x.Name for x in self.case.Examinations if x.EquipmentInfo.Modality == 'CT' and x.Name != self.exam.Name] 
        root = tk.Tk()
        root.withdraw()
        w = DropdownMenuWindow(root, items = allCtExams, title=f"Primary exam is {self.exam.Name}", label = f"Primary exam is {self.exam.Name}\n Select exam to copy onto:")      
        root.wait_window(w)  # Wait for the dropdown window to close
        
        self.targetExam = w.get_selected_items()
        print("Selected Items:", self.targetExam)
    
    def assembleRoiListToCopy(self):
        self.roiListToCopy = []
        for s in self.pm.StructureSets[self.exam.Name].RoiGeometries:
            if s.OfRoi.Type != "External" and s.HasContours(): #get rid of external and anything that isn't actually contoured
                self.roiListToCopy.append(s.OfRoi.Name)
        print(f"DEBUG: ROIs to be copied: {self.roiListToCopy}")
                
    def copyRois(self):
        self.pm.CopyRoiGeometries(SourceExamination=self.exam, TargetExaminationNames=[self.targetExam], 
                                  RoiNames=self.roiListToCopy, ImageRegistrationNames=[], TargetExaminationNamesToSkipAddedReg=[self.targetExam])

    def assemblePoiListToCopy(self):
        self.poiListToCopy = []
        for p in self.pm.StructureSets[self.exam.Name].PoiGeometries:
            if p.Point:
                self.poiListToCopy.append(p.OfPoi.Name)
    
    def copyPois(self):
        #This works by making a tiny sphere ROI around each POI in the primary exam, then copying that ROI to 
        #selected exam, and then setting the POI's coordinates to those of the copied mock structure
        #Then it deletes the sphere ROI entirely
        for p in self.poiListToCopy:
            
            xyzSource = self.pm.StructureSets[self.exam.Name].PoiGeometries[p].Point
            
            
            roiName = "zzCopyPoi_" + p
            mockRoi = self.pm.CreateRoi(Name=roiName, Color="Yellow", Type="Control", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)
            mockRoi.CreateSphereGeometry(Radius=0.5, Examination=self.exam, Center=xyzSource, Representation="TriangleMesh", VoxelSize=None)
            self.pm.CopyRoiGeometries(SourceExamination=self.exam, TargetExaminationNames=[self.targetExam], 
                                      RoiNames=[roiName], ImageRegistrationNames=[], TargetExaminationNamesToSkipAddedReg=[self.targetExam])
            
            #Get centroid of copied mock roi
            xyzTarget = self.pm.StructureSets[self.targetExam].RoiGeometries[roiName].GetCenterOfRoi()
            #Place point on target
            self.pm.StructureSets[self.targetExam].PoiGeometries[p].Point = xyzTarget
            #Delete mock roi
            self.pm.RegionsOfInterest[roiName].DeleteRoi()
            

#class CopyBeamSet

    
    
if __name__ == "__main__":
    CopyToNewExam()
        