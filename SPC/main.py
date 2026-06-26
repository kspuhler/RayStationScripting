from connect import *

import os
import sys
sys.path.append("F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
sys.path.append("\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")

from SPC.Classes.GuiManager import GuiDataManager, SPCSelectionWindow
from SPC.Classes.DicomIOManager import DicomIOManager

try:
    from connect import *
except:
    pass




#Get some generic info we will need later on
pat  = get_current("Patient")
mrn  = pat.PatientID

dataExportDir = os.path.join(os.path.join("\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationSPC", mrn))
print(f'Exporting patient data to: {dataExportDir}')


app = SPCSelectionWindow()
app.mainloop()



   

