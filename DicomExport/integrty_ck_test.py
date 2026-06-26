import os
import sys
import tkinter as tk



sys.path.append("F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
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
        self.beamSetIds   = [bs.DicomPlanLabel for bs in self.plan.BeamSets]

    def runExport(self):
        self.chooseDataToExport()
        self.case.ScriptableDicomExport(ExportFolderPath = self.exportPath, BeamSets = self.beamSets, IgnorePreConditionWarnings = True)
            
            
class IntegrityExportCyberknife(IntegrityExport):
    
    def __init__(self, fPathBase = fPathBaseIntegrity):
        super().__init__(fPathBase)
        
    def runExport(self):
        self.chooseDataToExport()
    
        for idx, bs in enumerate(self.beamSets):
            push = os.path.join(self.exportPath, self.beamSetIds[idx])
            os.makedirs(push)
            print('here')
            print(self.beamSets)
            print(bs)
            self.case.ScriptableDicomExport(ExportFolderPath = push, BeamSets = [bs], IgnorePreConditionWarnings = True, RtRadiationsForBeamSets = [bs]) 
      


def ask_cyberknife_choice():
    """
    Opens a simple Tkinter window asking the user to choose Cyberknife
    or Not Cyberknife.

    Returns:
        str: "Cyberknife" or "Not Cyberknife"
    """
    choice = {"value": None}

    def choose(value):
        choice["value"] = value
        root.destroy()

    root = tk.Tk()
    root.title("Machine Type")
    root.geometry("300x140")
    root.resizable(False, False)

    label = tk.Label(root, text="Choose machine type:", font=("Segoe UI", 11))
    label.pack(pady=(20, 10))

    button_frame = tk.Frame(root)
    button_frame.pack(pady=10)

    cyberknife_button = tk.Button(
        button_frame,
        text="Cyberknife",
        width=14,
        command=lambda: choose("Cyberknife")
    )
    cyberknife_button.grid(row=0, column=0, padx=5)

    not_cyberknife_button = tk.Button(
        button_frame,
        text="Varian",
        width=14,
        command=lambda: choose("Varian")
    )
    not_cyberknife_button.grid(row=0, column=1, padx=5)

    root.mainloop()

    return choice["value"]



if __name__ == "__main__":
    machine_choice = ask_cyberknife_choice()
    if machine_choice == "Cyberknife":
        tmp = IntegrityExportCyberknife(fPathBaseIntegrity)
    elif machine_choice == "Varian":
        tmp = IntegrityExport(fPathBaseIntegrity)
    
    