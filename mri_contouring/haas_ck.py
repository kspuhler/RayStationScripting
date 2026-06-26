try:
    from connect import *
except:
    pass

import sys

sys.path.append("\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
sys.path.append(r"F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")

from RSutil.CommonLibrary.Classes.RsNavigator import RsNavigator


###CONFIG

#case.PatientModel.CreateStructuresFromAtlas(SourceTemplate=db.TemplatePatientModels['aCyber MRI Haas Test'], SourceExaminationsNames=["1101346"], SourceRoiNames=["urethra"], SourcePoiNames=[], AssociateStructuresByName=False, TargetExamination=examination, NrOfFusionAtlases=15)

ATLAS_PARAMS = {'atlas_name': 'Cyber MRI Haas Test',
                'atlas_mrns': ["1101346", "10312023", "13212514", "14416557", "9706691", "17722824", "9120031", "17409914", "14542897", "17712347", "17614241", "9354426", "14728963", "17633505", 
                                         "13569971", "12426536", "15830932", "9367265", "10337362", "6301809", "15607582", "9887325", "9142015", "0730927", "15285065", "17066786", "976259", "17644161", "15239363", 
                                         "17300166", "17414002", "11747579", "15239247", "2240953", "12734830", "0641743", "14582045", "12303874", "12465506", "17635379", "12604772", "5144510", "5159590"],
                'atlas_rois': ["urethra"],
                'number_of_fusions': 15}
                
######

# def load_and_return_atlas(name):
#     db = get_current("PatientDB")
#     return LoadTemplatePatientModel(templateName=name)

def get_ck_mri(case, acceptable_protocol_names = ["AX T2 CYBERKNIFE", "AX T2"]):
    
    for ii in case.Examinations:
        if hasattr(ii, 'EquipmentInfo'):
            if ii.EquipmentInfo.Modality == "MR":
                if ii.GetProtocolName() in acceptable_protocol_names:
                    return ii
                

if __name__ == "__main__":
    

    case = get_current("Case")
    db = get_current ("PatientDB")
    try:
        bs = get_current("BeamSet")
    except:
        await_user_input("YOU MUST HAVE THE SIM BEAMSET OPEN!\n Please open and re-run!")
    
    
    sim = bs.GetPlanningExamination()
    
    atlas = db.LoadTemplatePatientModel(templateName=ATLAS_PARAMS['atlas_name'])
    
    
    try:
        mri = get_ck_mri(case)
        mri.SetPrimary()
    except: 
        print('DEBUG: CANNOT FIND MRI') #handling for user to set mri to primary and continue
    
    #Make external on MRI
    case.PatientModel.RegionsOfInterest['External'].CreateExternalGeometry(Examination=mri, ThresholdLevel=20)
    set_progress('Running atlas segmentation...', percentage = -1)
    case.PatientModel.CreateStructuresFromAtlas(SourceTemplate=atlas, 
                                                SourceExaminationsNames=ATLAS_PARAMS['atlas_mrns'], 
                                                SourceRoiNames=ATLAS_PARAMS['atlas_rois'] ,
                                                SourcePoiNames=[], AssociateStructuresByName=True, TargetExamination=mri, NrOfFusionAtlases=ATLAS_PARAMS['number_of_fusions'])
    
    
    ui = RsNavigator()
    ui.switch_tab(tab_go_to='Structure definition')
    ui.switch_sub_tab(sub_tab_go_to = "ROI tools")
    
    #await_user_input(f"Done. Please copy urethra onto planning CT scan and advance carepath.")
    sim.SetPrimary()
    
    while True:
        urethra_on_ct = case.PatientModel.StructureSets[sim.Name].RoiGeometries['urethra'].HasContours()
        if urethra_on_ct:
            break
        await_user_input("Please copy urethra onto CT sim before exiting. Press play when copied to exit.")
    
    case.PatientModel.StructureSets[mri.Name].RoiGeometries['urethra'].DeleteRoiGeometry()
    
    sys.exit()
    
    
    