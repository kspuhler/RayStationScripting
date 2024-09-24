from connect import *


class MachinePreplan(object):
    
    def __init__(self, case, exam, beamSet=None):
        
        self.db   = get_current("PatientDB")
        self.case = case
        self.exam = exam
        if beamSet:
            self.beamSet = beamSet
        
        
        self.addCouchStructures()
    
        


class TrueBeamPrePlan(MachinePreplan):
    
    def __init__(self, case, exam, beamSet):
        super().__init__(case=case, exam=exam, beamSet=beamSet)
        

    
    def addCouchStructures(self):
        if not self.beamSet.DeliveryTechnique == '3D-CRT':
            template = self.db.LoadTemplatePatientModel(templateName = 'TB Couch Clinical - Rails In', lockMode='Read')
            self.case.PatientModel.CreateStructuresFromTemplate(SourceTemplate=template, SourceExaminationName="CT 1", 
                                                           SourceRoiNames=["CouchInterior", "CouchRailRight_In", "CouchRailLeft_In", "CouchSurface"], SourcePoiNames=[],
                                                           AssociateStructuresByName=True, TargetExamination=self.exam, InitializationOption="AlignImageCenters")
        elif self.beamSet.DeliveryTechnique == '3D-CRT':
            self.case.PatientModel.CreateStructuresFromTemplate(SourceTemplate=self.db.TemplatePatientModels['TB Couch Clinical - Rails Out'], SourceExaminationName="CT 1", 
                                                           SourceRoiNames=["CouchInterior", "CouchRailRight_Out", "CouchRailLeft_Out", "CouchSurface"], SourcePoiNames=[],
                                                           AssociateStructuresByName=True, TargetExamination=self.exam, InitializationOption="AlignImageCenters")

class RadixactPrePlan(MachinePreplan):
    
    def __init__(self, case, exam):
        
        super().__init__(case, exam)
        
        
    def addCouchStructures(self):
        self.case.PatientModel.CreateStructuresFromTemplate(SourceTemplate=db.TemplatePatientModels['Radixact Couch'], SourceExaminationName="CT 1", SourceRoiNames=["Lower pallet", "Upper pallet", "couch center Radixact"], 
                                                       SourcePoiNames=[], AssociateStructuresByName=True, TargetExamination=self.exam, InitializationOption="AlignImageCenters")
    
    def setPitch(self, target): 
        pass
    
if __name__ == "__main__":
    from connect import *
    case = get_current("Case")
    exam = get_current("Exam")
    bs = get_current("BeamSet")
    