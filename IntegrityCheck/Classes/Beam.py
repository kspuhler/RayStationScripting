# -*- coding: utf-8 -*-
"""
Created on Thu Jan 11 11:39:16 2024

@author: spuhlk01
"""

import numpy as np

class Beam(object):
    
    NUM_MLC = None

    def __init__(self, beamSequenceSlice): 
        
        self.data = beamSequenceSlice
        
        self.getNumControlPoints()
        self.constructMlcArray()
        self.getBeamInfo()
        
        self.eqCheckMath = {}
        self.eqCheckString = {}
                
        
    
    def getBeamInfo(self):
        #get relative beam coordinates
        #iso, gantry angles, collimator angles, etc
        raise NotImplementedError

        
        
    def getNumControlPoints(self, **kwargs):
        raise NotImplementedError
        
    def constructMlcArray(self,):
        #return ndarray size (num_mlc, num_control_point)
        #overridden in RadixactBeam
        self.mlc = np.zeros(shape=(self.NUM_MLC, self.numControlPoints))
    

        
    def __eq__(self, other, tol = 0.1):
        
        retVal = True
        for key, value in self.eqCheckMath.items():

            string = '-Checking ' + key + ': '
            print(key)
            check = np.array(self.eqCheckMath[key]) - np.array(other.eqCheckMath[key])
            
            if np.max(np.abs(check)) > tol:
                retVal = False
                string += '\n*******************\n'
                string += 'FAILED \n'
                string += '*******************\n'
            else:
                string += 'Passed \n'
                
            print(string)
            
    
        for key, value in self.eqCheckString.items():
            
            string = '-Checking ' + key + ': '
            print(key)
            if not self.eqCheckString[key] == other.eqCheckString[key]:
                retVal = False
                string += '\n*******************\n'
                string += 'FAILED \n'
                string += '*******************\n'
            else:
                string += 'Passed \n'
            print(string)    
        return retVal
    
        
        
class VarianBeam(Beam):
    
    NUM_MLC = 120    
    
    def __init__(self, beamSequenceSlice):
        super().__init__(beamSequenceSlice)
        self.eqCheckMath = {'Energy': self.energy, 
                            'Isocenter Coords': self.iso, 
                            'SSD': self.ssd, 
                            'Gantry': self.gantry, 
                            'Collimator': self.col, 
                            'X Jaw': self.x, 
                            'Y Jaw': self.y, 
                            'MLC': self.mlc, 
                            'Fractional MU': self.mu}
        
        self.eqCheckString = {'Beam Type': self.type}
        try: #add applicators for electron plan
            self.eqCheckString['Applicator'] = self.applicator
        except:
            pass
        
        
        
    def getNumControlPoints(self):
        self.numControlPoints = len(self.data.ControlPointSequence)
        
    def getBeamInfo(self):
        
        self.x = np.zeros(shape=(2, 1), dtype = float)
        self.y = np.zeros(shape=(2, 1), dtype = float)
        self.mu = np.zeros(shape=(1, self.numControlPoints), dtype = float)
        
        cps = self.data.ControlPointSequence #literally just shorthand
        self.type     = self.data.RadiationType
     
        self.energy   = cps[0][0x300a,0x0114].value
        self.energy   = int(self.energy)
        self.iso      = cps[0][0x300a,0x012c].value
        self.ssd      = cps[0][0x300a, 0x0130].value
        self.gantry   = cps[0][0x300a, 0x011e].value
        self.rotation = cps[0][0x300a,0x120].value
        self.col      = cps[0][0x300a, 0x0120].value
        
        try:
            jaws = cps[0][0x300a,0x011a]
            self.x = jaws[0][0x300a,0x011c].value
            self.y = jaws[1][0x300a,0x011c].value
            
            
        except KeyError:
            pass
        
        #fill mlc
        for idx, cp in enumerate(cps): 
            try:
                self.mu[:,idx] = float(cp[0x300a, 0x0134].value)
            except ValueError:
                pass
            except KeyError:
                pass
            try:
                jaws = cp[0x300a,0x011a]
                self.mlc[:,idx] = jaws[-1][0x300a,0x011c].value
            except KeyError:
                pass
            except ValueError:
                pass
                
        if self.type.lower() == 'electron':
            if not hasattr(self, 'applicator'):
                self.applicator = []
            appSeq = self.data[0x300a,0x0107].value
            appSeq = appSeq[0]
            appId  = appSeq[0x300a,0x0108].value
            self.applicator.append(appId)
            #self.applicator.append(self.data.)


class RadixactBeam(Beam):
    
    NUM_MLC = 64
    
    def __init__(self, beamSequenceSlice):
        super().__init__(beamSequenceSlice)
        self.eqCheckMath = { 'X Jaw': self.x, 
                            'Y Jaw': self.y, 
                            'MLC': self.mlc, 
                            'Fractional MU': self.mu}
        
        
    def getBeamInfo(self):
        

        self.gantry = np.zeros(shape=(1, self.numControlPoints), dtype = float)
        self.iso    = np.zeros(shape=(3, self.numControlPoints), dtype = float)
        self.x      = np.zeros(shape=(2, self.numControlPoints), dtype = float)
        self.y      = np.zeros(shape=(2, self.numControlPoints), dtype = float)
        self.mu     = np.zeros(shape=(1, self.numControlPoints), dtype = float)
        
        mlcIndex = 0
        
        for idx, cp in enumerate(self.data.ControlPointSequence):
            
            self.gantry[:, idx]         = float(cp[0x300a, 0x011e].value)
            if idx == 0:
                self.iso[:, idx]            = [float(i) for i in cp[0x300a, 0x012c].value]
            self.mu[:, idx]             = float(cp[0x300a, 0x0134].value)
        
            tmp = cp.BeamLimitingDevicePositionSequence
            self.x[:, idx]           = [float(i) for i in tmp[0][0x300a, 0x011c]]
            self.y[:, idx]           = [float(i) for i in tmp[1][0x300a, 0x011c]]
            try:
                mlcString = cp[0x300d, 0x10a7].value
                self.mlc[:, mlcIndex]         = self.decodeMlcString(mlcString)
                mlcIndex += 1
            except KeyError:
                pass

        
          
    def getNumControlPoints(self):
        self.numControlPoints = len(self.data.ControlPointSequence)
        
    def decodeMlcString(self, mlcString): #decodes the byte string representing radixact mlc positions
        mlcString = mlcString.decode()
        mlcString =  mlcString.split('\\')
        return [float(i) for i in mlcString]
    
    def constructMlcArray(self):
        #return ndarray size (num_mlc, num_control_point)
        numMlcPoints = 0
        for ii in self.data.ControlPointSequence:
            try:
                ii[0x300d, 0x10a7]
                numMlcPoints += 1
            except KeyError:
                pass
        
        self.mlc = np.zeros(shape=(self.NUM_MLC, numMlcPoints))
        
        
        
class CyberKnifeBeam(Beam):
    
    NUM_MLC = 52
    
    def __init__(self, roboticPathControlPointSequenceSlice):
        super().__init__(roboticPathControlPointSequenceSlice)
        
        self.eqCheckMath = {'Robot Coords': self.coords, 'MU': self.mu, 'MLC': self.mlc}
        

    
    def getBeamInfo(self):
        self.coords = np.zeros(shape=(6, self.numControlPoints ), dtype = float) # [x, y, z, pitch, roll, yaw] other dimension is control points
        self.mu     = np.zeros(self.numControlPoints )
        
        #idx = 0
        arrayIndex = 0
        for idx, cp in enumerate(self.data): #loop over control points
            
            
            #print(idx)
            
            if idx%2:
                #idx+=1
                continue
            idxMU = idx + 1
            [x, y, z] = cp[0x3010, 0x0093].value #robot head positions
            p         = cp[0x3010, 0x0094].value #pitch
            r         = cp[0x3010, 0x0095].value #roll
            yw        = cp[0x3010, 0x0096].value #yaw
            
            

            self.coords[:, arrayIndex] = [x, y, z, p, r, yw] #machine head coordinates
            print([x,y,z,p,r,yw])
            print('    ')
            print(self.coords[:,arrayIndex])
            #self.coords[ arrayIndex,:] = [x, y, z, p, r, yw] #machine head coordinates
            try:
                self.mlc[:, arrayIndex] = cp.RTBeamLimitingDeviceOpeningSequence[0][0x300a, 0x064a].value #mlc positiions
            except:
                pass
            arrayIndex += 1 
            try:
                self.mu[arrayIndex] = self.data[idxMU][0x300a, 0x063c].value
            except IndexError:
                break
   #         idx += 1
    
    
    def getNumControlPoints(self):
        num = len(self.data)
        if num%2:
            raise ValueError("Odd number of control points in CK plan!")
            
        else:
            self.numControlPoints = int(num/2)
            

        
        
#if __name__ == '__main__':
#    import os
#    os.chdir('F:\SHARING\Radiation Oncology Physics\Raystation Export Check\CK\test\cone\noRadiationSet')
