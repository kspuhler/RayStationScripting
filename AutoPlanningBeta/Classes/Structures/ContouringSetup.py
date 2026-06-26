import sys
sys.path.append("\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
sys.path.append("F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")


from connect import *
from RSutil.variables import TRUEBEAMS, RADIXACTS, CYBERKNIFES

class ContouringSetup(object):
    
    #default parameters that can be replaced in kwargs
    _defaults = {"interactive":True, #Promopt user to edit structures
                 "autoUpdateDerived":True, #make sure derived structures update on destruct
                 "templateName": None, #template to load
                 "templateStuctures": None, #rois whichw e will load off of the template
                 "machine": None} #tx machine 
    
    def __init__(self, *args, **kwargs):
        #processing kwargs
        self.db = get_current("PatientDB")
        self.case = get_current("Case")
        self.exam = get_current("Examination")
        
        attributes = self._defaults.copy()
        attributes.update(kwargs)
        self._process_kwargs(attributes)
        
        self.switchRsUi()
        self.loadSupportStructures()
        self.loadStructureTemplate()
        

    def _process_kwargs(self, attributes):
        for key, value in attributes.items():
            if key in self._defaults:
                setattr(self, key, value)
            else:
                setattr(self, key, value)
                print(f"Warning: Unknown attribute '{key}'")
        return
    
    def switchRsUi(self):
        #move user view to contouring window
        ui = get_current("ui")
        ui.ToolPanel.TabItem['ROIs'].Select()
        ui.TitleBar.Navigation.MenuItem["Patient modeling"].Button.Click()
        
    def loadSupportStructures(self):
        if not(self.machine):
            print("NO MACHINE!")
        print(self.machine.lower())
        print([x.lower() for x in TRUEBEAMS])
        if self.machine.lower()  in [x.lower() for x in TRUEBEAMS]:
            support = self.db.LoadTemplatePatientModel(templateName="TB Couch Clinical - Rails In")
            self.case.PatientModel.CreateStructuresFromTemplate(SourceTemplate=support, 
                                                           SourceExaminationName="CT 1", 
                                                           SourceRoiNames=["CouchRailLeft_In", "CouchSurface", "CouchRailRight_In", "CouchInterior"],
                                                           SourcePoiNames=[], 
                                                           AssociateStructuresByName=True, 
                                                           TargetExamination=self.exam, 
                                                           InitializationOption="AlignImageCenters")
        elif self.machine.lower() in [x.lower() for x in RADIXACTS]:
            support = self.db.LoadTemplatePatientModel(templateName="Radixact Couch")
            self.case.PatientModel.CreateStructuresFromTemplate(SourceTemplate=support, 
                                                                SourceExaminationName="CT 1", 
                                                                SourceRoiNames=["Lower pallet", "Upper pallet", "couch center Radixact"], 
                                                                SourcePoiNames=[], 
                                                                AssociateStructuresByName=True, 
                                                                TargetExamination=self.exam, 
                                                                InitializationOption="AlignImageCenters")
        elif self.machine.lower() in [x.lower() for x in CYBERKNIFES]:
            support = self.db.LoadTemplatePatientModel(templateName="Cyberknife_DNE")
            self.case.PatientModel.CreateStructuresFromTemplate(SourceTemplate=support, 
                                                                SourceExaminationName="CYBER PROSTATE", 
                                                                SourceRoiNames=["zDNEPosterior"], 
                                                                SourcePoiNames=[], 
                                                                AssociateStructuresByName=True, 
                                                                TargetExamination=self.exam, 
                                                                InitializationOption="AlignImageCenters")            
            
    def loadStructureTemplate(self):
        
        self.assembleSourceRoiNames()
        
        structures = self.db.LoadTemplatePatientModel(templateName=self.templateName)
        self.case.PatientModel.CreateStructuresFromTemplate(SourceTemplate=structures, 
                                                            SourceExaminationName=None, 
                                                            SourceRoiNames=self.templateStuctures, 
                                                            SourcePoiNames=[], 
                                                            AssociateStructuresByName=True, 
                                                            TargetExamination=self.exam, 
                                                            InitializationOption="EmptyGeometries")
        
        for roi in self.templateStuctures:
            if self.case.PatientModel.RegionsOfInterest[roi].DerivedRoiExpression:
                try:
                    self.case.PatientModel.RegionsOfInterest[roi].UpdateDerivedGeometry(Examination = self.exam)
                except:
                    pass
    
    def assembleSourceRoiNames(self):
        remove = []
        for roi in  self.case.PatientModel.StructureSets[self.exam.Name].RoiGeometries:
            if roi.HasContours():
                remove.append(roi.OfRoi.Name)
        self.templateStuctures = [x for x in self.templateStuctures if x not in remove]
        
    def __del__(self):
        if self.autoUpdateDerived:
            for roi in self.case.PatientModel.RegionsOfInterest:
                if roi.DerivedRoiExpression: #and not roi.Name == "zNTO":
                    try:
                        roi.UpdateDerivedGeometry(Examination = self.exam)
                    except:
                        pass            
        
        
#   Selected patient: ...

# from connect import *

# case = get_current("Case")
# examination = get_current("Examination")
# db = get_current("PatientDB")


# case.PatientModel.CreateStructuresFromTemplate(SourceTemplate=db.TemplatePatientModels['TB Couch Clinical - Rails In'], SourceExaminationName="CT 1", SourceRoiNames=["CouchRailLeft_In", "CouchSurface", "CouchRailRight_In", "CouchInterior"], SourcePoiNames=[], AssociateStructuresByName=True, TargetExamination=examination, InitializationOption="AlignImageCenters")
            
        
if __name__ == "__main__":
    a = ContouringSetup(machine="Truebeam", templateName= "PLAN TEMPLATE: JH ProstLN 4500",
                  templateStuctures= ["PTV4500", "Bladder", "Rectum", "Lt Femoral", "Rt Femoral", "PTVn", "PTVp", "Bowel", "Bladder - GTVp", "Spacer", "zXRectum", "zXBladder", "zXBowel", "zZRectum", "zZBladder", "zZBowel", "Shell1", "zNTO", "zRectum50"]
          )       