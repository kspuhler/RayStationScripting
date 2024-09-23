"""
Created on Tue Mar 19 11:20:37 2024.

This script seeks to emulate the Eclipse functionality which allows a user to duplciate a structure set on a CT
and associate that new structure set with an existing plan.
@author: santoj14
"""

import os
import sys
import shutil
import pydicom

sys.path.append("F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD\DicomExport")
sys.path.append("\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD\DicomExport")

from connect import *

from DicomExportBase import DicomExportBase

#Get filepath to export

fPathBase_dup = '\\\Client\F$\SHARING\Radiation Oncology Physics\Raystation Duplicate Structure Sets\\'


class Duplicate_SS(DicomExportBase):
    """
    A class that provides the methods to import an anonymized CT and stucture set and re-import it into the patient.
    
    The user can then copy an existing plan onto the new CT and make an alternate plan for comparison.
    This class inherits a home-grown DicomExportBase class.
    """

    def __init__(self, fPathBase=fPathBase_dup):
        super().__init__(fPathBase)

    def assembleFilePath(self):
        """Build some file paths."""
        self.exportPath = os.path.join(self.fPath, self.mrn)
        print(self.exportPath)
        if not os.path.exists(self.exportPath):
            os.makedirs(self.exportPath)

    def runExport(self):
        """Export the anonymized CT and structure set to a pre-determined directory for re-import into RS."""
        clinic_db = get_current('ClinicDB')
        default_anonymization_options = clinic_db.GetSiteSettings().DicomSettings.DefaultAnonymizationOptions
        anonymization_settings = {'Anonymize': True,
                                  'AnonymizedName': 'Duplicate',
                                  'AnonymizedID': self.mrn + '_Duplicate',
                                  'RetainDates': default_anonymization_options.RetainLongitudinalTemporalInformationFullDatesOption,
                                  'RetainDeviceIdentity': default_anonymization_options.RetainDeviceIdentityOption,
                                  'RetainInstitutionIdentity': default_anonymization_options.RetainInstitutionIdentityOption,
                                  'RetainUIDs': default_anonymization_options.RetainUIDs,
                                  'RetainSafePrivateAttributes': default_anonymization_options.RetainSafePrivateOption}
        try:
            self.case.ScriptableDicomExport(AnonymizationSettings=anonymization_settings,
                                            ExportFolderPath=self.exportPath,
                                            Examinations=[self.exam.Name],
                                            RtStructureSetsForExaminations=[self.exam.Name],
                                            IgnorePreConditionWarnings=True)
        except Exception as error:
            print(error)
            raise error

    def getUIDinfo(self):
        """Get the anonymized UID info for re-import into RS."""
        first_file = os.listdir(self.exportPath)[0]
        if first_file.endswith(".dcm"):
            ds = pydicom.filereader.dcmread(self.exportPath + '\\' + first_file)
            print('Getting UID info from:', first_file, '......')
            self.StudyInsUID = str(ds.StudyInstanceUID)
            self.SeriesInsUID = str(ds.SeriesInstanceUID)

    def runImport(self):
        """re-import the anonymized CT and structure set to into RS."""
        print('Re-importing planning CT as a duplicate image set and structure set')
        self.getUIDinfo()
        print('StudyUID:', self.StudyInsUID)
        print('SeriesUID:', self.SeriesInsUID)
        import_path = str(self.exportPath)
        impID = self.patient.PatientID + '_Duplicate'
        print('Importing Duplicate CT into patient:', self.patient.PatientID)
        print('Looking for patient exported as:', impID)

        self.patient.ImportDataFromPath(Path=import_path,
                                        CaseName=self.case.CaseName,
                                        AllowMismatchingPatientID=True,
                                        SeriesOrInstances=[{'PatientID': impID,
                                                            'StudyInstanceUID': self.StudyInsUID,
                                                            'SeriesInstanceUID': self.SeriesInsUID}])
        print('Cleaning up...')
        shutil.rmtree(import_path)

    def fuse_duplicate_to_original(self):
        """Fuse the original CT and anonymized CT in order to be able to copy a plan."""
        self.case.CreateNamedIdentityFrameOfReferenceRegistration(FromExaminationName="CT 1",
                                                                  ToExaminationName="left prone breast",
                                                                  RegistrationName="Duplicate-to-Original",
                                                                  Description=None)


if __name__ == "__main__":
    tmp = Duplicate_SS(fPathBase_dup)
    #tmp.runImport()
