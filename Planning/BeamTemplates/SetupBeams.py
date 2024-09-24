# -*- coding: utf-8 -*-
"""
Created on Thu Mar 14 14:08:40 2024

@author: spuhlk01
"""
from connect import *

class SetupBeams(object):
    
    def __init__(self, gantryAngles = None, beamSet = None):
        
        if not beamSet:
            self.beamSet = get_current("BeamSet")
        else:
            self.beamSet = beamSet
            
        if not gantryAngles:
            self.gantryAngles = [0, 90, 270]
        else:
            self.gantryAngles = gantryAngles()
            
            
        self.beamSet.UpdateSetupBeams(ResetSetupBeams = "TRUE", SetupBeamsGantryAngles = self.gantryAngles)
        
        for idx, ii in enumerate(self.gantryAngles):
            print(idx)
            print(ii)
            self.beamSet.PatientSetup.SetupBeams[idx].Name = "SETUP g" + str(ii) 
            self.beamSet.PatientSetup.SetupBeams[idx].Description = "SETUP g" + str(ii) 
        
        
if __name__ == '__main__':
    tmp = SetupBeams()