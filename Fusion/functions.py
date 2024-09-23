from connect import *

def makeBoxRoi():

    case = get_current("Case")
    exam = get_current("Examination")
    
    try:
        p = case.PatientModel.StructureSets[exam.Name].PoiGeometries['Localization point'].Point
    except:
        print('*************CANNOT FIND LOCALIZATION POINT *****************')
        return False
    
    box = case.PatientModel.CreateRoi(Name="zzFuzeBox", Color="Magenta", Type="Undefined", TissueName=None, RbeCellTypeName=None, RoiMaterial=None)
    box.CreateBoxGeometry(Size={ 'x': 10, 'y': 10, 'z': 10 }, Examination=exam, Center=p, Representation="TriangleMesh", VoxelSize=None)
    return

  # CompositeAction ends 



def findCkMRI():
    pass