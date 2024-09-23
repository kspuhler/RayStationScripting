from connect import *
import sys
sys.path.append("\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
sys.path.append("F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")

from Planning.Structures.Functions.checkForContour import checkForContour
from Planning.Structures.Functions.tryDefaultRoiName import tryDefaultRoiName
from RSutil.variables import OPT_STRUCTURE_COLOR


def fiducialAutoContour(roiName):
    
        """Use the RS thresholding tool to identify fiducials in patient.
        
        This will search the entire CT for objects with a 3071 HU value in the vicinity of roiName, and 
        contour those objects. It then booleans the fiducial contour with the
        fiducial ROI contour 
        """
        
        FIDUCIAL_ROI_NAME = "Fiducial-Markers"
        
        case = get_current('Case')
        pm   = case.PatientModel 
        exam = get_current('Examination')
        
        searchRoi = tryDefaultRoiName(roiName=roiName, needsGeometry=True, fallback=True)
        
        if checkForContour(FIDUCIAL_ROI_NAME, caseSensitive=(True)):
            
            
            fids = pm.RegionsOfInterest['Fiducial-Markers']
            fids.GrayLevelThreshold(Examination=exam, LowThreshold=1800,
                                        HighThreshold=3071,
                                        PetUnit="",
                                        CbctUnit=None,
                                        BoundingBox=None)

            fids.CreateAlgebraGeometry(Examination=exam, Algorithm="Auto",
                                           ExpressionA={'Operation': "Union",
                                                        'SourceRoiNames': [FIDUCIAL_ROI_NAME],
                                                        'MarginSettings': {'Type': "Expand",
                                                                           'Superior': 0,
                                                                           'Inferior': 0,
                                                                           'Anterior': 0,
                                                                           'Posterior': 0,
                                                                           'Right': 0, 'Left': 0}},
                                           ExpressionB={'Operation': "Union", 'SourceRoiNames': [searchRoi],
                                                        'MarginSettings': {'Type': "Expand",
                                                                           'Superior': 3.0,
                                                                           'Inferior': 3.0,
                                                                           'Anterior': 3.0,
                                                                           'Posterior': 3.0,
                                                                           'Right': 3.0,
                                                                           'Left': 3.0}},
                                           ResultOperation="Intersection",
                                           ResultMarginSettings={'Type': "Expand",
                                                                 'Superior': 0,
                                                                 'Inferior': 0,
                                                                 'Anterior': 0,
                                                                 'Posterior': 0,
                                                                 'Right': 0,
                                                                 'Left': 0})
        
        else:
            fids = pm.CreateRoi(Name=FIDUCIAL_ROI_NAME, Color=OPT_STRUCTURE_COLOR,
                                                        Type="Marker", TissueName=None,
                                                        RbeCellTypeName=None, RoiMaterial=None)

            fids.GrayLevelThreshold(Examination=exam, LowThreshold=1800,
                                        HighThreshold=3071,
                                        PetUnit="",
                                        CbctUnit=None,
                                        BoundingBox=None)

            fids.CreateAlgebraGeometry(Examination=exam, Algorithm="Auto",
                                           ExpressionA={'Operation': "Union",
                                                        'SourceRoiNames': [FIDUCIAL_ROI_NAME],
                                                        'MarginSettings': {'Type': "Expand",
                                                                           'Superior': 0,
                                                                           'Inferior': 0,
                                                                           'Anterior': 0,
                                                                           'Posterior': 0,
                                                                           'Right': 0, 'Left': 0}},
                                           ExpressionB={'Operation': "Union", 'SourceRoiNames': [searchRoi],
                                                        'MarginSettings': {'Type': "Expand",
                                                                           'Superior': 3.0,
                                                                           'Inferior': 3.0,
                                                                           'Anterior': 3.0,
                                                                           'Posterior': 3.0,
                                                                           'Right': 3.0,
                                                                           'Left': 3.0}},
                                           ResultOperation="Intersection",
                                           ResultMarginSettings={'Type': "Expand",
                                                                 'Superior': 0,
                                                                 'Inferior': 0,
                                                                 'Anterior': 0,
                                                                 'Posterior': 0,
                                                                 'Right': 0,
                                                                 'Left': 0})
        
        #Delete fiducial ROI if nothing was found
        
        if not pm.StructureSets[exam.Name].RoiGeometries[FIDUCIAL_ROI_NAME].HasContours():
            try:
                fids.DeleteRoi()
            except:
                pass
            
        return 


if __name__ == "__main__":
    fiducialAutoContour(["PTV4500", "PTVp", "MDGTV", "Prostate", "GTVp"])