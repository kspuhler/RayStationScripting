import sys

sys.path.append("F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
sys.path.append("\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")

#from variables import ACCURAY_MACHINES, VARIAN_MACHINES



def getPlanFromPlanName():
    
    return


def interpretCTSimOrientation(exam):
    #Input: Raystation examination (namely CT Sim)
    #Return: HFS turned into HeadFirstSupine etc
    
    tmp = exam.PatientPosition
    if tmp == 'HFS':
        return 'HeadFirstSupine'
    
    elif tmp == 'HFP':
        return 'HeadFirstProne'
    
    elif tmp == 'FFP':
        return 'FeetFirstProne'
    
    elif tmp == 'FFS':
        return 'FeetFirstSupine'
        
    else:
        return False
    
    
def genPlanNameUnique(case, name, idx = 0):
    #checks if name is unqiue and appends _x if not
    print('genPlanNameUnique is deprecated, refactor to genUniqueName()')
    plans = [x.Name for x in case.TreatmentPlans]
    
    if not name in plans:
        return name
    else:
        return genPlanNameUnique(case, f"{name}_{idx + 1}", idx + 1)
        
    
def genUniqueName(collection, name, idx = 0):
    #checks if name is unqiue and appends _x if not
    hold = name    
    if not name in collection:
        return name
    else:
        while name in collection:
            idx += 1
            name = hold + '_' + str(idx)
        return name

