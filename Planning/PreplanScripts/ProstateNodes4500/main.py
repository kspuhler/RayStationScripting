try:
    from connect import *
except:
    pass

#from tkinter import tk
from tkinter import messagebox
import sys
sys.path.append("\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
sys.path.append("F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")

from Launcher.ProtocolPrepScript import ProtocolPrepScript
from Planning.PreplanScripts.ProstateNodes4500.Classes.MakePTVProstateEBRT import MakePTVProstateEBRT
from Planning.PreplanScripts.ProstateNodes4500.Classes.MakeProstateNodesOars import MakeProstateNodesOars




class HaasProstateNodes4500(ProtocolPrepScript):
     
    INFORMATION ='This script will create structures needed to do a Haas 180*25 prostate+nodes plan \n It would be followed by one of the protocols named JH Prostate+Nodes 180*25'
    
    REQUIRED_OARS    = ["Bladder", "Rectum", "Bowel"]
    REQUIRED_TARGETS = ["MDGTV", "LtNode", "RtNode"]
    
    def __init__(self):
        super().__init__()
        
    def preChecks(self):
        super().preChecks()
        #override to do SIB expansions too
        
    def processMissingOars(self):
        pass
        
    def processMissingTargets(self):
        pass
            
    
    def makeOptStructures(self):
        tmp = MakeProstateNodesOars()
        del(tmp)
        return
        
    def makeTargets(self):
        tmp = MakePTVProstateEBRT()
        del(tmp)
        return

if __name__ == "__main__":
    a = HaasProstateNodes4500()