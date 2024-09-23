from connect import *

import sys
sys.path.append("\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
sys.path.append("F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")

from FrontEnd.CopyablePopup import CopyablePopup
from PlanCheck.Functions.Functions import *



if __name__ == '__main__':
    
    isocenters = getAllIsocentersInBeamSet()
    msg = ''
    for i in isocenters:
        msg += calcShift(i, message=True)
    
    popup = CopyablePopup(title="Shift Calculator", message=msg)
    popup.showPopup()