import tkinter as tk
from tkinter import ttk

import sys
sys.path.append("\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
sys.path.append("F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")

from RSutil.variables import TRUEBEAMS, ACCURAY_MACHINES


from connect import *




class PlanSetupGui(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Plan Setup")
        self.geometry("500x300")

        # Example data
        self.planTemplates = ["Prostate", "Lung SBRT", "Whole Brain"]
        self.machines = ["TrueBeam", "CyberKnife", "Radixact"]

        self.machineOptions = {
            "TrueBeam": ["6MV", "10MV", "FFF"],
            "CyberKnife": ["Fixed Collimator", "Iris", "MLC"],
            "Radixact": ["Helical", "TomoDirect"]
        }

        # --- Plan template dropdown ---
        ttk.Label(self, text="Plan Template").pack(pady=(10,0))
        self.planVar = tk.StringVar(value=self.planTemplates[0])
        self.planDropdown = ttk.Combobox(self, textvariable=self.planVar, values=self.planTemplates, state="readonly")
        self.planDropdown.pack(pady=5)

        # --- Machine dropdown ---
        ttk.Label(self, text="Machine").pack(pady=(10,0))
        self.machineVar = tk.StringVar(value=self.machines[0])
        self.machineDropdown = ttk.Combobox(self, textvariable=self.machineVar, values=self.machines, state="readonly")
        self.machineDropdown.pack(pady=5)
        self.machineDropdown.bind("<<ComboboxSelected>>", self.updateOptions)

        # --- Options listbox ---
        ttk.Label(self, text="Options").pack(pady=(10,0))
        self.optionListbox = tk.Listbox(self, height=6, selectmode="multiple")
        self.optionListbox.pack(pady=5, fill="x", expand=True)

        # initialize listbox with default machine
        self.updateOptions()

    def updateOptions(self, event=None):
        machine = self.machineVar.get()
        options = self.machineOptions.get(machine, [])

        # Clear old options
        self.optionListbox.delete(0, tk.END)

        # Insert new ones
        for opt in options:
            self.optionListbox.insert(tk.END, opt)
            


if __name__ == "__main__":
    app = PlanSetupGui()
    app.mainloop()

