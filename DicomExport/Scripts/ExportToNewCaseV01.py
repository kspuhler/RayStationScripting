import os
import sys
import glob

import pydicom as pdm

import tkinter as tk
from tkinter import ttk


sys.path.append("F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
sys.path.append("\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")

try:
    from connect import *
except:
    pass


from Launcher.ScriptObject import ScriptObject
from FrontEnd.CopyablePopup import CopyablePopup
from DicomExport.DicomExportBase import DicomExportBase




class GuiDataManager(ScriptObject):
    #Handles user data selection in the DataSelectionWindow class
    def __init__(self):
        super().__init__(verboseExecution=False, runPreChecks=False, inferPhysician=False)
        self.assembleGuiData()  
        
    def assembleGuiData(self):
        self.guiData = {c.CaseName: [p.Name for p in c.TreatmentPlans] for c in self.patient.Cases if not 'spc' in c.CaseName.lower()}# if not c.CaseName == self.case.CaseName}
        print(f'DEBUG: assembleGuiData() returns: {self.guiData}')
    def updateSelections(self, column, selectedItems):
        """Store updated selections for each column in guiData."""
        self.guiData[column] = selectedItems



class DataSelectionWindow(tk.Toplevel):
    #Window visible to user, it will show columns of each case, along with every plan inside of that case
    #TODO: Selectable case for import
    def __init__(self):
        super().__init__()
        
        self.title("Select Plans To Export:")
        self.geometry("600x400")
        
        self.GuiDataManager = GuiDataManager()
        

        # Styling for a more modern look
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure("TLabel", background="#f0f0f0", foreground="#333", font=("Arial", 10))
        style.configure("TButton", background="#4CAF50", foreground="white", padding=6, relief="flat")
        style.configure("TListbox", background="white", padding=5, relief="flat")

        # Create columns based on the data from GuiDataManager
        self.createListboxes()
        
        # Add single "Run" button
        runButton = ttk.Button(self, text="Run", command=self.getExportDataAndExitGui)
        runButton.grid(row=2, column=0, columnspan=len(self.GuiDataManager.guiData) + 1, pady=20)



    def createListboxes(self):
        for col, (header, items) in enumerate(self.GuiDataManager.guiData.items()):
            label = ttk.Label(self, text=header, style="TLabel")
            label.grid(row=0, column=col, padx=10, pady=10)

            listbox = tk.Listbox(self, selectmode=tk.MULTIPLE, exportselection=False)
            listbox.grid(row=1, column=col, padx=10, pady=10)

            for item in items:
                listbox.insert(tk.END, item)
                listbox.selection_set(0, tk.END)

            listbox.bind("<<ListboxSelect>>", self.createSelectionHandler(header, listbox))

        # Add "Export To" column
        col = len(self.GuiDataManager.guiData)
        label = ttk.Label(self, text="Export To", style="TLabel")
        label.grid(row=0, column=col, padx=10, pady=10)

        self.exportToListbox = tk.Listbox(self, selectmode=tk.SINGLE, exportselection=False)
        self.exportToListbox.grid(row=1, column=col, padx=10, pady=10)

        for caseName in self.getCaseNames():
            self.exportToListbox.insert(tk.END, caseName)

        self.exportToListbox.selection_set(tk.END)  # Select "New Case" by default


    def getCaseNames(self):
        patient = get_current("Patient")
        caseNames = [case.CaseName for case in patient.Cases]
        caseNames.append("New Case")
        return caseNames


    def createSelectionHandler(self, col_header, listbox):
        def selectionHandler(event):
            selected_indices = listbox.curselection()
            selected_items = [listbox.get(i) for i in selected_indices]
            self.GuiDataManager.updateSelections(col_header, selected_items)
        return selectionHandler


    def getExportDataAndExitGui(self):
        tmp = self.GuiDataManager.guiData
        self.GuiDataManager.guiData = {k: v for k, v in tmp.items() if v}
        print(self.GuiDataManager.guiData)
        self.selectedExportIndex = self.exportToListbox.curselection()
        selected_indices = self.exportToListbox.curselection()
        if not selected_indices:
            print("No export target selected.")
            self.selectedExportTarget = None
        else:
            selected_case = self.exportToListbox.get(selected_indices[0])
            self.selectedExportTarget = None if selected_case == "New Case" else selected_case

        self.selectedExportData = self.GuiDataManager.guiData

        self.destroy()
        
        
class DataExportManager(object):
    
    def __init__(self, guiDataSelections = None):
        self.guiDataSelections = guiDataSelections
        
        self.BASE_EXPORT_DIRECTORY = "\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationSPC"
        self.constructExportDirectory()
        
        
    
    def constructExportDirectory(self):
        self.patient = get_current("Patient")
        self.exportDirectory = os.path.join(self.BASE_EXPORT_DIRECTORY, self.patient.PatientID)
        
        
    def setActiveCase(self, caseNameToSetActive): 
        self.patient.Save()
        #Manages the case we are setting as active
        case = [c for c in self.patient.Cases if c.CaseName == caseNameToSetActive]
        print(f'DEBUG: Case: {case}')
        case[0].SetCurrent()
        self.activeCase = case[0]

    def pushSelectedData(self):
        print(f'DEBUG: GUI Selection was {self.guiDataSelections}')
        self.exportDirectoryList = []
        #Gets a dictionary from the VM of keys = Cases, vals = [list of tx plans to push]
            
        #Case level loop
        for caseID in self.guiDataSelections.keys():
            print(f'DEBUG: Case: {caseID}')
            self.setActiveCase(caseID)
            #Makes the directory to push to and adds it to the list we will import from
            fPath = os.path.join(self.exportDirectory, caseID)
            self.exportDirectoryList.append(fPath)
            if not os.path.exists(fPath):
                os.makedirs(fPath)
            #Assemble list of beamsets
            for planID in self.guiDataSelections[caseID]:
                print(f'DEBUG: Plan {planID}')
                p = self.activeCase.TreatmentPlans[planID] #Reference to RS plan
                beamSetsToPush = [bs.BeamSetIdentifier() for bs in p.BeamSets if not "sim" in planID.lower()]
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

class DicomImportManager(object):
    
    def __init__(self, exportDirectoryList=None, importCase=None):
        self.importDirectoryList = exportDirectoryList
        self.importCase = importCase
        self.patient = get_current("Patient")
        self.runImports()
        
        
    # def setActiveCase(self, caseNameToSetActive): 
        
    #     self.patient.Save()
    #     #Manages the case we are setting as active
    #     case = [c for c in self.patient.Cases if c.CaseName == caseNameToSetActive]
    #     print(f'DEBUG: Case: {case}')
    #     case[0].SetCurrent()
    #     self.activeCase = case[0]
        
    def parseDirectoryForUniqueFiles(self, fPath, identifier="*dcm"):
        #Assembles assinine RS import paramenter for files starting with identifier
        foundStudyUIDs  = []
        foundSeriesUIDs = {} #this is what we are going to format and return return, it is a dictionaroy of {studyID1: [seriesID1,2,3....]}
        filesToParse = glob.glob(os.path.join(fPath, identifier))
        for file in filesToParse:
            f = pdm.read_file(file)
            print(f"Reading {file}")
            studyUid = str(f.StudyInstanceUID)
            seriesUid = str(f.SeriesInstanceUID)
            
            if not studyUid in foundStudyUIDs: #IF this is a brand new study id we need to update the return dictionary properly
                
                foundStudyUIDs.append(studyUid)
                foundSeriesUIDs[studyUid] = list(seriesUid)
            
            elif studyUid in foundSeriesUIDs: #now we will check if this is a new seriesID which is the fundamental issue with running the auto import
                if not seriesUid in foundSeriesUIDs[studyUid]:
                    foundSeriesUIDs[studyUid].append(seriesUid)
                    
        #Formatting the return now
        result = [
            {
                'PatientID': self.patient.PatientID,
                'StudyInstanceUID': study_uid,
                'SeriesInstanceUID': series_uid
            }
            for study_uid, series_list in foundSeriesUIDs.items()
            for series_uid in series_list
            ]
        return result
                
           
        
    
    def runImports(self):
        for fPath in self.importDirectoryList: #Looping over the F/.../MRN/Case level folders
            print(f'Parsing {fPath}')
            importArg = self.parseDirectoryForUniqueFiles(fPath)
            
            w=self.patient.ImportDataFromPath(Path = fPath, CaseName=self.importCase, 
                                              SeriesOrInstances = importArg)


if __name__ == "__main__":  
    root = tk.Tk()
    root.withdraw()  # Hide main window
    app = DataSelectionWindow()
    app.wait_window()
    
    Dem = DataExportManager(guiDataSelections=app.selectedExportData)
    Dem.pushSelectedData()
    
    Dim = DicomImportManager(exportDirectoryList=Dem.exportDirectoryList, importCase=app.selectedExportTarget)
    
    sys.exit()
