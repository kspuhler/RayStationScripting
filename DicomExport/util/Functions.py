# -*- coding: utf-8 -*-
"""
Created on Sun Mar 10 14:38:40 2024

@author: spuhlk01
"""

import pydicom as pdm
import os

def renameDicomToPlanName(fpath):
    
    ds    = pdm.read_file(fpath)
    fname =  ds.RTPlanLabel
    newName = 'RP.'+fname+'.dcm'
    os.rename(fname, newName)
    