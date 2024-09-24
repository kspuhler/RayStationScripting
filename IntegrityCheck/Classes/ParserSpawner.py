import pydicom as pdm
import numpy as np


from Machines import *

class ParserSpawner(object):
    #Base class for organizing information in dicom files, handles machines differences and stuff
    MACHINE_DICT = {'VARIAN' :  ['DNU_TB_TEST', 'TrueBeamSN1106', 'TrueBeamSN1106_V', '21EX'],
                    'RADIXACT': ['4010100_1000MU'],
                    'CK_MLC':   ['RSL_CyberKnife', 'C0363', 'C0480'],
                    }
    
    def __init__(self, fpath):
        self.dicom     = pdm.read_file(fpath)
        self.getMachineName(self.dicom)
        
        
    ##################################################################################################
    
    def getMachineName(self, dicom): #gets the machine name from the dicom file
    
        if hasattr(dicom, 'RoboticPathControlPointSequence'): #is a ck
            self.txMachine = dicom.TreatmentDeviceIdentificationSequence[0].DeviceLabel
            
        else: #is not a ck
            self.txMachine = [x.TreatmentMachineName for x in dicom.BeamSequence]
            if len(set(self.txMachine)) > 1:
                Warning('PARSER: Multiple machines detected in plan for file:' + self.fpath)
                
            else:
                self.txMachine = self.txMachine[0]
                
                
    def spawnParser(self, txMachine):
        if txMachine in self.MACHINE_DICT['VARIAN']:
            return VarianParser(self.dicom)
        elif txMachine in self.MACHINE_DICT['RADIXACT']:
            return RadixactParser(self.dicom)
        elif txMachine in self.MACHINE_DICT['CK_MLC']:
            return CyberKnifeParser(self.dicom)
        else:
            raise Exception(f"PARSER: {txMachine} is not a recognized machine id")
                
        
 
# =============================================================================
# if __name__ == '__main__':
#     fpath = 'F:\\SHARING\\Radiation Oncology Physics\\Physics Staff\\KS\\RaystationTesting\\Integrity Check\\Test\\'
#     
#     try:
#         rs   = ParserSpawner(fpath+'3D\\RayStation.dcm')
#         rss  = rs.spawnParser(rs.txMachine)
#         print('3D RS Build Success!')
#         
#     except: 
#         print("3D RS Fail")
#         
#     try:
#         aria = ParserSpawner(fpath+'3D\\RP.WUH19761976.3D.dcm')
#         ariaa = aria.spawnParser(aria.txMachine)
#         print("3D Aria Build Success!")
#         
#     except:
#         print("3D Aria Fail")
#         
#     try:
#         ck   = ParserSpawner(fpath+'CKPlan\\RTRAD1.2.752.243.1.1.20231226134825205.4900.15706.dcm')
#         ckk  = ck.spawnParser(ck.txMachine)
#         print("CK Build Success!")
#         
#     except:
#         print('CK Fail')
#         
#     try:
#         radi = ParserSpawner(fpath+'Radixact\\Thymoma4500_Plan.7080438177968')
#         radii = radi.spawnParser(radi.txMachine)
#         print('Radixact Build Success!')
#     except:
#         print("radixact fail") 
#     try: 
#         vmat = ParserSpawner(fpath+'VMAT\\RP.1.2.246.352.71.5.569583262656.2340046.20231205145527.dcm')
#         vmats = vmat.spawnParser(vmat.txMachine)
#         
#         print("VMAT Build Success!")
#     except:
#         print("vmat fail")
# 
# 
# =============================================================================
