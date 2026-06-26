try:
    from connect import *
except:
    pass
import tkinter as tk
from tkinter import ttk

import sys
sys.path.append("\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
sys.path.append("F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")

from Planning.Structures.Templates.StructureTemplate import StructureTemplate
from Planning.Structures.Classes.AutoSegmentationTemplate import AutoSegmentationTemplate,TamAbdomenTemplate, TamHeadAndNeckTemplate
from FrontEnd.AutoContourTemplateFrontEnd.availableTemplates import availableTemplates, breastTailorTrial

# Tkinter Frontend
class AutoContouringTemplateSelection:
    def __init__(self, root, title = "Select AutoContouring Template", templates = availableTemplates):
        self.root = root
        self.root.title(title)
        self.templates = templates
        # Set modern window appearance
        self.root.configure(bg="#34495e")  # Dark slate gray background

        # Create a style for ttk widgets
        self.style = ttk.Style()
        self.style.configure("TLabel", background="#34495e", foreground="#ecf0f1", font=("Arial", 12))
        self.style.configure("TButton", background="#2980b9", foreground="white", font=("Arial", 12), padding=10)
        self.style.map("TButton", background=[("active", "#3498db")])  # Button hover effect
        self.style.configure("TCombobox", fieldbackground="#2c3e50", foreground="white", padding=5)

        # Center window on the screen
        self.centerWindow()

        # Dropdown menu label
        self.label = ttk.Label(root, text="Choose Template:")
        self.label.pack(pady=(10, 5))

        # Dropdown menu with padding
        self.selectedOption = tk.StringVar()
        self.dropdown = ttk.Combobox(root, textvariable=self.selectedOption)
        self.dropdown['values'] = list(self.templates.keys())
        self.dropdown.pack(padx=20, pady=10)

        # GO button with padding
        self.goButton = ttk.Button(root, text="GO", command=self.launchClass)
        self.goButton.pack(padx=20, pady=10)

        # Ensure window comes to front
        self.root.lift()
        self.root.focus_force()

    def launchClass(self):
        selectedKey = self.selectedOption.get()
        if not selectedKey:
            messagebox.showwarning("Selection Error", "Please select a template from the dropdown.")
            return
        
        # Check if the selected template triggers the laterality window with new templates
        if selectedKey == "Tailor Protocols":  # Replace with the actual key of the special template
            self.spawnLateralityWindow(newTemplates=breastTailorTrial)
        elif selectedKey in self.templates:
            # Instead of calling the template directly, check its type
            template = self.templates[selectedKey]
            print('memmmmi')
            # Here, you handle the template based on what kind of object it is
            if issubclass(template, AutoSegmentationTemplate):
                # If it's a class, instantiate it
                print(f"Instantiating template class: {selectedKey}")
                template()  # Instantiate the class
            elif issubclass(template, StructureTemplate):
                # Handle other cases if the template is not a class (e.g., instance of a class or other objects)
                print(f"Handling template object: {selectedKey}")
                # Add logic to handle non-callable template objects here
                template.make_empty_rois()
            self.goButton.config(state="disabled")  # Disable the GO button after click
            self.root.quit()  # Close the application
        else:
            print("Please select a valid option.")
            
    def spawnLateralityWindow(self, newTemplates):
        """Spawns a new window with laterality options for a specific template and a new set of templates."""
        # Destroy the original window before spawning the new one
        self.root.destroy()  
        
        # Create a new Tk root window instead of Toplevel
        newWindow = tk.Tk()
        
        # Spawn the laterality window with the new templates
        lateralityWindow = AutoContouringTemplateWithLaterality(newWindow, title="Select New Template with Laterality", templates=newTemplates)
        
        # Start the new laterality window event loop
        newWindow.mainloop()


    def centerWindow(self):
        """Centers the window on the screen."""
        self.root.update_idletasks()
        screenWidth = self.root.winfo_screenwidth()
        screenHeight = self.root.winfo_screenheight()
        windowWidth = 400  # Set wider window size
        windowHeight = self.root.winfo_reqheight()

        positionRight = int(screenWidth / 2 - windowWidth / 2)
        positionDown = int(screenHeight / 2 - windowHeight / 2)

        # Set the geometry of the window with a specified width
        self.root.geometry(f"{windowWidth}x{windowHeight}+{positionRight}+{positionDown}")
        
        
class AutoContouringTemplateWithLaterality(AutoContouringTemplateSelection):
    def __init__(self, root, title="Select AutoContouring Template", templates=availableTemplates):
        # Initialize the parent class
        super().__init__(root, title, templates)

        # Add Left/Right radiobuttons for laterality
        self.lateralityVar = tk.StringVar(value="None")  # Variable to store selected laterality

        self.radioFrame = ttk.Frame(self.root)
        self.radioFrame.pack(pady=10)

        self.leftRadio = ttk.Radiobutton(self.radioFrame, text="Left", variable=self.lateralityVar, value="Left", command=self.checkLateralitySelection)
        self.leftRadio.pack(side="left", padx=5)

        self.rightRadio = ttk.Radiobutton(self.radioFrame, text="Right", variable=self.lateralityVar, value="Right", command=self.checkLateralitySelection)
        self.rightRadio.pack(side="right", padx=5)

        # Initially disable the GO button until Left or Right is selected
        self.goButton.config(state="disabled")

    def checkLateralitySelection(self):
        """Maps 'Left' to 'L' and 'Right' to 'R', and enables the GO button."""
        laterality = self.lateralityVar.get()
    
        if laterality == "Left":
            self.lateralityVar.set("L")  # Set as "L" for Left
        elif laterality == "Right":
            self.lateralityVar.set("R")  # Set as "R" for Right
    
        if laterality != "None":
            self.goButton.config(state="normal")  # Enable GO button when Left/Right is selected
        else:
            self.goButton.config(state="disabled")  # Disab
            
    def launchClass(self):
        super().launchClass()
        pm = get_current("Case")
        pm = pm.PatientModel
        for ii in pm.RegionsOfInterest:
            if ii.Name[-1] == '_':
                ii.Name += self.lateralityVar.get()

        self.root.destroy()

# Running the Tkinter application
if __name__ == "__main__":
    root = tk.Tk()
    app = AutoContouringTemplateSelection(root)
    root.mainloop()