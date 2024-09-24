try:
    from connect import *
except:
    pass
import tkinter as tk
from tkinter import ttk

import sys
sys.path.append("\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
sys.path.append("F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")


from Planning.Structures.Classes.AutoSegmentationTemplate import TamAbdomenTemplate, TamHeadAndNeckTemplate
from FrontEnd.AutoContourTemplateFrontEnd.availableTemplates import availableTemplates

# Tkinter Frontend
class AutoContouringTemplateSelection:
    def __init__(self, root):
        self.root = root
        self.root.title("Select Template To Run")

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
        self.dropdown['values'] = list(availableTemplates.keys())
        self.dropdown.pack(padx=20, pady=10)

        # GO button with padding
        self.goButton = ttk.Button(root, text="GO", command=self.launchClass)
        self.goButton.pack(padx=20, pady=10)

        # Ensure window comes to front
        self.root.lift()
        self.root.focus_force()

    def launchClass(self):
        selectedKey = self.selectedOption.get()
        if selectedKey in availableTemplates:
            availableTemplates[selectedKey]()  # Instantiate the class
            self.goButton.config(state="disabled")  # Disable the button after click
            self.root.quit()  # Terminate the application after instantiation
        else:
            print("Please select a valid option.")

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

# Running the Tkinter application
if __name__ == "__main__":
    root = tk.Tk()
    app = AutoContouringTemplateSelection(root)
    root.mainloop()