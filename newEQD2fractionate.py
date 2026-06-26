import numpy as np
from connect import *
import tkinter as tk
from tkinter import simpledialog

# Create a simple GUI window to ask for the number of fractions
root = tk.Tk()
root.withdraw()  # Hide the root window

# Ask user for the number of fractions using a simple dialog
fxns = simpledialog.askinteger("Total Fractions", "Enter the total number of fractions:", minvalue=1)

# Check if the input is valid
if fxns is None:
    print("No input provided. Exiting script.")
else:
    beam_set = get_current('BeamSet')
    
    # Access dose values and modify them based on the user input
    dd = beam_set.FractionDose.DoseValues.DoseData
    dd_flat = np.divide(dd, fxns).flatten()
    beam_set.FractionDose.SetDoseValues(Dose=dd_flat, CalculationInfo="Setting dose to fraction from plan")

    print(f"Dose distribution updated for {fxns} fractions.")