import pydicom as pdm
import glob
import os

def getUniqueDicomFiles(specificer, fdir=None):

    if not fdir:
        fdir = os.getcwd()

    
    '''Grabs dicom files that fit specifier and returns unique UIDs'''
    
    for 