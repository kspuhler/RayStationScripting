# -*- coding: utf-8 -*-
"""
Created on Wed Mar 27 12:00:48 2024

@author: spuhlk01
"""

# -*- coding: utf-8 -*-
"""
Created on Thu Feb  8 13:56:17 2024

@author: spuhlk01
"""

try:
    from connect import *
except:
    pass

import sys

sys.path.append("\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")


from Sim.Templates.SimTemplate import SimTemplate


class BreastBilateral(SimTemplate):
    
    def __init__(self, planName, beamSetName):
        #fieldNum 2 = tangents 3= tan + sclav 4 = 4 field 5= with electron boost
        
        #TODO electron functionality for five fields
        
        super().__init__(planName, beamSetName)
        
        pois = [x.Name for x in self.case.PatientModel.PointsOfInterest]
        
        if not "Marker 1" in pois:
            self.case.PatientModel.CreatePoi(Examination=self.exam, Point={ 'x': 0, 'y': 0, 'z': 0 }, Name="Marker 1", Color="Yellow", VisualizationDiameter=1, Type="Marker")
        
        if not "Marker 2" in pois:
            self.case.PatientModel.CreatePoi(Examination=self.exam, Point={ 'x': 0, 'y': 0, 'z': 0 }, Name="Marker 2", Color="Yellow", VisualizationDiameter=1, Type="Marker")
        

        
        self.addBeams()
        if False:
            self.doContours()
        
    
    def addBeams(self):
        
        
        biPointLt = self.beamSet.CreatePhotonBeam(BeamQualityId='6',  IsocenterData={ 'Position': { 'x': 0, 'y': 0, 'z': 0 }, 'NameOfIsocenterToRef': 'BI_POINT_LT', 'Name':'BI_POINT_LT', 'Color': "3, 252, 252" }, 
                                          Name = 'BI_POINT_LT', GantryAngle = 0, CollimatorAngle = 0)

        pinLt = self.beamSet.CreatePhotonBeam(BeamQualityId='6',  IsocenterData={ 'Position': { 'x': 0, 'y': 0, 'z': 0 }, 'NameOfIsocenterToRef': 'pin_lt', 'Name':'PIN_LT', 'Color': "252, 3, 236" }, 
                                          Name = 'PIN_LT', GantryAngle = 0, CollimatorAngle = 0)
                              
        biPointRt = self.beamSet.CreatePhotonBeam(BeamQualityId='6',  IsocenterData={ 'Position': { 'x': 0, 'y': 0, 'z': 0 }, 'NameOfIsocenterToRef': 'BI_POINT_RT', 'Name':'BI_POINT_RT', 'Color': "3, 252, 252" }, 
                                          Name = 'BI_POINT_RT', GantryAngle = 0, CollimatorAngle = 0)

        pinRt = self.beamSet.CreatePhotonBeam(BeamQualityId='6',  IsocenterData={ 'Position': { 'x': 0, 'y': 0, 'z': 0 }, 'NameOfIsocenterToRef': 'pin_rt', 'Name':'PIN_RT', 'Color': "252, 3, 236" }, 
                                          Name = 'PIN_RT', GantryAngle = 0, CollimatorAngle = 0)


        self.addMedial()
        self.addSclav()
        self.addPAB()
            
    
    def addMedial(self):
        x1 = -15
        x2 = 15
        y1 = -15
        y2 = 15
        
        bName = ''


                
        self.rtisoName = 'Rt Breast'
        bName =  'Rt Medial'
        g  = 50
        c  =  0 
        

        rtMedial = self.beamSet.CreatePhotonBeam(BeamQualityId='6',  IsocenterData={ 'Position': { 'x': 0, 'y': 0, 'z': 0 }, 'NameOfIsocenterToRef': self.rtisoName, 'Name': self.rtisoName, 'Color': "255, 255, 128" }, 
                                              Name = bName, GantryAngle = g, CollimatorAngle = c)   
        
        rtMedial.SetInitialJawPositions(X1=x1, X2 = 0, Y1 = y1, Y2 = y2)     


                
        self.ltisoName = 'Lt Breast'
        bName = 'Lt Medial'
        g   = 310
        c   =   0
        x1  =   0
        ltMedial = self.beamSet.CreatePhotonBeam(BeamQualityId='6',  IsocenterData={ 'Position': { 'x': 0, 'y': 0, 'z': 0 }, 'NameOfIsocenterToRef': self.ltisoName, 'Name': self.ltisoName, 'Color': "255, 255, 128" }, 
                                              Name = bName, GantryAngle = g, CollimatorAngle = c)   
        
        ltMedial.SetInitialJawPositions(X1=x1, X2 = 0, Y1 = y1, Y2 = y2)     
     
        
    def addSclav(self):
        
        x1 = -5
        x2 = 5
        y1 = 0
        y2 = 5
        c  = 0
        
        
        g = 15
        bName = 'rt_sclav'
        rtSclav = self.beamSet.CreatePhotonBeam(BeamQualityId='6',  IsocenterData={ 'Position': { 'x': 0, 'y': 0, 'z': 0 }, 'NameOfIsocenterToRef': self.rtisoName, 'Name': self.rtisoName, 'Color': "255, 255, 128" }, 
                                                  Name = bName, GantryAngle = g, CollimatorAngle = c)  
            
        rtSclav.SetInitialJawPositions(X1=x1, X2 = x2, Y1 = y1, Y2 = y2)  
            
        
        bName = 'lt_sclav'
        g = 345
        ltSclav = self.beamSet.CreatePhotonBeam(BeamQualityId='6',  IsocenterData={ 'Position': { 'x': 0, 'y': 0, 'z': 0 }, 'NameOfIsocenterToRef': self.ltisoName, 'Name': self.ltisoName, 'Color': "255, 255, 128" }, 
                                                  Name = bName, GantryAngle = g, CollimatorAngle = c)  
            
        ltSclav.SetInitialJawPositions(X1=x1, X2 = x2, Y1 = y1, Y2 = y2)              

        
    def addPAB(self):
        
        
        x1 = -5
        x2 = 5
        y1 = 0
        y2 = 5
        g=180
        c  = 0 
        
        bName = 'rt_pab'
        rtpab = self.beamSet.CreatePhotonBeam(BeamQualityId='6',  IsocenterData={ 'Position': { 'x': 0, 'y': 0, 'z': 0 }, 'NameOfIsocenterToRef': self.rtisoName, 'Name': self.rtisoName, 'Color': "255, 255, 128" }, 
                                              Name = bName, GantryAngle = g, CollimatorAngle = c)  
        
        rtpab.SetInitialJawPositions(X1=x1, X2 = x2, Y1 = y1, Y2 = y2)  

        bName = 'lt_pab'
        ltpab = self.beamSet.CreatePhotonBeam(BeamQualityId='6',  IsocenterData={ 'Position': { 'x': 0, 'y': 0, 'z': 0 }, 'NameOfIsocenterToRef': self.ltisoName, 'Name': self.ltisoName, 'Color': "255, 255, 128" }, 
                                              Name = bName, GantryAngle = g, CollimatorAngle = c)  
        
        ltpab.SetInitialJawPositions(X1=x1, X2 = x2, Y1 = y1, Y2 = y2)  
        
    def doContours(self):
        
        self.exam.RunDeepLearningSegmentationWithCustomRoiNames(ExaminationsAndRegistrations={self.exam.Name: None }, ModelAndRoiNames= {'RSL DLS Male Pelvic CT': {'SpinalCord': 'SpinalCanal'}})
        
        
        
if __name__ == '__main__':
    tmp = BreastBilateral('bilat', 'bilat')
        
            
        

        