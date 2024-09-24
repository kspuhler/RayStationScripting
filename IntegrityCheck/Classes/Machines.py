# -*- coding: utf-8 -*-
"""
Created on Wed Jan 10 15:58:12 2024

Handles parsing on a machine level basis

@author: spuhlk01
"""

from Beam import *

class MachineParserBase(object):
    '''Generic parser, just implements constructor '''
    NUM_MLC   = None
    
    
    def __init__(self, dicom):
        self.beams = []
        
        
        self.getPatientDemographics(dicom)
        self.getBeamSequence(dicom)
        self.processBeamSequence()
        

    
    def getPatientDemographics(self, dicom):

        self.PID      = dicom.PatientID
        self.Patient  = dicom.PatientName
        

        
        
    def getBeamSequence(self, dicom): #overriden in ck 
        self.beamSequence = dicom.BeamSequence
        
    def processBeamSequence(self):
        raise NotImplementedError
        
    def __eq__(self, other):
        
        retVal = True
        
       
        if not type(self) == type(other):
            print(f"Attempted to run comparison between different machines!")
            return False
        
        for idx, beam in enumerate(self.beams):
            print("Checking Beam: " + str(idx + 1))
            if not self.beams[idx] == other.beams[idx]:
                print(f"Mismatch in beam {idx + 1}")
                retVal = False
        return retVal
            
            
        
        
    
        

class VarianParser(MachineParserBase):
    
    NUM_MLC = 120
    
    def __init__(self, dicom):
        super().__init__(dicom)
        self.dicom = dicom
        self.getDoseInfo()


       
        
    def removeSetupBeams(self): #should replace with better logic due to naming conventions rarely being followed 
        deleteStrings = ['setup', 'cbct', 'sb'] #strings to look for in beam names to be removed
        toDelete = []
        for idx, beam in enumerate(self.beamSequence): #loop over all beams in beamsequence and delete them if they appear to be a setup beam
            tmp = beam.BeamName
            if  any(s in tmp.lower() for s in deleteStrings):
                toDelete.append(idx)
        
        for idx in reversed(toDelete): #loop over beam sequence backwards and remove indices of ostensible setup beams
            del self.beamSequence[idx]
            

            
                
    def processBeamSequence(self):
        self.removeSetupBeams() 
        self.beams = []
        for b in self.beamSequence:
            #print(b.BeamName)
            self.beams.append(VarianBeam(b))
            
    def getDoseInfo(self):
        
        fgs = self.dicom.FractionGroupSequence[0]
        
        rbs = fgs.ReferencedBeamSequence
        self.fractions = fgs[0x300a, 0x0078].value
        
        self.beamMU = []
        for idx, ii in enumerate(rbs):
            try:
                self.beamMU.append(rbs[idx][0x300a,0x0086].value)
            except KeyError: #RS puts setup beams in this tag with no mu key
                pass
            
            
    def __eq__(self, other):
        
        print('Beginning check for patient ' + str(self.Patient) + ' MRN: ' + str(self.PID))
        try:
            print(f'Plan ID is: {self.dicom.RTPlanLabel}')
        except:
            pass
        
        retVal = True
        
        if self.fractions == other.fractions:
            
            print('-Checking Fractions: PASSED')
        else:
            print("-Checking Fractions: FAILED")
            retVal = False

        muCheck = np.array(self.beamMU) - np.array(other.beamMU)
        if np.max(np.abs(muCheck)) > 1.0:
            print("-Checking Beam MUs: FAILED")
            retVal = False
        else:
            print("-Checking Beam MUs: PASSED")
        
        if super().__eq__(other):
            pass
        else:
            retVal = False
            
        return retVal
        
        #for idx, ii in enumerate(self.beams):
        #    
        #    if not self.beams[idx] == other.beams[idx]:
        #        return False
        #return True
            
                   
        
        
        
    
class RadixactParser(MachineParserBase):
    
    NUM_MLC = 60
    
    def __init__(self, dicom):
        super().__init__(dicom)
        self.dicom = dicom
        self.getDoseInfo()
        #self.getLasers(dicom)
        
        
    def getDoseInfo(self):
            
        fgs = self.dicom.FractionGroupSequence[0]
            
        rbs = fgs.ReferencedBeamSequence
        self.fractions = fgs[0x300a, 0x0078].value
            
        self.beamMU = []
        for idx, ii in enumerate(rbs):
            try:
                self.beamMU.append(rbs[idx][0x300a,0x0086].value)
            except KeyError: #RS puts setup beams in this tag with no mu key
                pass
                
        
        
    def getLasers(self, dicom):
        self.lasers = []
        x = dicom.PatientSetupSequence[0].SetupDeviceSequence[0][0x300a,0x01bc].value
        y = dicom.PatientSetupSequence[0].SetupDeviceSequence[1][0x300a,0x01bc].value
        z = dicom.PatientSetupSequence[0].SetupDeviceSequence[2][0x300a,0x01bc].value
        self.lasers = [float(i) for i in [x,y,z]]
        
    def processBeamSequence(self):
        self.beams = []
        for b in self.beamSequence:
            self.beams.append(RadixactBeam(b))
    
    def __eq__(self, other):
        
        print('Beginning check for patient ' + str(self.Patient) + ' MRN: ' + str(self.PID))
        retVal = True
        
        if self.fractions == other.fractions:
            
            print('-Checking Fractions: PASSED')
        else:
            print("-Checking Fractions: FAILED")
            retVal = False

        muCheck = np.array(self.beamMU) - np.array(other.beamMU)
        if np.max(np.abs(muCheck)) > 1.0:
            print("-Checking Beam MUs: FAILED")
            retVal = False
        else:
            print("-Checking Beam MUs: PASSED")
        
        if super().__eq__(other):
            pass
        else:
            retVal = False
            
        return retVal
    
    
class CyberKnifeParser(MachineParserBase):
    
    NUM_MLC = 52
    
    def __init__(self, dicom):
        super().__init__(dicom)
        
        
    def getBeamSequence(self, dicom):
        self.beamSequence = dicom.RoboticPathControlPointSequence
    
    def processBeamSequence(self):
        self.beams = []
        self.beams.append(CyberKnifeBeam(self.beamSequence))
        
    def __eq__(self, other):
        if not super().__eq__(other):
            return False
        return self.beams == other.beams
    