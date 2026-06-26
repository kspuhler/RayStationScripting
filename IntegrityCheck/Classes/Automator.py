import os
import pydicom as pdm
import glob
from ParserSpawner import VarianParser, CyberKnifePlanParser


class Automator(object):
    '''Tries to automatically find the corresponding dicom file for integrity check'''
    
    def __init__(self, Parser = None):
        
        returnDir = os.getcwd()
        self.planNameToMatch = Parser.dicom.RTPlanLabel
        
        if isinstance(Parser, VarianParser):
            checkDir = 'F:\\SHARING\\Radiation Oncology Physics\\Raystation Export Check\\Aria\\'
            checkPrefix = "RP*"
        elif isinstance(Parser, CyberKnifeParser):
            checkDir = 'F:\\SHARING\\Radiation Oncology Physics\\Raystation Export Check\\CK\\'
            checkPrefix = "RT*"
        else: 
            print("Cannot determine parser type")
            self.found = False
            return 
        
        checkDir = os.path.join(checkDir, Parser.PID)
        self.findMatch(checkDir, checkPrefix)
        
        
    def findMatch(self, checkDir, checkPrefix):    
        try:
            os.chdir(checkDir)
        except FileNotFoundError as e:
            print(f''''
                  ***ERROR: Directory {checkDir} not found. \n
                  This probably means you did not export from ARIA/Precision.\n
                  You can do so now without relaunching the program.***''')
        for f in glob.glob(checkPrefix):
            d = pdm.read_file(f)
            if d.RTPlanLabel == self.planNameToMatch:
                self.found = os.path.join(checkDir, f)
                return
            else:
                continue
        self.found = False
        return
                
            
        

        
            