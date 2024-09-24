from connect import *
import sys
import tkinter as tk

sys.path.append("\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
sys.path.append("F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")

from Planning.Structures.Functions.checkForContour import checkForContour
from FrontEnd.GenericPopup import GenericPopup
from FrontEnd.DropdownMenuWindow import DropdownMenuWindow


def tryDefaultRoiName(roiName, needsGeometry = False, fallback = False):
    
    '''Checks contours in patient model for a given roiName, returns it if it exists
    
    needsGeometry: specifies if the ROI needs to be contoured already
    fallback: True will prompt user to select an ROI if it does not exist in patient model
    
    '''
    case = get_current("Case")
    pm   = case.PatientModel
    exam = get_current("Examination")
    
    searchingForRoi = True #controls while loop
    selectedRoi     = None #Return Value
    
    if not isinstance(roiName, list):
        roiName = [roiName]  
    
    for ii in roiName: #Checks patient model for roiName and returns first one it finds
        if checkForContour(ii, caseSensitive=False):
            if needsGeometry:
                print(f"DEBUG: {ii}")

                if pm.StructureSets[exam.Name].RoiGeometries[ii].HasContours():
                    selectedRoi = ii
                    return selectedRoi
                else:
                    continue #go to next iteration because ROi is not contoured TODO specify more behavior if needed
            
            elif not needsGeometry:
                selectedRoi = ii
                return selectedRoi
            
    if not fallback: #function will have exited by now if acceptable ROI was found
        w = GenericPopup(title="Failed to find necessary ROI!", message = f"Failed to find an ROI with name: {roiName} \n Script will now exit!")
        w.showPopup()
        sys.exit()
        
    elif fallback:
        items = []
        
        for ii in pm.StructureSets[exam.Name].RoiGeometries:
            if needsGeometry:
                if ii.HasContours():
                    items.append(ii.OfRoi.Name)
            else:
                items.append(ii.OfRoi.Name)
        
        root = tk.Tk()
        root.withdraw()  # Hide the root window
        
        w = DropdownMenuWindow(root, items, allow_multiple=False, title="Unable To Find ROI", label="Unable to find ROI\nPlease Select ROI to search:")
        w.grab_set()  # Make sure the dropdown window grabs focus
        root.wait_window(w)  # Wait for the dropdown window to close
        
        selectedRoi = w.get_selected_items()
        
        return selectedRoi 