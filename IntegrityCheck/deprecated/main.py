import sys
import os
sys.path.insert(0, './Classes')
sys.path.insert(0, './util')
oldStdOut = sys.stdout


from tkinter import Tk
from tkinter.filedialog import askopenfilename

from Classes.ParserSpawner import ParserSpawner
from Classes.Machines import *
from Classes.Beam import *

from util.Functions import *

#Tk().withdraw() 

#baseDir = 'F:\SHARING\Radiation Oncology Physics\Raystation Export Check\\'''
#rsDir = baseDir + 'Raystation'


#f1 = askopenfilename(initialdir= rsDir,
#                     title= "Please Choose RS Plan:",
#                     filetypes=[("RP Dicom", "RP*")]) 


#if False:
#    logPath = os.path.join(os.path.dirname(f1), 'check.log')
#    logger= open(logPath, "w")
#    sys.stdout = logger


#plan1 = ParserSpawner(f1)
#plan1 = plan1.spawnParser(plan1.txMachine)




#f2 = askopenfilename(initialdir = baseDir,
#                     title = "Please Choose Exported Plan:",
#                     filetypes=[("RP Dicom", "RP*")]) 


#plan2 = ParserSpawner(f2)
#plan2 = plan2.spawnParser(plan2.txMachine)

#print(plan1 == plan2)

    
    
    
pwd = os.getcwd()
os.chdir('F:\SHARING\Radiation Oncology Physics\Raystation Export Check\Raystation\\WUH19761976\\')
f1 = ParserSpawner('RP1.2.752.243.1.1.20240306140005700.8000.73704.dcm')
f1 = f1.spawnParser(f1.txMachine)
os.chdir('F:\SHARING\Radiation Oncology Physics\Raystation Export Check\Aria\\WUH19761976\\')
f2 = ParserSpawner('RP.WUH19761976.3D-RS-TEST.dcm')
f2 = f2.spawnParser(f2.txMachine)


os.chdir(pwd)


#logger= open('killme.log', "w")
#sys.stdout = logger

if f1 == f2:
    print('INTEGRITY CHECK PASSES')
else:
    print('INTEGRITY CHECK FAILS')