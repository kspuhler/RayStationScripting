
try:
    from connect import *
except:
    pass

import sys

sys.path.append("\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
sys.path.append(r"F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")



###CONFIG

#case.PatientModel.CreateStructuresFromAtlas(SourceTemplate=db.TemplatePatientModels['aCyber MRI Haas Test'], SourceExaminationsNames=["1101346"], SourceRoiNames=["urethra"], SourcePoiNames=[], AssociateStructuresByName=False, TargetExamination=examination, NrOfFusionAtlases=15)


ATLAS_PARAMS = {'atlas_name': 'ProstateNodes Haas Test',
                'atlas_mrns': ["17622598", "12802972", "13490725", "12572656", "8957315", "1143702", "11912146", "16243828", "12541668", "10375426", "1473151", "12737576", "12775370", "11152963", "15210295", "12652739", "11303202", 
                               "14065197", "17496255", "2115637", "17548019", "12435874", "16333837", "9026878", "9535844", "12391953", "16302939", "12511634"],
                'atlas_rois': ["LtNode", "RtNode"],
                'number_of_fusions': 15}
                
######

if __name__ == "__main__":
    

    case = get_current("Case")
    db = get_current ("PatientDB")
    bs = get_current("BeamSet")
    
    sim = bs.GetPlanningExamination()
    
    atlas = db.LoadTemplatePatientModel(templateName=ATLAS_PARAMS['atlas_name'])
    
    

    set_progress('Running atlas segmentation...', percentage = -1)
    case.PatientModel.CreateStructuresFromAtlas(SourceTemplate=atlas, 
                                                SourceExaminationsNames=ATLAS_PARAMS['atlas_mrns'], 
                                                SourceRoiNames=ATLAS_PARAMS['atlas_rois'] ,
                                                SourcePoiNames=[], AssociateStructuresByName=True, TargetExamination=sim, NrOfFusionAtlases=ATLAS_PARAMS['number_of_fusions'])
    
    

    
    #await_user_input(f"Done. Please copy urethra onto planning CT scan and advance carepath.")
    
    sys.exit()
    
    
    