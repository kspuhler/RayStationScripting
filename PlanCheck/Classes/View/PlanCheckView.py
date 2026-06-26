import sys
sys.path.append("F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
sys.path.append("\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")

import tkinter as tk
from tkinter import ttk, messagebox
from PlanCheck.Classes.VM.PlanCheckViewModel import PlanCheckViewModel

class PlanCheckApp:
    def __init__(self, master, planCheckViewModel):
        self.master = master
        self.master.title("Treatment Plan Checker")

        self.planCheckViewModel = planCheckViewModel
        self.setupUI()

    def setupUI(self):
        # Create the Notebook widget (tabbed interface)
        self.notebook = ttk.Notebook(self.master)
        self.notebook.pack(fill='both', expand=True)

        # Add the Plan tab
        self.planTab = ttk.Frame(self.notebook)
        self.notebook.add(self.planTab, text="Treatment Plan")
        self.setupPlanTab()

        # Add Beamset tabs
        self.addBeamsetTabs()

    def setupPlanTab(self):
        # Plan Status Label
        planStatusLabel = tk.Label(self.planTab, text=f"Plan Status: {self.planCheckViewModel.runPlanChecks()}", font=("Arial", 12))
        planStatusLabel.pack(pady=10)
    
        # ROI Alerts Label
        roiAlertsLabel = tk.Label(self.planTab, text="ROI Alerts:", font=("Arial", 12))
        roiAlertsLabel.pack(pady=5)
    
        # ROI alert info
        textParts = []
        roiAlertInfo = self.planCheckViewModel.getRoiAlerts()
        if roiAlertInfo:
            textParts.append("CIED Warnings:")
            textParts.extend(roiAlertInfo)
        else:
            textParts.append("No CIED warnings found")
    
        # Override info
        overrideInfo = self.planCheckViewModel.getRoiOverrides()
        if overrideInfo:
            textParts.append("\n")
            textParts.extend(overrideInfo)
        else:
            textParts.append("\nNo override info\n")
    
        # Label to display all combined info
        self.roiAlertsText = tk.Label(self.planTab, text="".join(textParts), font=("Arial", 10), justify=tk.LEFT)
        self.roiAlertsText.pack(pady=10)

    def addBeamsetTabs(self):
        # Add a tab for each beamset if there are multiple
        for idx, beamsetViewModel in enumerate(self.planCheckViewModel.getBeamsetViewModels()):
            beamsetTab = ttk.Frame(self.notebook)
            self.notebook.add(beamsetTab, text=f"BS: {beamsetViewModel.name}")

            # Add specific details for this beamset in its tab
            self.setupBeamsetTab(beamsetTab, beamsetViewModel)

    def setupBeamsetTab(self, tab, beamsetViewModel):
        # Add Beamset Name, Machine, and other info
        beamsetInfo = beamsetViewModel.getBeamsetInfo()

        beamsetLabel = tk.Label(tab, text=f"BeamSet: {beamsetViewModel.name}", font=("Arial", 14))
        beamsetLabel.pack(pady=10)

        machineLabel = tk.Label(tab, text=f"Machine: {beamsetViewModel.machine}", font=("Arial", 12))
        machineLabel.pack(pady=5)

        genericInfoLabel = tk.Label(tab, text=f"{beamsetViewModel.genericBeamSetCheckInfo}", font=("Arial", 12))
        genericInfoLabel.pack(pady=10)

        specificInfoLabel = tk.Label(tab, text=f"{beamsetViewModel.specificBeamSetCheckInfo}", font=("Arial", 12))
        specificInfoLabel.pack(pady=10)
        
        checkButton = tk.Button(tab, text="Run Checks", command=lambda: self.runChecksForBeamset(beamsetViewModel))
        checkButton.pack(pady=10)

    def runChecksForBeamset(self, beamsetViewModel):
        # Show check results in a messagebox for the specific beamset
        resultText = beamsetViewModel.runBeamsetCheck()
        messagebox.showinfo(f"BeamSet {beamsetViewModel.name} Check Results", resultText)


if __name__ == "__main__":
    from PlanCheck.Classes.Model.PlanCheckModel import PlanCheckModel
    # Create the PlanCheckModel instance with the treatment plan
    planCheckModel = PlanCheckModel()  # Automatically loads the plan and creates beamset models
    planCheckViewModel = PlanCheckViewModel(planCheckModel)

    root = tk.Tk()
    app = PlanCheckApp(root, planCheckViewModel)
    root.mainloop()
