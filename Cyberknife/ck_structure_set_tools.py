# -*- coding: 
    
from connect import *
import sys
sys.path.append(r"\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
sys.path.append(r"F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")


from Planning.Structures.Functions.checkForContour import checkForContour


def make_spine_tracking_volume():
    
    case = get_current("Case")
    exam = get_current("Examination")
    pm = case.PatientModel


    #exam.RunDeepLearningSegmentationComposite(ExaminationsAndRegistrations={ exam.Name: None }, ModelNamesAndRoisToInclude={ 'RSL DLS Head and Neck CT': ["SpinalCord"] })


    if not checkForContour("Spine_Tracking_Vol"):

        case.PatientModel.CreateRoi(Name="Spine_Tracking_Vol", Color="Fuchsia", Type="Undefined", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)

    with CompositeAction('ROI algebra (Spine_Tracking_Vol)'):

        tracking = case.PatientModel.RegionsOfInterest['Spine_Tracking_Vol'].SetAlgebraExpression(ExpressionA={ 'Operation': "Union", 'SourceRoiNames': ["SpinalCord"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 4, 'Posterior': 3, 'Right': 3, 'Left': 3 } }, 
                                                                                              ExpressionB={ 'Operation': "Union", 'SourceRoiNames': [x.Name for x in pm.RegionsOfInterest if x.Type.lower()=='ptv'], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, 
                                                                                              ResultOperation="Subtraction", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })
        tracking.UpdateDerivedGeometry(Examination=exam, Algorithm="Auto")


if __name__ == "__main__":
    make_spine_tracking_volume()