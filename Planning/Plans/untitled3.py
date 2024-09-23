# -*- coding: utf-8 -*-
"""
Created on Wed Sep 18 12:07:05 2024

@author: spuhlk01
"""

class PlanGenerator:
    def __init__(self):
        self.machine = None  # Placeholder for selected machine
        self.rx = None  # Placeholder for Rx value
        self.fractions = None  # Placeholder for Fractions value
        self.otherOptions = self.getOtherOptions()  # Populate options for second dropdown

    def getOtherOptions(self):
        # Example method to fetch options for the second dropdown
        return ["Option 1", "Option 2", "Option 3"]  # Replace with actual method to fetch options

    def launchWindow(self):
        # Launch the PlanGeneratorFrontEnd window with ALL_MACHINES and other options
        app = PlanGeneratorFrontEnd(ALL_MACHINES, self.otherOptions, self)
        app.mainloop()

    def setMachine(self, machine):
        # Set the machine selected from the window
        self.machine = machine
        print(f"Selected machine: {self.machine}")

    def setRxAndFractions(self, rx, fractions):
        # Set the Rx and Fractions values from the window
        self.rx = rx
        self.fractions = fractions
        print(f"Rx: {self.rx}, Fractions: {self.fractions}")

    def generatePlan(self):
        # Logic for generating plan
        if self.machine and self.rx and self.fractions:
            print(f"Generating plan for machine: {self.machine}, Rx: {self.rx}, Fractions: {self.fractions}")
        else:
            print("Missing input for plan generation")