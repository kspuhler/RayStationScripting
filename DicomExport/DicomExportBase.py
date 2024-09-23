import os
try:
    from connect import *
except:
    pass

class DicomExportBase(object):
    """Generic base class for dicom exports
    
    Configure by giving a custom filepath fPath to where it will push
    
    default behavior pushes to fPath/mrn/
    """

    def __init__(self, fPath) -> None:
        self.fPath = fPath
        self.getCurrent()
        self.assembleFilePath()
        self.runExport()
        

    def getCurrent(self):

        self.patient     = get_current('Patient') 
        self.mrn         = self.patient.PatientID
        self.case        = get_current('Case')
        self.plan        = get_current('Plan')
        self.exam        = get_current('Examination')

    def assembleFilePath(self):
        #Default behavior to write it to F/path/to/$fPath/$mrn
        self.exportPath = os.path.join(self.fPath, self.mrn)
        print(self.exportPath)
        if not os.path.exists(self.exportPath):
            os.makedirs(self.exportPath)

    def chooseDataToExport(self):

        raise NotImplementedError

    def runExport(self):
        print("Do not run DicomExportBase")
        raise NotImplementedError
    
    
