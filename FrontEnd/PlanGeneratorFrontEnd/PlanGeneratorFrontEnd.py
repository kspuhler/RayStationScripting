import tkinter as tk
from tkinter import ttk
import sys

sys.path.append("\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
sys.path.append("F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")

from RSutil.variables import ALL_MACHINES


class PlanGeneratorFrontEnd(tk.Tk):
    def __init__(self, allMachines, targets, parent=None):
        super().__init__()

        self.title("Plan Generator")
        self.geometry("450x350")

        # Adding sleek background
        self.configure(bg="#2c3e50")  # Dark blue background

        # Reference to PlanGenerator (optional for test mode)
        self.parent = parent

        # Dropdown (Combobox) for machine selection
        self.selectedMachine = tk.StringVar(value=allMachines[0])  # Default to the first machine

        # Dropdown (Combobox) for target selection
        self.selectedTarget = tk.StringVar(value=targets[0] if targets else None)  # Default to the first target or None

        # Entry fields for Rx, Coverage Level, Fractions, and Plan Name
        self.rxValue = tk.StringVar()
        self.coverageLevelValue = tk.StringVar(value="95")  # Default value set to 95
        self.fractionsValue = tk.StringVar()
        self.planNameValue = tk.StringVar()

        # Create a ttk style for labels, buttons, etc.
        self.style = ttk.Style()
        self.style.configure("TLabel", background="#2c3e50", foreground="#ecf0f1", font=("Helvetica", 12, "bold"))
        self.style.configure("TEntry", font=("Helvetica", 12))
        self.style.configure("TButton", font=("Helvetica", 12, "bold"), foreground="#2c3e50", background="#ecf0f1")

        self.createWidgets(allMachines, targets)

    def createWidgets(self, allMachines, targets):
        # Define padding
        padding = {"padx": 10, "pady": 10}

        # Frame for input fields
        inputFrame = ttk.Frame(self)
        inputFrame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Dropdown label for machine
        machineLabel = ttk.Label(inputFrame, text="Select Machine:")
        machineLabel.grid(row=0, column=0, **padding, sticky="W")

        # Dropdown (Combobox) for machines
        machineDropdown = ttk.Combobox(inputFrame, textvariable=self.selectedMachine, values=allMachines)
        machineDropdown.grid(row=0, column=1, **padding, sticky="EW")
        machineDropdown.state(["readonly"])  # Readonly to prevent manual typing

        # Target label
        targetLabel = ttk.Label(inputFrame, text="Select Target:")
        targetLabel.grid(row=1, column=0, **padding, sticky="W")

        # Target dropdown (Combobox)
        targetDropdown = ttk.Combobox(inputFrame, textvariable=self.selectedTarget, values=targets)
        targetDropdown.grid(row=1, column=1, **padding, sticky="EW")
        targetDropdown.state(["readonly"])  # Readonly to prevent manual typing

        # Rx label and entry field
        rxLabel = ttk.Label(inputFrame, text="Rx:")
        rxLabel.grid(row=2, column=0, **padding, sticky="W")

        rxEntry = ttk.Entry(inputFrame, textvariable=self.rxValue)
        rxEntry.grid(row=2, column=1, **padding, sticky="EW")

        # Coverage Level label and entry field
        coverageLevelLabel = ttk.Label(inputFrame, text="Coverage Level:")
        coverageLevelLabel.grid(row=2, column=2, **padding, sticky="W")

        coverageLevelEntry = ttk.Entry(inputFrame, textvariable=self.coverageLevelValue)
        coverageLevelEntry.grid(row=2, column=3, **padding, sticky="EW")

        # Fractions label and entry field
        fractionsLabel = ttk.Label(inputFrame, text="Fractions:")
        fractionsLabel.grid(row=3, column=0, **padding, sticky="W")

        fractionsEntry = ttk.Entry(inputFrame, textvariable=self.fractionsValue)
        fractionsEntry.grid(row=3, column=1, **padding, sticky="EW")

        # Plan Name label and entry field
        planNameLabel = ttk.Label(inputFrame, text="Plan Name:")
        planNameLabel.grid(row=4, column=0, **padding, sticky="W")

        planNameEntry = ttk.Entry(inputFrame, textvariable=self.planNameValue)
        planNameEntry.grid(row=4, column=1, **padding, sticky="EW")

        # Generate Plan button
        generateButton = ttk.Button(inputFrame, text="Generate Plan", command=self.submit)
        generateButton.grid(row=5, column=0, columnspan=4, pady=20)

        # Configure grid weights
        inputFrame.grid_columnconfigure(1, weight=1)
        inputFrame.grid_columnconfigure(3, weight=1)
        inputFrame.grid_rowconfigure(5, weight=1)  # Allow button to expand if needed

    def submit(self):
        # Get the selected machine, target, Rx, Coverage Level, Fractions, and Plan Name
        selectedMachine = self.selectedMachine.get()
        selectedTarget = self.selectedTarget.get()
        rx = self.rxValue.get() or None  # Default to None if empty
        coverageLevel = self.coverageLevelValue.get() or None  # Default to None if empty
        fractions = self.fractionsValue.get() or None  # Default to None if empty
        planName = self.planNameValue.get() or None  # Default to None if empty

        if self.parent:  # If PlanGenerator is present
            self.parent.setMachine(selectedMachine)
            self.parent.setRxAndCoverageLevel(rx, coverageLevel)
            self.parent.setFractions(fractions)
            self.parent.setPlanName(planName)
            self.parent.setTarget(selectedTarget)
        else:  # In test mode, print the values
            print(f"Test mode: Selected machine is {selectedMachine}, Target: {selectedTarget}, Rx: {rx}, Coverage Level: {coverageLevel}, Fractions: {fractions}, Plan Name: {planName}")

        # Close the window
        self.destroy()

# Test Mode: Run the window standalone for testing
if __name__ == "__main__":
    # Mock list of ALL_MACHINES and targets for testing
    TEST_MACHINES = ["Test Machine 1", "Test Machine 2", "Test Machine 3"]
    TEST_TARGETS = ["Target 1", "Target 2", "Target 3"]

    # Create the window without PlanGenerator, using test data
    app = PlanGeneratorFrontEnd(TEST_MACHINES, TEST_TARGETS)
    app.mainloop()