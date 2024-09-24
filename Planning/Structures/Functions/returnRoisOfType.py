from connect import *

def returnRoisOfType(typesToInclude):
    '''Returs all structures of a selection of types iff they are contoures'''
    
    case = get_current("Case")
    pm   = case.PatientModel
    exam = get_current("Examination")
    ss   = pm.StructureSets[exam.Name]
    
    if not isinstance(typesToInclude, list):
        typesToInclude = [typesToInclude]
    
    typesToInclude = [x.lower() for x in typesToInclude]
        
    tmp = [structure for structure in ss.RoiGeometries if structure.HasContours()] #All contoured structures
    output = [structure.OfRoi.Name for structure in tmp if structure.OfRoi.Type.lower() in typesToInclude] #All contours with type in input parameter
    return output
    
    
if __name__ == "__main__":
    print(returnRoisOfType(["ptv","ctv","gtv"]))