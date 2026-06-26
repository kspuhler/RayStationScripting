import os
import sys
import glob
import pydicom as pdm

sys.path.append("F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
sys.path.append("\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")

try:
    from connect import *
except:
    pass


from Launcher.ScriptObject import ScriptObject
from DicomExport.DicomExportBase import DicomExportBase

class DicomIOManager(ScriptObject):
    
    def __init__(self):
        super().__init__(verboseExecution=False, runPreChecks=False, inferPhysician=False)
        self.activeCase = self.case
        self.importCase = self.case
        self.spcDirectoryParent = os.path.join("\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationSPC", self.patient.PatientID)
        self.spcDirectoryChildren = []
        
    
    def assemblePathsForDebug(self):
        self.spcDirectoryChildren = [ f.path for f in os.scandir(self.spcDirectoryParent) if f.is_dir() ]
        print(f'DEBUG: Path tree = {self.spcDirectoryChildren}')
    
    def makeSpcSubDirectories(self, caseNames):
        if not isinstance(caseNames, list):
            caseNames = [caseNames]
        for c in caseNames:
            check = os.path.join(self.spcDirectoryParent, case)
            if not os.path.exists(check):
                os.mkdir(check)
                

    def setActiveCase(self, caseNameToSetActive): 
        self.patient.Save()
        #Manages the case we are setting as active
        case = [c for c in self.patient.Cases if c.CaseName == caseNameToSetActive]
        print(f'DEBUG: Case: {case}')
        case[0].SetCurrent()
        self.activeCase = case[0]

    def pushSelectedData(self, guiManagerSelections):
        print(f'DEBUG: GUI Selection was {guiManagerSelections}')

        #Gets a dictionary from the VM of keys = Cases, vals = [list of tx plans to push]
        
        #Case level loop
        for caseID in guiManagerSelections.keys():
            print(f'DEBUG: Case: {caseID}')
            self.setActiveCase(caseID)
            #Makes the directory to push to and adds it to the list we will import from
            fPath = os.path.join(self.spcDirectoryParent, self.activeCase.CaseName)
            if not os.path.exists(fPath):
                os.makedirs(fPath)
            self.spcDirectoryChildren.append(fPath)
            #Assemble list of beamsets
            for planID in guiManagerSelections[caseID]:
                print(f'DEBUG: Plan {planID}')
                p = self.activeCase.TreatmentPlans[planID] #Reference to RS plan
                beamSetsToPush = [bs.BeamSetIdentifier() for bs in p.BeamSets]
                #Get CTs
                imagesToPush = []
                for bs in p.BeamSets:
                    ctName = bs.GetPlanningExamination()
                    if not ctName.Name in imagesToPush:
                        imagesToPush.append(ctName.Name)
                print(f'Pushing images: {imagesToPush} beamsets: {beamSetsToPush} from case {caseID} to folder {fPath}')
                self.activeCase.ScriptableDicomExport(ExportFolderPath = fPath,
                                                  Examinations = imagesToPush,
                                                  BeamSets = beamSetsToPush,   
                                                  PhysicalBeamSetDoseForBeamSets = beamSetsToPush,
                                                  RtStructureSetsForExaminations  = imagesToPush, 
                                                  IgnorePreConditionWarnings = True)

    
    def getUidsForImport(self, specifier = None , fdir=None):
        '''Grabs dicom files that fit specifier and returns unique UIDs'''
        
        print(f'DEBUG: Running UID scan for specifier {specifier}')
        if not fdir:
            fdir = os.getcwd()

        if not specifier in ["CT*dcm", "RP*dcm", "RS*dcm", "RD*dcm"]:
            raise Warning(f"You are running getUniqueDicomFiles() with an odd specifier of {specifier} and you should make sure this is intentional!")
        
        filesToParse = glob.glob(os.path.join(fdir, specifier))
        if not filesToParse:
            raise Warning(f"No files found for {specifier}") 
            return
        

        studyUIDs = []
        seriesUIDs = []
        
        
        
        for fname in filesToParse:
            f = pdm.read_file(fname)
            if not str(f.StudyInstanceUID) in studyUIDs:
                studyUIDs.append(str(f.StudyInstanceUID))
            if not str(f.SeriesInstanceUID) in seriesUIDs:
                seriesUIDs.append(str(f.SeriesInstanceUID))
        r = {'PatientID': str(self.patient.PatientID),   
                'StudyInstanceUID': [str(s) for s in studyUIDs], 
                'SeriesInstanceUID': [str(s) for s in seriesUIDs]}
        print(f'Returning value: {r}')
        return r
    
    def runImport(self, caseName=None):
        
        for fpath in self.spcDirectoryChildren:
            print(f'IMPORT Path = {fpath}')
            #Assemble function parameter for import
            ctParam   = self.getUidsForImport(specifier = "CT*dcm", fdir = fpath)
            #print(f"DEBUG CT param {ctParam}")
            planParam = self.getUidsForImport(specifier = "RP*dcm", fdir = fpath) 
            #print(f"DEBUG plan param {planParam}")
            doseParam = self.getUidsForImport(specifier = 'RD*dcm', fdir = fpath)
            #print(f"DEBUG dose param {doseParam}")
            structSetParam = self.getUidsForImport(specifier="RS*dcm", fdir = fpath)
            #print(f"DEBUG ss param {structSetParam}")
            print(f"DEBUG argument for import is {[ctParam, doseParam, planParam, structSetParam]}")
            w=self.patient.ImportDataFromPath(Path = fpath, CaseName=self.importCase.CaseName, SeriesOrInstances = [ctParam, doseParam, planParam, structSetParam])