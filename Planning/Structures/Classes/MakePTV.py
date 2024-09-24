# -*- coding: utf-8 -*-
"""
Created on Tue May 14 13:28:56 2024

@author: spuhlk01
"""

from connect import *

import tkinter as tk
import sys
sys.path.append("\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
sys.path.append("F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")

from Planning.Structures.Functions.checkForContour import checkForContour
from FrontEnd.GenericPopup import GenericPopup
from FrontEnd.CheckWithUserWindow import CheckWithUserWindowBoolean
from FrontEnd.DropdownMenuWindow import DropdownMenuWindow
from FrontEnd.MakePTVFrontEnd.MarginInputWindow import MarginInputWindow
from Launcher.ScriptObject import ScriptObject

class MakePTV(ScriptObject):
    '''
    MakePTV is a base class that other PTV scripts inherit from and should not generally be invoked at the user level.\nUsers: Please let Karl know if you're seeing this message in Raystation because you shouldn't be. 
     
    Dev: Provides a basic format for creating PTVs: loads case etc information in .getCurrent() and then provides a set of pre-checks, at base level only checks for external contour, generally overridden in subclasses
     
    '''
    
    def __init__(self, getMarginFromUser = False, margins = None, templates = None):
        
        self.getMarginFromUser = getMarginFromUser
        self.margins = margins      
        super().__init__()
        self.makePtv()
            
    def preChecks(self):
        
        if not checkForContour('external'):
            ext = self.pm.CreateRoi(Name="External", Color="Green", Type="External", TissueName="", RbeCellTypeName=None, RoiMaterial=None) ##TODO CHANGE BACK TO EXTERNAL
            ext.CreateExternalGeometry(Examination=self.exam, ThresholdLevel=-250)
    
        if self.getMarginFromUser:
            self.openMarginWindow()

        return
            
        
    def openMarginWindow(self):
        self.root = tk.Tk()
        self.root.withdraw()
        headers = list(self.margins.keys())

        MarginInputWindow(self.root, numColumns=len(headers), headers=headers, callback=self.handleMarginInput, templates=self.templates)
        
        
        #self.root.deiconify()  # Restore the window if it was minimized
        #self.root.lift()  # Bring the window to the top
        #self.root.attributes('-topmost', True)  # Set it as topmost
        self.root.focus_force()  # Force focus on the window

        
        self.root.mainloop()
        
    def formatMargins(self, marginDict):
        # Start with the required margin structure
        formattedMargins = {'Type': "Expand"}
    
        # Add the user-provided keys and their values
        for key in marginDict:
            formattedMargins[key] = marginDict[key]
    
        return formattedMargins
    
    def handleMarginInput(self, result):
        # Callback to handle the dictionary result
        self.margins = result
        print("Received margins:", self.margins)
    
        # Reformat margins for each part, accommodating arbitrary keys
        formattedMargins = {}
        for marginName, marginValues in self.margins.items():
            formattedMargins[marginName] = self.formatMargins(marginValues)
    
        print("Formatted margins:", formattedMargins)
    
        # Store the formatted margins for use in makePtv
        self.formattedMargins = formattedMargins
        if hasattr(self, 'root'):
            self.root.quit()  # Stop the mainloop
            self.root.destroy()  # Destroy the root window
    
    def makePtv(self):
        raise NotImplementedError
        
        
if __name__ == "__main__":
    tmp = MakePTV()
        


    





