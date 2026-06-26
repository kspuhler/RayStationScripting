
try:
    from connect import *
except:
    pass
import tkinter as tk
import sys

sys.path.append("\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
sys.path.append("F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
from Launcher.ScriptObject import ScriptObject
from Planning.Structures.Functions.checkForContour import checkForContour


class ProtocolPrepScript(ScriptObject):
    
    INFORMATION = 'Test for __repr__ call'
    
    REQUIRED_OARS = ['testoar1', 'testoar2']
    REQUIRED_TARGETS = ['testTarg1', 'testTarg2']
    
    def __init__(self, runPreChecks=True, inferPhysician=True):
        # Always force verboseExecution to False
        print("Launching superclass protocolprep()")
        super().__init__(verboseExecution=False, runPreChecks=runPreChecks, inferPhysician=inferPhysician)

        self.makeTargets()
        print("KDS DEBUG!")
        self.makeOptStructures()
    
    def preChecks(self):
        self.missingOARs    = []
        self.missingTargets = []
        for r in self.REQUIRED_OARS:
            if not checkForContour(r):
                self.missingOARs.append(r)
        for r in self.REQUIRED_TARGETS:
            if not checkForContour(r):
                self.missingTargets.append(r)
        
            
    def makeOptStructures(self):
        pass
    
    def makeTargets(self):
        pass
    
    def processMissingOars(self):
        pass
        
    def processMissingTargets(self):
        pass
    
    @classmethod
    def getInfo(cls):
        out = ''
        if cls.INFORMATION:
            out+=cls.INFORMATION +'\n\n'
        if cls.REQUIRED_OARS:
            out+=f"**Script requires these OARs: {[x for x in cls.REQUIRED_OARS]}\n"
        if cls.REQUIRED_TARGETS:
            out+=f"**Script requires these Targets: {[x for x in cls.REQUIRED_TARGETS]}\n" 
        return out
    
if __name__=="__main__":
    a = ProtocolPrepScript()
    print(repr(a))
        
        
        
