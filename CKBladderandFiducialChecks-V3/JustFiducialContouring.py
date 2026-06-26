# -*- coding: utf-8 -*-
"""
Created on Thu Jun 19 13:15:48 2025

@author: santoj14
"""

from connect import *


class CKsimulation():
    """
    A base class for creating scripts and apps specific to Cyberknife Prostate cases.

    Uses the autocontoured bladder and prostate to determine the volumes and ratio,
    places the fiducial marker points and the determines the trackability and 
    quality of the fiducial implant
    """

    def __init__(self, *args):

        
        self.init_current_CT()

        self.contour_list   = [] #LIST OF GEOMETRIES CONTAINING CONTOURS
        self.contour_list2  = [] #LIST OF ALL GEOMETRIES; FILLED AND EMPTY
        self.fiducials_list = []
        self.selected_Target = 'MDBOOST'
        
        make_contour_list(self)
        print(self.contour_list)
        make_POI_list(self)
        print(self.fiducials_list)

    def init_current_CT(self, *args):
        """Initialize the active RS CT set, study, contours, and POIs."""
        self.case = get_current("Case")
        self.examination = get_current("Examination")
        self.exam_name = self.examination.Name
        print("FROM init_current_CT():THE CURRENT CT SET IS:", self.exam_name)

        self.PatientModel = self.case.PatientModel
        self.StructureSet = self.PatientModel.StructureSets
        
        #### ensure you look for contours and fiducuals on the primamry CT only
        self.Contours = self.StructureSet[self.exam_name].RoiGeometries
        self.Fiducials = self.StructureSet[self.exam_name].PoiGeometries
        
    def createFiducialROI(self, *args):
              """
              Create an ROI in which to search for fiducials.

              Create an expansion around the prostate. Activated when the user selects a
              target contour from the drop-down.
              """
              print(self.contour_list2)
              if "PROS-ROI" in self.contour_list2: 
                  print('PROS-ROI already exists!')
              else:
                  retval_0 = self.case.PatientModel.CreateRoi(Name="PROS-ROI", Color="Blue",
                                                              Type="Control", TissueName=None,
                                                              RbeCellTypeName=None, RoiMaterial=None)

                  retval_0.CreateMarginGeometry(Examination=self.examination, SourceRoiName=self.selected_Target,
                                                    MarginSettings={'Type': "Expand",
                                                                    'Superior': 2,
                                                                    'Inferior': 2,
                                                                    'Anterior': 2,
                                                                    'Posterior': 2,
                                                                    'Right': 2,
                                                                    'Left': 2})

    def deleteFiducialROI(self, *args):
            """Delete the Fiducial ROI."""
            try:
              print('Deleting PROS-ROI contour')
              self.case.PatientModel.RegionsOfInterest['PROS-ROI'].DeleteRoi()
            except Exception as A:
              print(A)
            
    def findFiducials(self, *args):
            """Use the RS thresholding tool to identify fiducials in patient.
            
            This will search the entire CT for objects with a 3071 HU value, and 
            contour those objects. It then booleans the fiducial contour with the
            fiducial ROI contour 
            """
            if "Fiducial-Markers" in self.contour_list2:
                print('Fiducial-Markers contour already exists!')
                test = self.case.PatientModel.RegionsOfInterest['Fiducial-Markers']
                test.GrayLevelThreshold(Examination=self.examination, LowThreshold=2763.9,
                                            HighThreshold=3071,
                                            PetUnit="",
                                            CbctUnit=None,
                                            BoundingBox=None)

                test.CreateAlgebraGeometry(Examination=self.examination, Algorithm="Auto",
                                               ExpressionA={'Operation': "Union",
                                                            'SourceRoiNames': ["Fiducial-Markers"],
                                                            'MarginSettings': {'Type': "Expand",
                                                                               'Superior': 0,
                                                                               'Inferior': 0,
                                                                               'Anterior': 0,
                                                                               'Posterior': 0,
                                                                               'Right': 0, 'Left': 0}},
                                               ExpressionB={'Operation': "Union", 'SourceRoiNames': ["PROS-ROI"],
                                                            'MarginSettings': {'Type': "Expand",
                                                                               'Superior': 0,
                                                                               'Inferior': 0,
                                                                               'Anterior': 0,
                                                                               'Posterior': 0,
                                                                               'Right': 0,
                                                                               'Left': 0}},
                                               ResultOperation="Intersection",
                                               ResultMarginSettings={'Type': "Expand",
                                                                     'Superior': 0,
                                                                     'Inferior': 0,
                                                                     'Anterior': 0,
                                                                     'Posterior': 0,
                                                                     'Right': 0,
                                                                     'Left': 0})
                return test
            
            else:
                retval_0 = self.case.PatientModel.CreateRoi(Name="Fiducial-Markers", Color="255, 128, 64",
                                                            Type="Marker", TissueName=None,
                                                            RbeCellTypeName=None, RoiMaterial=None)

                retval_0.GrayLevelThreshold(Examination=self.examination, LowThreshold=2763.9,
                                            HighThreshold=3071,
                                            PetUnit="",
                                            CbctUnit=None,
                                            BoundingBox=None)

                retval_0.CreateAlgebraGeometry(Examination=self.examination, Algorithm="Auto",
                                               ExpressionA={'Operation': "Union",
                                                            'SourceRoiNames': ["Fiducial-Markers"],
                                                            'MarginSettings': {'Type': "Expand",
                                                                               'Superior': 0,
                                                                               'Inferior': 0,
                                                                               'Anterior': 0,
                                                                               'Posterior': 0,
                                                                               'Right': 0, 'Left': 0}},
                                               ExpressionB={'Operation': "Union", 'SourceRoiNames': ["PROS-ROI"],
                                                            'MarginSettings': {'Type': "Expand",
                                                                               'Superior': 0,
                                                                               'Inferior': 0,
                                                                               'Anterior': 0,
                                                                               'Posterior': 0,
                                                                               'Right': 0,
                                                                               'Left': 0}},
                                               ResultOperation="Intersection",
                                               ResultMarginSettings={'Type': "Expand",
                                                                     'Superior': 0,
                                                                     'Inferior': 0,
                                                                     'Anterior': 0,
                                                                     'Posterior': 0,
                                                                     'Right': 0,
                                                                     'Left': 0})
            
                return retval_0



def make_contour_list(self, *args):
    """Make a list of contours names to check. Only populates filled contours."""
    for i in self.Contours:
        if (i.HasContours() == True):
         names = i.OfRoi.Name
         self.contour_list.append(names)
    for i in self.Contours:
         names = i.OfRoi.Name
         self.contour_list2.append(names)

def make_POI_list(self, *args):
    """Make a list of POI names to check."""
    for i in self.Fiducials:
        names = i.OfPoi.Name
        self.fiducials_list.append(names)