try:
    from connect import *
except:
    pass


import os
import sys


#current_folder = os.path.dirname(os.path.abspath(__file__))
#parent_folder = os.path.dirname(current_folder)
#parent_folder = os.path.dirname(parent_folder)


#sys.path.append(parent_folder)

sys.path.append("\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
sys.path.append("F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")

from Planning.Structures.Templates.roi_list_templates import prostNodes4500
from Planning.Structures.Templates import StructureTemplate
from Sim.Templates.SimTemplate import SimTemplate
from Sim.Templates.Isocenters import Isocenters
from Sim.Templates.Pelvis import Pelvis, ProstateCK
from Sim.Templates.Breast import Breast
from Sim.Templates.HeadAndNeck import HeadAndNeck
from Sim.Templates.OpposedLats import OpposedLats
from Sim.Templates.BreastBilateral import BreastBilateral


import tkinter as tk
from tkinter.ttk import Combobox, Button
from tkinter import simpledialog

from datetime import datetime




def makeTemplate(selection, root):
    
    now = datetime.now()
    now = now.strftime('%m-%d-%y')
    pname = 'SIM' + now
    
    if selection == "Single Iso":
        tmp = Isocenters(numberOfIsocenters=1, planName = pname, beamSetName = 'SIM')
        
    elif selection == "Multi Iso":
        numIso = simpledialog.askinteger("", "How Many Isocenters?")
        tmp = Isocenters(numberOfIsocenters=numIso, planName = pname, beamSetName = 'SIM')
        
    elif selection == "Lt Breast Tangents":
        tmp = Breast(2, 'left', pname, 'SIM')
        
    elif selection == "Lt Breast 3 Field": 
        tmp = Breast(3, 'left', pname, 'SIM')
        
    elif selection == "Lt Breast 4 Field":
        tmp = Breast(4, 'left', pname, 'SIM')
        
    elif selection == "Rt Breast Tangents":
        tmp = Breast(2, 'right', pname, 'SIM')

    elif selection == "Rt Breast 3 Field": 
        tmp = Breast(3, 'right', pname, 'SIM')
        
    elif selection == "Rt Breast 4 Field":
        tmp = Breast(4, 'right', pname, 'SIM')
        
    elif selection == "Bilateral Breast":
        tmp = BreastBilateral(pname, 'SIM')
    
    elif selection == "Pelvis":
        tmp = Pelvis(1, pname, 'SIM')
        
    elif selection == "Prostate CK":
        tmp = ProstateCK(1, pname, 'SIM')
        
    elif selection == "Head and Neck":
        tmp = HeadAndNeck(1, pname, 'SIM')

    elif selection == "Opposed Lats":
        numIso = simpledialog.askinteger("", "How Many Isocenters?")
        tmp = OpposedLats(numberOfIsocenters=numIso, planName = pname, beamSetName = 'SIM')
        
    root.destroy()
    return
    

# Create the main window
root = tk.Tk()
root.title("Select a template:")

selection = tk.StringVar()

# Create a dropdown menu
options  = ["Single Iso", "Multi Iso", "Opposed Lats",
             "Pelvis", "Prostate CK", "Head and Neck",
            "Lt Breast Tangents", "Lt Breast 3 Field", "Lt Breast 4 Field", 
            "Rt Breast Tangents", "Rt Breast 3 Field", "Rt Breast 4 Field",
            "Bilateral Breast"]

comboBox = Combobox(root, state="readonly", values=options)
comboBox.pack()

button   = Button(root, text="Generate Plan", command = lambda: makeTemplate(options[comboBox.current()], root))
button.pack()


root.mainloop()

