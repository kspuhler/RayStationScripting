# -*- coding: utf-8 -*-
"""
Created on Wed Feb 26 15:56:17 2025

@author: spuhlk01
"""

from datetime import datetime

from connect import *

class BeamSetCheckModel(object):
    
    def __init__(self, beamSet):
        
        self.genericBeamSetCheckResults = '' #Stuff that we always check
        self.specificBeamSetCheckResults = '' #Stuff specific to different machiens and stuff
        
        self.case = get_current("Case")
        self.rois = self.case.PatientModel.RegionsOfInterest
        self.beamSet = beamSet
        self.type = self.beamSet.DeliveryTechnique
        self.exam = self.beamSet.GetPlanningExamination()
        
        
        self.runGenericBeamSetChecks()
        #print(self.genericBeamSetCheckResults)
        self.runSpecificBeamSetChecks()
        
    def runGenericBeamSetChecks(self):
        self.getPrescription()
        self.displayRx()
        self.runSimCheck()
        self.doseGridChecks()
        

    def runSpecificBeamSetChecks(self):
        raise NotImplementedError
    
    ############################################################    
    #############Actual Checks Implemented Below!###############
    ############################################################
    
    def doseGridChecks(self):
        self.doseGrid = self.beamSet.FractionDose.InDoseGrid
        tmp = self.doseGrid.VoxelSize
        if not tmp['x'] == tmp['y'] == tmp['z']:
            self.genericBeamSetCheckResults += f'**WARNING: Anisotropic Dose Grid: x: {tmp["x"]}, y: {tmp["y"]}, z: P{tmp["z"]} \n'
        if any(v >0.13  for v in [tmp['x'], tmp['y'], tmp['z']]) and self.checkIfStereotactic():

            self.genericBeamSetCheckResults += "**WARNING: Dose grid size larger than 1.2mm and plan appears to be SRS/SBRT \n"
        
    def checkIfStereotactic(self):
        #This wil make an assumption about whether or not a plan is stereotactic
        
        if any(x in self.beamSet.DicomPlanLabel.lower() for x in ['srs', 'sbrt']): #The beamset having srs/sbrt in its name is a likely giveaway
            print(self.beamSet.DicomPlanLabel.lower())
            return True
        
        if self.beamSet.FractionationPattern.NumberOfFractions <= 5:
            return True
        return False
            
    def runCollisionCheck(self):
        raise NotImplementedError
    
    def runSupportStructureCheck(self):
        raise NotImplementedError
    
    def runSimCheck(self):
        #Flag a CT if it is more than 2 weeks old
        ctDate = self.exam.GetExaminationDateTime()
        
        d = ctDate.Day
        m = ctDate.Month
        y = ctDate.Year
        
        now    = datetime.now()
        ctDate = datetime(y, m, d)
        
        diff = (now - ctDate).days
        
        if diff > 14:
            self.genericBeamSetCheckResults += '**WARNING: Planning CT is more than two weeks old. \n'
                    
        if 'fb' in self.exam.Name.lower():
            self.genericBeamSetCheckResults += "**WARNING: Plan was done on free-breathing CT. \n"
            
        return
        
    def getPrescription(self):
        tmp = self.beamSet.Prescription.PrescriptionDoseReferences[0]
        self.rxType = tmp.PrescriptionType
        #if self.rxType == 'DoseAtVolume':
        if True:   
            self.rx = {'Target': tmp.OnStructure.Name,
                   'Dose': tmp.DoseValue,
                   'Volume': tmp.DoseVolume,
                   'Fractions':self.beamSet.FractionationPattern.NumberOfFractions}
        
        #elif self.rxType == 'DoseAtPoint':
            
        #    self.rx = {'Target': tmp.OnStructure.Name}
           
        #Handling for other types namely handcalcs TODO!!!
        else:
                print(f'Cannot process Rx of type: {tmp.PrescriptionType}')
                return 
            
    def displayRx(self):
        if hasattr(self, "rx"):# and self.rxType == 'DoseAtVolume':
            self.genericBeamSetCheckResults += f'Beamset Rx: {self.rx["Dose"]}cGy in {self.rx["Fractions"]} fx to target {self.rx["Target"]}\n'
        else:
            self.genericBeamSetCheckResults += 'Cannot Process Rx presumably due to point rx, will implement soon.\n'

        
        