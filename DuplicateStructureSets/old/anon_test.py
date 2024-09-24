from connect import get_current



def DICOM_export(path, ignore_precondition_warnings):

    clinic_db = get_current('ClinicDB')
    default_anonymization_options = clinic_db.GetSiteSettings().DicomSettings.DefaultAnonymizationOptions
    anonymization_settings = {'Anonymize': True,
                              'AnonymizedName': 'anonymizedName',
                              'AnonymizedID': 'anonymizedID',
                              'RetainDates': default_anonymization_options.RetainLongitudinalTemporalInformationFullDatesOption,
                              'RetainDeviceIdentity': default_anonymization_options.RetainDeviceIdentityOption,
                              'RetainInstitutionIdentity': default_anonymization_options.RetainInstitutionIdentityOption,
                              'RetainUIDs': default_anonymization_options.RetainUIDs,
                              'RetainSafePrivateAttributes': default_anonymization_options.RetainSafePrivateOption}

    case = get_current('Case')


    try:
        examination = get_current('Examination')
        structure_set = case.PatientModel.StructureSets[examination.Name]
        result = case.ScriptableDicomExport(ExportFolderPath = path,
                                            AnonymizationSettings = anonymization_settings,
                                            Examinations = [examination.Name],
                                            RtStructureSetsForExaminations = [examination.Name],
                                            DicomFilter = '',
                                            IgnorePreConditionWarnings = ignore_precondition_warnings)

        print("Success!")

    except Exception as error:
        print(error)
        raise error

if __name__ == '__main__':
    path = r"C:\Your\Path\Here"
    DICOM_export(path, True)
