
#Function to crop rectum from Spacer and any gtv structures
from connect import *

import sys


sys.path.append("\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
sys.path.append("F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")

from Planning.Structures.Functions.checkForContour import checkForContour



def cropXfromY(x = None, y = None, margin = None, patient_model = None, exam = None, make_derived = False, new_roi_name = False):
    
    #Deletes all of the structures in the list [y] from structure x, leaving them UNDERVIDED
    
    
    # margin can be left blank for zero, a float for uniform, or a list of [sup, inf, ant, post, right, left]
    
    if not patient_model:
        patient_model = get_current('Case')
        patient_model = patient_model.PatientModel
        
    if not exam:
        exam = get_current('Examination')
        
    if not type(y) == list:
        y = [y]

    if not margin:
        margin = 6*[0]
    elif not type(margin) == list:
        margin = 6*[margin]
    elif type(margin) == list and len(margin) != 6:
        raise Error("margin must be either blank, a float, or a list of [sup, inf, ant, post, right, left]")

        
    if not make_derived:
        patient_model.RegionsOfInterest[x].CreateAlgebraGeometry(Examination=exam, Algorithm="Auto",
                                                                        ExpressionA={ 'Operation': "Union", 'SourceRoiNames': [x], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, 
                                                                        ExpressionB={ 'Operation': "Union", 'SourceRoiNames': y, 'MarginSettings': { 'Type': "Expand", 'Superior': margin[0], 'Inferior': margin[1], 'Anterior': margin[2], 'Posterior': margin[3], 'Right': margin[4], 'Left': margin[5] } }, 
                                                                        ResultOperation="Subtraction", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })
        return
    
    elif make_derived:
        if not new_roi_name:
            raise Error("You need to provde a name for the new roi")
        tmp = patient_model.CreateRoi(Name=new_roi_name, Color="Purple", Type="Unknown", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)
        tmp.SetAlgebraExpression(Examination=exam, Algorithm="Auto",
                                                                        ExpressionA={ 'Operation': "Union", 'SourceRoiNames': [x], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, 
                                                                        ExpressionB={ 'Operation': "Union", 'SourceRoiNames': y, 'MarginSettings': { 'Type': "Expand", 'Superior': margin[0], 'Inferior': margin[1], 'Anterior': margin[2], 'Posterior': margin[3], 'Right': margin[4], 'Left': margin[5] } }, 
                                                                        ResultOperation="Subtraction", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })    

        tmp.UpdateDerivedGeometry(Examination=exam, Algorithm="Auto")
        return
    
def crop_spacer_from_rectum(rectum_name = "Rectum", spacer_name = "Spacer", margin = [0.1, 0.1, 0.3, 0, 0.2, 0.2]): #crop is a list of structures we will remove from rectum contour
    

    cropXfromY(x=rectum_name, y = spacer_name, margin = margin)
    return



# with CompositeAction('ROI algebra (Rectum)'):

#   case.PatientModel.RegionsOfInterest['Rectum'].CreateAlgebraGeometry(Examination=examination, Algorithm="Auto", ExpressionA={ 'Operation': "Union", 'SourceRoiNames': ["Rectum"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ExpressionB={ 'Operation': "Union", 'SourceRoiNames': ["Spacer"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ResultOperation="Subtraction", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })

#   # CompositeAction ends 


# with CompositeAction('ROI algebra (tmp)'):

#   retval_0 = case.PatientModel.CreateRoi(Name="tmp", Color="Orange", Type="Organ", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)

#   retval_0.SetAlgebraExpression(ExpressionA={ 'Operation': "Union", 'SourceRoiNames': ["Rectum"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ExpressionB={ 'Operation': "Union", 'SourceRoiNames': ["Spacer"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, ResultOperation="Subtraction", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })

#   retval_0.UpdateDerivedGeometry(Examination=examination, Algorithm="Auto")

#   # CompositeAction ends 

