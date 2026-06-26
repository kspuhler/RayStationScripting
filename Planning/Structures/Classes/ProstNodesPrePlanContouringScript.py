
try:
    from connect import *
except:
    pass

import tkinter as tk
import sys
sys.path.append("\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
sys.path.append("F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")

from Planning.Structures.Classes.MakePTVProstateEBRT import MakePTVProstateEBRT
from Planning.Structures.Classes.MakeProstateNodesOars import MakeProstateNodesOars

if __name__=="__main__":
    MakePTVProstateEBRT()
    MakeProstateNodesOars()