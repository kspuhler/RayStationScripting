##Base class for adding default structures
##Author KDS
from connect import *


class StructureTemplate(object):
    ###Takes a list of tuples of form (name, color, type) and makes empty ROIsin patientModel


    def __init__(self, roiList, patientModel):
        self.roiList = roiList
        self._checkRoiList()
        self.pm = patientModel
        self._getRoisInPatientModel()



    def _checkRoiList(self):

        ##Will probably never be visible to end users just an internal check that we didn't goof up an RoiList 
        
        validColors = ["red", "blue", "white", "yellow", "green"]
        validTypes  = ["Gtv", "Ctv", "Ptv", "Organ", "Control"]
        for idx, tup in enumerate(self.roiList):
            if len(tup) != 3:
                raise Exception(f"ROI number {idx} does not have conforming structure of 3 entries (name, color, type)")
            #if not tup[1].lower() in validColors:
            #    raise Exception(f"ROI number {idx} with name {tup[0]} has invalid color {tup[1]}")
            #    return False
            if not tup[2] in validTypes:
                raise Exception(f"ROI number {idx} with name {tup[0]} has invalid type {tup[2]}")
                return False
        return True
    
    def _getRoisInPatientModel(self):
        
        self.roisInPatientModel = []
        for ii in self.pm.RegionsOfInterest:
            self.roisInPatientModel.append(ii.Name)
        print(self.roisInPatientModel)

    def make_empty_rois(self): 
        
        for ii in self.roiList:
            if not ii in self.roisInPatientModel:
                try:
                    self.pm.CreateRoi(Name = ii[0], Color = ii[1], Type = ii[2])
                except:
                    pass

if __name__ == '__main__':
    from roi_list_templates import *
    case = get_current("Case")
    pm = case.PatientModel
    test = StructureTemplate(prostSBRT, pm)
    test.make_empty_rois()
