from connect import *
import sys
sys.path.append("\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
sys.path.append("F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
from Planning.Structures.Templates.oar_list_definitions import skin as skinDef
from Planning.Structures.Functions.checkForContour import checkForContour



def makeSkin():
    
    case = get_current("Case")
    examination = get_current("Examination")

    if  checkForContour('skin'):
    
        try:
            case.PatientModel.RegionsOfInterest['Skin'].DeleteRoi()
        except:
            case.PatientModel.RegionsOfInterest['skin'].DeleteRoi()
    else:
        pass
        
    if not checkForContour('external'):
        ext = case.PatientModel.CreateRoi(Name="External", Color="Green", Type="External", TissueName="", RbeCellTypeName=None, RoiMaterial=None)
        ext.CreateExternalGeometry(Examination=examination, ThresholdLevel=-250)

    skin = case.PatientModel.CreateRoi(Name=skinDef[0], Color=skinDef[1], Type=skinDef[2], TissueName=None, RbeCellTypeName=None, RoiMaterial=None)
    skin.SetAlgebraExpression(ExpressionA={ 'Operation': "Union", 'SourceRoiNames': ["External"], 'MarginSettings': { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 } }, 
                                  ExpressionB={ 'Operation': "Union", 'SourceRoiNames': ["External"], 'MarginSettings': { 'Type': "Contract", 'Superior': 0.3, 'Inferior': 0.3, 'Anterior': 0.3, 'Posterior': 0.3, 'Right': 0.3, 'Left': 0.3 } }, 
                                  ResultOperation="Subtraction", ResultMarginSettings={ 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 })
    skin.UpdateDerivedGeometry(Examination=examination, Algorithm="Auto")


if __name__ == '__main__':
    makeSkin()