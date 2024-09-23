"""
Created on Tue Feb 20 09:48:24 2024.

@author: santoj14
"""

"""
A class for Cyberknife Prostate cases.

This class provides methods for determining bladder volume as well as
fiducial-related metrics.
Uses the auto contoured bladder and prostate to determine the volumes and ratio,
inserts  the fiducial marker points (POIs) and the determines the trackability and 
quality of the fiducial implant via an implementation of Accuray's minimum
angle test.
"""
from connect import *
import numpy as np
import math as m
from PyQt5.QtWidgets import QMessageBox
from itertools import combinations
#from termcolor import colored
import sys

sys.path.append("F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD\CK Bladder and Fiducial Checks")
sys.path.append("\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD\CK Bladder and Fiducial Checks")


class CKsimulation():
    """
    A base class for creating scripts and apps specific to Cyberknife Prostate cases.

    Uses the autocontoured bladder and prostate to determine the volumes and ratio,
    places the fiducial marker points and the determines the trackability and 
    quality of the fiducial implant
    """

    def __init__(self, *args):

        self.case = get_current("Case")
        self.examination = get_current("Examination")
        self.exam_name = self.examination.Name
        print("THE CURRENT CT SET IS:", self.exam_name)

        self.PatientModel = self.case.PatientModel
        self.StructureSet = self.PatientModel.StructureSets

        #### ensure you look for contours and fiducuals on the primamry CT only
        self.Contours = self.StructureSet[self.exam_name].RoiGeometries
        self.Fiducials = self.StructureSet[self.exam_name].PoiGeometries

        self.contour_list = []
        self.fiducials_list = []

        self.spacings_combos = []  ## iter object
        self.name_pairs_combos = []  ## iter object
        self.angle_names_combo = []  ## iter object
        self.angle_combos = []  ## iter object

        self.name_pairs = []
        self.two_groups = []
        self.segments = []
        self.segments_names = []
        self.pair_distance = []
        self.angle_names = []
        self.angle_names_formatted = []
        self.angle_group = []
        self.angles = []
        self.min_angle_msg = []
        self.min_angle_test = []

        self.noContoursExist = QMessageBox()
        self.noFiducialsExist = QMessageBox()
        self.FiducialsPass = QMessageBox()
        self.FiducialsFail = QMessageBox()

        make_contour_list(self)
        print(self.contour_list)
        make_POI_list(self)
        print(self.fiducials_list)
        #lookForGTV(self)

        if ('Bladder' in self.contour_list) and (self.Contours['Bladder'].HasContours() == True) and (
                'GTVp' in self.contour_list and self.Contours['GTVp'].HasContours() == True):
            self.Bladder_volume = round(self.Contours['Bladder'].GetRoiVolume(), 2)
            self.Prostate_volume = round(self.Contours['GTVp'].GetRoiVolume(), 2)
            self.Ratio = round(self.Bladder_volume / self.Prostate_volume, 2)

        elif ('Bladder' in self.contour_list) and (self.Contours['Bladder'].HasContours() == True) and (
                'mdGTV' in self.contour_list and self.Contours['mdGTV'].HasContours() == True):
            self.Bladder_volume = round(self.Contours['Bladder'].GetRoiVolume(), 2)
            self.Prostate_volume = round(self.Contours['mdGTV'].GetRoiVolume(), 2)
            self.Ratio = round(self.Bladder_volume / self.Prostate_volume, 2)

        elif ('Bladder' in self.contour_list) and (self.Contours['Bladder'].HasContours() == True) and (
                'MDGTV' in self.contour_list and self.Contours['MDGTV'].HasContours() == True):
            self.Bladder_volume = round(self.Contours['Bladder'].GetRoiVolume(), 2)
            self.Prostate_volume = round(self.Contours['MDGTV'].GetRoiVolume(), 2)
            self.Ratio = round(self.Bladder_volume / self.Prostate_volume, 2)

        else:
            msg = 'There must be a ''Bladder'' contour and a target named GTVp, mdGTV, or MDGTV!!'
            self.noContoursExist.setIcon(QMessageBox.Critical)
            self.noContoursExist.setWindowTitle("Error")
            self.noContoursExist.setText(msg)
            print(msg)
            retval = self.noContoursExist.exec_()
            sys.exit()

    def createFiducialROI(self, *args):
        """
        Create an ROI in which to search for fiducials.
        
        Create an expansion around the prostate.
        """
        if "PROS-ROI" in self.contour_list:
            print('PROS-ROI already exists!')
        else:
            retval_0 = self.case.PatientModel.CreateRoi(Name="PROS-ROI", Color="Blue",
                                                        Type="Control", TissueName=None,
                                                        RbeCellTypeName=None, RoiMaterial=None)

            if ('GTVp' in self.contour_list):
                retval_0.CreateMarginGeometry(Examination=self.examination, SourceRoiName="GTVp",
                                              MarginSettings={'Type': "Expand",
                                                              'Superior': 2,
                                                              'Inferior': 2,
                                                              'Anterior': 2,
                                                              'Posterior': 2,
                                                              'Right': 2,
                                                              'Left': 2})

            elif ('mdGTV' in self.contour_list):
                retval_0.CreateMarginGeometry(Examination=self.examination, SourceRoiName="mdGTV",
                                              MarginSettings={'Type': "Expand",
                                                              'Superior': 2,
                                                              'Inferior': 2,
                                                              'Anterior': 2,
                                                              'Posterior': 2,
                                                              'Right': 2,
                                                              'Left': 2})
            elif ('MDGTV' in self.contour_list):
                retval_0.CreateMarginGeometry(Examination=self.examination, SourceRoiName="MDGTV",
                                              MarginSettings={'Type': "Expand",
                                                              'Superior': 2,
                                                              'Inferior': 2,
                                                              'Anterior': 2,
                                                              'Posterior': 2,
                                                              'Right': 2,
                                                              'Left': 2})

    def deleteFiducialROI(self, *args):
        """Delete the Fiducial ROI."""
        #if 'PROS-ROI' in self.contour_list:
        print('Deleting PROS-ROI contour')
        self.case.PatientModel.RegionsOfInterest['PROS-ROI'].DeleteRoi()
        #else:
        #   print('PROS-ROI does not exist!')

    def findFiducials(self, *args):
        """Use the RS thresholding tool to identify fiducials in patient.
        
        This will search the entire CT for objects with a 3071 HU value, and 
        contour those objects. It then booleans the fiducial contour with the
        fiducial ROI contour 
        """
        if "Fiducial-Markers" in self.contour_list:
            #self.case.PatientModel.RegionsOfInterest['Fiducial-Markers'].DeleteRoi()
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

    def insertFiducialMarkers(self, *args):
        """Create four marker type POIs in the patient.
        
        This will create 4 unplaced fiducials in the patient prostate volume
        The user will need to use the RayStation POI tools to place the fiducials
        in the physical markers on the CT.
        """
        if (self.Contours['Fiducial-Markers'].HasContours() == True):
            print("CREATING FIDUCIAL POIs")
            for i in range(0, 4):
                fid_center = self.Contours["Fiducial-Markers"].GetCenterOfRoi()
                name = 'Fid' + str(i + 1)  #DO NOT CHANGE THIS!!!

                if name in self.fiducials_list:
                 print('Fiducial: ', name, ' already exists!')
                else:
                    self.case.PatientModel.CreatePoi(Examination=self.examination,
                                                 Point={'x': fid_center['x'] + i / 2,
                                                        'y': fid_center['y'],
                                                        'z': fid_center['z']},
                                                 Name=name, Color="0, 255, 128",
                                                 VisualizationDiameter=0.5,
                                                 Type="Marker")
        self.Fiducials = self.StructureSet[0].PoiGeometries

    def count_fiducials(self, *args):
        """Count the number of fiducials (marker-type) POIs."""
        marker_count = 0

        #loop over POIs to get number of points of type marker
        for i, j in enumerate(self.Fiducials):
            marker_type = j.OfPoi.Type

            if marker_type == 'Marker':
                marker_count += 1

        if marker_count == 0:
            msg2 = 'There seem to be no fiducials identified. Please make sure you run run_bladder_check first!!'
            print(msg2)
            self.noFiducialsExist.setIcon(QMessageBox.Critical)
            self.noFiducialsExist.setWindowTitle("Error")
            self.noFiducialsExist.setText(msg2)
            print(msg2)
            retval = self.noFiducialsExist.exec_()
            sys.exit()

        return (marker_count)

    def getFiducialCoordinates(self, *args):
        """Get fiducial names and coordinates."""
        #loop over fiducial markers in plan and get numpy array of coords
        print('========== point names and coordinates===================')
        mker = 0
        coords = []
        coord = []
        names = []

        print('There are:', self.count_fiducials(), ' Fiducials')

        try:
            for i, j in enumerate(self.Fiducials):
                pt_name = j.OfPoi.Name
                marker_type = j.OfPoi.Type

                if marker_type == 'Marker':
                    coords = j.Point.values()
                    coords = list(coords)
                    self.fid_x = round(coords[0], 3)
                    self.fid_y = round(coords[1], 3)
                    self.fid_z = round(coords[2], 3)

                    names.append(pt_name)
                    coord.append(coords)

                    mker += 1

            self.coord_np = np.array(coord)
            self.names_np = np.array(names)
            print(self.names_np)
            print(self.coord_np)

            #user iter lib to create N groups of 2 points for fiducial spacing
            self.spacings_combos = combinations(self.coord_np[:], 2)
            #N groups of 2 fiducial names
            self.name_pairs_combos = combinations(self.names_np[:], 2)

        except:
            pass

    def calculateFiducialSpacings(self, *args):
        """Calculate the spacing between N fiducials."""
        print('============== Fiducial Spacings ================')
        pairdis = []

        for x, y in enumerate(self.name_pairs_combos):
            self.name_pairs.append(y)

        self.name_pairs = np.array(self.name_pairs)

        for c, d in enumerate(self.spacings_combos):
            self.two_groups.append(d)

        self.two_groups = np.array(self.two_groups)

        for j in range(0, len(self.two_groups)):
            for k in range(0, 2):
                a = self.two_groups[j][k]
                b = self.two_groups[j][0]
                name1 = self.name_pairs[j][k]
                name2 = self.name_pairs[j][0]

            #Generate N segments between M fiducials (6 segments for 4 fiducials e.g.)
            segment = a - b
            seg_name = (str(name1) + str(' ') + str(name2))
            self.segments.append(segment)
            self.segments_names.append(seg_name)

            distance = np.linalg.norm(segment)
            distance = round(distance, 2)
            pairdis.append(distance)

        self.pair_distance = np.array(pairdis)

        ### make arrays of all the M segments connecting the N fiducials 
        self.segments_names = np.array(self.segments_names)
        self.segments = np.array(self.segments)

        print(self.name_pairs)
        print(self.pair_distance)

        print('============== Connecting Segments  ================')
        print(self.segments_names)
        print(self.segments)

    def calculateFiducialAngles(self, *args):
        """Calculate the angles between M 3-point segments joining the fiducials.
        
        This information will be used in the minimum angle test method.
        """
        self.angle_names_combo = combinations(self.segments_names[:], 2)
        self.angle_combos = combinations(self.segments[:], 2)

        for i, j in enumerate(self.angle_combos):
            self.angle_group.append(j)

        for i, j in enumerate(self.angle_names_combo):
            self.angle_names.append(j)

        self.angle_names = np.array(self.angle_names)
        self.angle_group = np.array(self.angle_group)

        print('============== Angles  ================')
        ang_num = 0

        for count, i in enumerate(self.angle_group):
            a = self.angle_group[count][1]
            b = self.angle_group[count][0]
            n = self.angle_names[count]

            if (check_duplicate(n) == True):
                ang_num += 1
                print('ANGLE NUMBER:', ang_num)
                print('ANGLE NAME:', n)
                dot = np.dot(a, b)
                norm_a = np.linalg.norm(a)
                norm_b = np.linalg.norm(b)
                cos_xy = ((dot / (norm_a * norm_b)))
                print('cos ', cos_xy)

                angle = round(np.arccos(cos_xy), 3)
                angle_deg = np.degrees(angle)
                angle_deg = round(angle_deg, 3)

                if check_internal_angle(n) == False:
                    angle_deg = round(180. - angle_deg, 3)

                print('angle ', angle_deg, '\n')

                angle_name_string = 'Angle: ' + str(n)
                angle_name_string = angle_name_string.replace('[', '').replace('\'', '').replace(']', '')
                self.angle_names_formatted.append(angle_name_string)
                self.angles.append(angle_deg)

        self.angles = np.array(self.angles)
        print('LIST OF ANGLES:')
        print(self.angles)

    def minAngleTest(self, *args):
        """Perform minumum angle test defined in Precision treatment delivery manual.
               
        If the angle defined by the vertex formed by any 3 fiducials is greater than 15 degrees,
        return a Pass (Boolean True). Otherwise, the test fails (Boolean False).
        """
        fail_angle_count = 0
        num_fids = self.count_fiducials()
        num_possible_triangles = m.comb(num_fids, 3)

        print("Number of possible triangles:", num_possible_triangles)

        for i, a in enumerate(self.angles):
            if (a >= 15.0) and (a <= 165.0):
                self.min_angle_msg.append('Angle: ' + str(i) + 'passes the minimum angle requirement\n')
                self.min_angle_test.append('Pass')

            else:
                self.min_angle_msg.append(
                    'The angle formed by fiducials:\n' + str(i) + '\n does not pass the minimum angle requirement\n\n')
                self.min_angle_test.append('Fail')
                fail_angle_count += 1

        if num_possible_triangles <= fail_angle_count:
            msg2 = 'The fiducials fail the minimum angle test'
            print(msg2)
            self.FiducialsFail.setIcon(QMessageBox.Critical)
            self.FiducialsFail.setWindowTitle("Failed")
            self.FiducialsFail.setText(msg2)
            retval = self.FiducialsFail.exec_()

            return False
        else:
            msg2 = 'The fiducials pass the minimum angle test'
            print(msg2)
            self.FiducialsPass.setIcon(QMessageBox.Information)
            self.FiducialsPass.setWindowTitle("Pass")
            self.FiducialsPass.setText(msg2)
            retval = self.FiducialsPass.exec_()

            return True


def check_duplicate(items):
    """Input a list and return True if there are repeats otherwise it returns False.
       
    This function checks the segement name array and selects for connected vertices.
    This is dependent on automatic fiducial naming in insertFiducialMarkers() method.
    """
    endpoint_names = []
    #break into endpoint names of the 2 segments comprising the angle
    for item in items:
        item1 = item[0:4]
        item2 = item[5:9]
        endpoint_names.append(item1)
        endpoint_names.append(item2)

    already_seen = []
    for i, j in enumerate(endpoint_names):
        if j in already_seen:
            return True
        already_seen.append(j)

    return False


def check_internal_angle(items):
    """Check if a certain combination of segments is an internal or external angle.
    
    This method uses the unique segment name to determine if the angle is external or internal. 
    Internal angles occur when the segment name has the following form:
    (1-2)-(1-3), where the number indicates a unique fiducial name.If the name has a form:
    (1-2)-(3-1), the angle is external and one must take (180-the angle) for consistency.
    This is dependent on automatic fiducial naming in insertFiducialMarkers() method.
    """
    endpoint_names = []
    #break into endpoint names of the 2 segments comprising the angle
    for item in items:
        item1 = item[0:4]
        item2 = item[5:9]
        endpoint_names.append(item1)
        endpoint_names.append(item2)

    if endpoint_names[0] == endpoint_names[3]:
        print('This was originally an external angle!')
        return False
    else:
        return True


def make_contour_list(self, *args):
    """Make a list of contours names to check."""
    for i in self.Contours:
        names = i.OfRoi.Name
        self.contour_list.append(names)


def make_POI_list(self, *args):
    """Make a list of POI names to check."""
    for i in self.Fiducials:
        names = i.OfPoi.Name
        self.fiducials_list.append(names)


def lookForGTV(self, *args):
    """Make a list of GTV-type ROIs."""
    print('looking for GTV volumes')
    for i in self.Contours:
        if (i.OfRoi.Type == 'Gtv') and (i.HasContours() == True):
            print(i.OfRoi.Name)
