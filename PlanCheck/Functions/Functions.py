# -*- coding: utf-8 -*-
"""
Created on Thu Jun 13 11:13:59 2024

@author: spuhlk01
"""

from connect import *
import numpy as np

sys.path.append("F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
sys.path.append("F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")

from FrontEnd.GenericPopup import GenericPopup

def getAllIsocentersInBeamSet(bs = None):
    '''Returns a list of isocenters
        Each isocenter has a property position and annotation (name)'''
    if not bs:
        try:
            bs = get_current('BeamSet')
        except:
            raise Exception("DEBUG: You do not have a beam set open!")
    isocenters = []
    isoNames = []
    for b in bs.Beams:
        if not b.Isocenter.Annotation.Name in isoNames:
            isoNames.append(b.Isocenter.Annotation.Name)
            isocenters.append(b.Isocenter)
    
    return isocenters
    

def isMultiIsoBeamSet(bs = None):
    '''Determine if a given beam set has multiple isocenters
    useful for other checking functions'''
       
    isocenters = getAllIsocentersInBeamSet(bs)
    if len(list(set(isocenters))) > 1:
        return True
    else:
        return False
    

def calcShift(isocenter, message = False, bs = None, exam = None, pm = None):
    '''Determine a shift for an isocenter
       $message=True will prepare a string for planner to copy
       $message=False will just return the calc'''
    if not bs:
        try:
            bs = get_current('BeamSet')
        except:
            raise Exception("DEBUG: You do not have a beam set open!")
    if not exam:
        try:
            exam = get_current('Examination')
        except:
            raise Exception("DEBUG: You do not have a primary CT open!")
    if not pm:
        try:
            case = get_current('Case')
            pm   = case.PatientModel
        except:
            raise Exception("DEBUG: Cannot load patient model!")
    
    lp = pm.StructureSets[exam.Name].LocalizationPoiGeometry.Point #localizationPoint xyz
    x  = isocenter.Position['x'] - lp['x']
    x  = round(x, 1)
    y  = isocenter.Position['y'] - lp['y']
    y  = round(y, 1)
    z  = isocenter.Position['z'] - lp['z']
    z  = round(z, 1)
    
    if not message: #return calculated points
        return x,y,z
    
    messageOut = f'Isocenter: {isocenter.Annotation.Name} \n'
    
    
    if x == 0:
        pass
    elif x > 0:
        lr = 'Left'
    elif x < 0:
        lr = 'Right'
    try:
        messageOut += f'{np.abs(x)}cm {lr}\n'
    except:
        pass
        

    if y == 0:
        pass
    elif y > 0:
        pa = 'Posterior'
    elif y < 0:
        pa = 'Anterior'
    try:
        messageOut += f'{np.abs(y)}cm {pa}\n'
    except:
        pass

    if z == 0:
        pass
    elif z > 0:
        si = 'Superior'
    elif z < 0:
        si = 'Inferior'
    try:
        messageOut += f'{np.abs(z)}cm {si}\n'
    except:
        pass
    
    return messageOut

        
