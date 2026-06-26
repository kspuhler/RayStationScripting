import os
from connect import *
import pydicom as pdm
import glob




def test():
    
    fdir = '\\\Client\F$\SHARING\Radiation Oncology Physics\RayStationSPC\\'
    p = get_current("Patient")
    
    ct = pdm.read_file(fdir+'CT1.2.840.114358.14038002597876.20231116111514.2032907503995.87.dcm')
    print(ct.StudyID)

def get_all_ct(fdir):
    return glob.glob(os.path.join(fdir, "CT*dcm"))

def get_dose(fdir):
    return glob.glob(os.path.join(fdir, "RD*dcm"))

def get_plan(fdir):
    return glob.glob(os.path.join(fdir, "RP*dcm"))

def get_structure_set(fdir):
    return glob.glob(os.path.join(fdir, "RS*dcm"))

if __name__ == "__main__":
    

    pat = get_current("Patient")
    mrn = pat.PatientID
    
    currentCases = [c.CaseName for c in pat.Cases]
    
    CaseNameParam = None
    if not "SPC" in currentCases:
        CaseNameParam = "SPC"
    
    fdir = '\\\Client\F$\SHARING\Radiation Oncology Physics\RayStationSPC\\' 
    
    for idx, ii in enumerate(get_all_ct(fdir)):
        ct = pdm.read_file(ii)
        if idx >1:
            break
        
    dStudy = []
    dSeries = []
    for jj in get_dose(fdir):
        print('jj')
        print(jj)
        d = pdm.read_file(jj)
        dStudy.append(str(d.StudyInstanceUID))
        dSeries.append(str(d.SeriesInstanceUID))
        
        
    for kk in get_plan(fdir):
        print("kk")
        print(kk)
        p = pdm.read_file(kk)
    
    for ll in get_structure_set(fdir):
        s = pdm.read_file(ll)
        
        

    bsParameter = {'PatientID': str(mrn),
                   'StudyInstanceUID': str(ct.StudyInstanceUID),
                   'SeriesInstanceUID': str(ct.SeriesInstanceUID)}
    bsParameterDose = {'PatientID': str(mrn),
                   'StudyInstanceUID': dStudy,
                   'SeriesInstanceUID': dSeries}
    bsParameterPlan = {'PatientID': str(mrn),
                   'StudyInstanceUID': str(p.StudyInstanceUID),
                   'SeriesInstanceUID': str(p.SeriesInstanceUID)}
    bsParameterStruc = {'PatientID': str(mrn),
                   'StudyInstanceUID': str(s.StudyInstanceUID),
                   'SeriesInstanceUID': str(s.SeriesInstanceUID)}
    
    print("up in da  club")
    print(fdir)
    print(mrn)
    print(bsParameter)
    
    
    print(f"DEBUG argument for import is {[bsParameter, bsParameterDose, bsParameterPlan, bsParameterStruc]}")
    w=pat.ImportDataFromPath(Path = os.path.join(fdir), CaseName=None, SeriesOrInstances = [bsParameter, bsParameterDose, bsParameterPlan, bsParameterStruc])
    
    print("New Case Name")
    for c in pat.Cases:
        print(c.CaseName)
        if not c.CaseName in currentCases:
            c.CaseName = "SPC"
            break