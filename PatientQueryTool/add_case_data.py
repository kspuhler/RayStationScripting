# -*- coding: utf-8 -*-
"""
Created on Fri Jan 23 13:30:10 2026

@author: spuhlk01
"""

# PatientQueryTool/main.py
import sys

sys.path.append(r"\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
sys.path.append(r"F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")

from PatientQueryTool.access.ray_repository import RayRepository
from PatientQueryTool.engine.executor import execute_physician_alias_query
from Planning.Structures.Functions.checkForContour import checkForContour

try:
    from connect import *
except:
    pass

import pickle


def run(recovery = True):
    
    
    
    ###CONFIG###
    
    physician_key = "Tam"
    tag_site = "Abdomen"
    
    DUMP_NAME = physician_key+"_"+tag_site
    DUMP_NAME = DUMP_NAME.upper()
    
    pkl_out = r"\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD\PatientQueryTool\pickles"
    pkl_out = os.path.join(pkl_out, f'{DUMP_NAME}.pkl')
    
    # CONTOURS_TO_PARSE{'Pelvis': ['Rectum', 'Bladder', 'PTV4500'],
    #                   'Breast': ['PTV_Tangents', 'tumorbed', 'tumor bed', 'PTV Tangents', 'PTVTangents'],
    #                   'Lung': [],
    #                   'HeadNeck': ['PTV6996', 'PTV5940', 'PTV5412', 'PTV_6996', 'PTV_5940', 'PTV_5412'. ]}
    
    ##########
    #RUNTIME
    
    
    pd = get_current("PatientDB")
    ray_repository = RayRepository()

    base_filter   = {}#{'Gender': 'Male'}      # add AND constraints here, e.g. {"Gender": "Female"}
    

    records = execute_physician_alias_query(
        ray_repository=ray_repository,
        base_filter=base_filter,
        physician_key=physician_key,
        use_index_service=True,
        return_records=True,
    )

    print("Matches:", len(records))
    processed = []
    fail = []
    
    if recovery:
        file = open(pkl_out,'rb')
        processed, fail = pickle.load(file)
        print(f'Recovered {[x for x in processed]}')
      
    
    for idx, record in enumerate(records):
        
        if record['PatientID'] in processed:
            print('Skipping')
            continue
        print(f'Processing patient {idx} out of {len(records)}')
        try:
        	pd.LoadPatient(PatientInfo = record)
        except:
        	pass
        try:
        	patient = get_current("Patient")
        except:
        	continue
        cases = patient.Cases
        
        for c in cases:
            if any(x.lower() in c.CaseName.lower() for x in ["DNU", "TEST"]):
                continue
            c.SetCurrent()
            if not c.BodySite:
                #if checkForContour("PTV4500") or checkForContour("MDGTV") or checkForContour("Bladder") or checkForContour("Rectum"): #SUCCESS
                #    c.BodySite = "Pelvis"
                if checkForContour("Stomach") and checkForContour("Esophagus") and checkForContour("Liver"):
                    
                    c.BodySite = tag_site

                #elif checkForContour("Brain"):
                #    c.BodySite = "Brain"
              #  else:
              #      c.BodySite = "Unknown"
              #      fail.append(record['PatientID'])
                    
            patient.Save()
            processed.append(record['PatientID'])

            if idx%20 == 0:
                with open(pkl_out, 'wb') as f:  # Python 3: open(..., 'wb')
                    pickle.dump([processed, fail], f)
        
    
    

run()
