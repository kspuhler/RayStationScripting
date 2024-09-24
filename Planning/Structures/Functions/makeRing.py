from connect import *
import sys
sys.path.append("\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
sys.path.append("F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
from Planning.Structures.Functions.checkForContour import checkForContour


def makeRing(radius, structure):
    #makes a ring of radius mm around structrure

    case = get_current("Case")
    examination = get_current("Examination")
    
    name = f'{structure}_Ring_{radius}cm'
    if checkForContour(name.lower()):
        case.PatientModel.RegionsOfInterest[name].DeleteRoi()
    
    
    r1 = radius
    r2 = r1 + 0.2
    

    
   
    retval_0 = case.PatientModel.CreateRoi(Name=name, Color="0, 255, 128", Type="Undefined", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)
    retval_0.SetAlgebraExpression(ExpressionA={ 'Operation': "Union", 'SourceRoiNames': [structure], 'MarginSettings': { 'Type': "Expand", 'Superior': r2, 'Inferior': r2, 'Anterior': r2, 'Posterior': r2, 'Right': r2, 'Left': r2 } }, ExpressionB={ 'Operation': "Union", 'SourceRoiNames': [structure], 'MarginSettings': { 'Type': "Expand", 'Superior': r1, 'Inferior': r1, 'Anterior': r1, 'Posterior': r1, 'Right': r1, 'Left': r1 } }, ResultOperation="Subtraction", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })
    retval_0.UpdateDerivedGeometry(Examination=examination, Algorithm="Auto")


if __name__ == '__main__':
    makeRing(.2, 'PTV_CK')
    makeRing(2.0, 'PTV_CK')

