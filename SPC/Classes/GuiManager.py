
import os
import sys
import traceback

import tkinter as tk
from tkinter import ttk


sys.path.append("F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
sys.path.append("\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")

try:
    from connect import *
except:
    pass


from Launcher.ScriptObject import ScriptObject
from SPC.Classes.DicomIOManager import DicomIOManager
from FrontEnd.CopyablePopup import CopyablePopup

class GuiDataManager(ScriptObject):

    def __init__(self):
        super().__init__(verboseExecution=False, runPreChecks=False, inferPhysician=False)
        self.assembleGuiData()  
        
    def assembleGuiData(self):
        self.guiData = {c.CaseName: [p.Name for p in c.TreatmentPlans] for c in self.patient.Cases if not 'spc' in c.CaseName.lower()}# if not c.CaseName == self.case.CaseName}
        print(f'DEBUG: assembleGuiData() returns: {self.guiData}')
        
    def updateSelections(self, column, selectedItems):
        """Store updated selections for each column in guiData."""
        self.guiData[column] = selectedItems



class SPCSelectionWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Select Plans To Export:")
        self.geometry("800x400")
        
        self.GuiDataManager = GuiDataManager()
        self.DicomIOManager = DicomIOManager()

        # Styling for a more modern look
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure("TLabel", background="#f0f0f0", foreground="#333", font=("Arial", 10))
        style.configure("TButton", background="#4CAF50", foreground="white", padding=6, relief="flat")
        style.configure("TListbox", background="white", padding=5, relief="flat")

        # Create columns based on the data from GuiDataManager
        self.createListboxes()
        
        # Add single "Run" button
        runButton = ttk.Button(self, text="Run", command=self.runExport)
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


    def runExport(self):
        
        selectedExportIndex = self.exportToListbox.curselection()
        if not selectedExportIndex:
            print("No export target selected.")
            return

        selectedExportTarget = self.exportToListbox.get(selectedExportIndex[0])
        print(f"Export target: {selectedExportTarget}")


        self.DicomIOManager.pushSelectedData(self.GuiDataManager.guiData)
        #self.DicomIOManager.assemblePathsForDebug()
        #self.DicomIOManager.runImport()
        self.destroy()




if __name__ == "__main__":
    
    app = SPCSelectionWindow()
    app.mainloop()
    popup = CopyablePopup(title="Copyable Popup", message="\\Client\F$\SHARING\Radiation Oncology Physics\RayStationSPC")
    popup.showPopup()