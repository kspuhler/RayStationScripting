# -*- coding: utf-8 -*-
"""
Created on Sun Mar 10 14:16:30 2024

@author: spuhlk01
"""

import sys
import os
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io

# Custom imports
sys.path.insert(0, './Classes')
sys.path.insert(0, './util')
from Classes.ParserSpawner import ParserSpawner
from Classes.Machines import *
from Classes.Beam import *
from util.Functions import *

# Save the original standard output
oldStdOut = sys.stdout

Tk().withdraw()

baseDir = 'F:\\SHARING\\Radiation Oncology Physics\\Raystation Export Check\\'
rsDir = baseDir + 'Raystation'
outDir = baseDir + 'Output'

f1 = askopenfilename(initialdir=rsDir,
                     title="Please Choose RS Plan:",
                     filetypes=[("RP Dicom", "RP*")]) 

plan1 = ParserSpawner(f1)
plan1 = plan1.spawnParser(plan1.txMachine)

try:
    t = f'Selected plan was {plan1.dicom.RTPlanLabel}'
except:
    t = 'Please Choose Exported Plan:'

f2 = askopenfilename(initialdir=baseDir,
                     title=t,
                     filetypes=[("RP Dicom", "*dcm")]) 

plan2 = ParserSpawner(f2)
plan2 = plan2.spawnParser(plan2.txMachine)

outDir = outDir + '\\' + plan1.PID
outPdf = outDir + '\\' + plan1.dicom.RTPlanLabel + '.pdf'

if not os.path.exists(outDir):
    os.makedirs(outDir)

# Capture the standard output
output = io.StringIO()
sys.stdout = output


#Run comparison, this all happens in __eq__ overrides for the classes imported
plan1==plan2

# Restore the standard output
sys.stdout = oldStdOut

# Get the captured output
log_content = output.getvalue()

# Write the captured output to the PDF
c = canvas.Canvas(outPdf, pagesize=letter)
width, height = letter

lines = log_content.split('\n')
y = height - 40
for line in lines:
    if y < 40:  # Check if we need a new page
        c.showPage()
        y = height - 40
    c.drawString(40, y, line)
    y -= 15  # Move to the next line

c.save()
