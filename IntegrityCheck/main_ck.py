import sys
import os
import shutil
import glob
from pathlib import Path
from tkinter import Tk
from tkinter.filedialog import askopenfilename, askdirectory
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io
import pydicom as pdm

# Custom imports
sys.path.insert(0, './Classes')
sys.path.insert(0, './util')
from Classes.ParserSpawner import ParserSpawner
from util.Functions import *


def processDirectory(directory):
    '''strip the precision files out of their various /DCM folders into parent'''
    parent = Path(directory)
    
    for wildcard in ['rtplan*dcm', 'robot*dcm']:
        for f in parent.rglob(wildcard):
            if f.is_file() and f.parent != parent:
                shutil.move(str(f), str(parent / f.name))
                
    for subdir in parent.glob("DCM_*"):   # wildcard pattern
        if subdir.is_dir():
            shutil.rmtree(subdir)
            
################################################################################################

        
oldStdOut = sys.stdout
        



##################
####RAYSTATION####
##################

Tk().withdraw()

baseDir = 'F:\\SHARING\\Radiation Oncology Physics\\Raystation Export Check\\'
rsDir = baseDir + 'Raystation'
outDir = baseDir + 'Output'

f1 = askopenfilename(initialdir=rsDir,
                     title="Please Choose RS Plan:",
                     filetypes=[("RP Dicom", "RP*dcm")])

rs_plan = pdm.read_file(f1)
uid = rs_plan.FrameOfReferenceUID
rs_path = Path(f1).parent

rad_file_candidates = list(rs_path.glob('RTRAD*dcm'))

rs_rad = []

for f in rad_file_candidates:
    tmp = pdm.read_file(f)
    if tmp.FrameOfReferenceUID == uid:
        rs_rad.append(f)
    
    
rs_data = {'Plan': f1,
           'Rad': rs_rad}




###################
#####PRECISION#####
###################

precision_base_dir = baseDir + 'Precision'

precision_data_dir = askdirectory(title="Select Folder Containing Precision Dicoms",
                  initialdir = precision_base_dir)

processDirectory(precision_data_dir)

precision_data_dir = Path(precision_data_dir)

precision_data = {'Plan': None,
                  'Rad': []}

#Find plan with UID matching RS UID
for f in list(precision_data_dir.glob('rtplan*dcm')):
    tmp = pdm.read_file(f)
    if tmp.FrameOfReferenceUID == uid:
        precision_data['Plan'] = f
        
#Find matching rad files
for f in list(precision_data_dir.glob('robot*dcm')):
    tmp = pdm.read_file(f)
    if tmp.FrameOfReferenceUID == uid:
        precision_data['Rad'].append(f)
        

#########################
#######Read Files########
#########################

rs_data['Plan'] = ParserSpawner(rs_data['Plan'])
rs_data['Plan'] = rs_data['Plan'].spawnParser(rs_data['Plan'].txMachine)
rs_data['Rad'] = [ParserSpawner(x) for x in rs_data['Rad']]
rs_data['Rad'] = [x.spawnParser(x.txMachine) for x in rs_data['Rad']]


precision_data['Plan'] = ParserSpawner(precision_data['Plan'])
precision_data['Plan'] = precision_data['Plan'].spawnParser(precision_data['Plan'].txMachine)
precision_data['Rad']  = [ParserSpawner(x) for x in precision_data['Rad']]
precision_data['Rad']  = [x.spawnParser(x.txMachine) for x in precision_data['Rad']]

        
#########################
######TEGRIDY CHECK######
#########################

outDir = outDir + '\\' + rs_data['Plan'].PID
try:
    outPdf = outDir + '\\' + rs_data['Plan'].dicom.RTPlanLabel + '.pdf'
except:
    outPdf = outDir + '\\' + rs_data['Plan'].dicom.StudyDescription + '.pdf'
    
if not os.path.exists(outDir):
    os.makedirs(outDir)

# Capture the standard output
output = io.StringIO()
sys.stdout = output


#Run comparison, this all happens in __eq__ overrides for the classes imported
rs_data['Plan'] == precision_data['Plan']

for idx, rad in enumerate(rs_data['Rad']):
    rs_data['Rad'][idx] == precision_data['Rad'][idx]

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
