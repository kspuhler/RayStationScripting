# -*- coding: utf-8 -*-
"""
Created on Sun Mar 10 14:16:30 2024

@author: spuhlk01
"""

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

Tk().withdraw() 

baseDir = 'F:\SHARING\Radiation Oncology Physics\Raystation Export Check\\'''
rsDir = baseDir + 'Raystation'
outDir = baseDir + 'Output'

f1 = askopenfilename(initialdir= rsDir,
                     title= "Please Choose RS Plan:",
                     filetypes=[("RP Dicom", "RP*")]) 




plan1 = ParserSpawner(f1)
plan1 = plan1.spawnParser(plan1.txMachine)



try:
    t = f'Selected plan was {plan1.dicom.RTPlanLabel}'
    
except:
    t = 'Please Coose Exported Plan:'

f2 = askopenfilename(initialdir = baseDir,
                     title = t,
                     filetypes=[("RP Dicom", "*dcm")]) 


plan2 = ParserSpawner(f2)
plan2 = plan2.spawnParser(plan2.txMachine)

outDir = outDir + '\\' + plan1.PID
outLog = outDir + '\\' + plan1.dicom.RTPlanLabel +'.log'

if not os.path.exists(outDir):
    os.makedirs(outDir)

logger= open(outLog, "w")
sys.stdout = logger

plan1 == plan2
logger.close()

sys.stdout = oldStdOut