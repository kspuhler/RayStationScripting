""" 
set_max_mlc_jaws\copy_beam_set.py

Designed to copy a beam set for a Varian machine.

Created on Tue Apr  1 15:09:41 2025

@author: clanco01
"""

from connect import *
import sys

# Add path to import machine names
sys.path.append("\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
from RSutil.variables import VARIAN_MACHINES

class CopyBeamSet:
    
    def __init__(self, beam_set, plan, exam_name):
        
        self.plan = plan
        self.beam_set = beam_set
        self.base_name = self.beam_set.DicomPlanLabel
        self.max_name_length = 16
        self.exam_name = exam_name
        
        # Check if it is a Varian machine
        if self.beam_set.MachineReference.MachineName not in VARIAN_MACHINES:
            await_user_input("Machine in beam set is not a Varian machine.  Not supported.")
            exit()
        
        # Create default settings for MTS settings
        self.mts_settings={ 'DisplayName': None, 'MotionSynchronizationSettings': None, 
                           'RespiratoryIntervalTime': None, 'RespiratoryPhaseGatingDutyCycleTimePercentage': None, 
                           'MotionSynchronizationTechniqueType': "Undefined" }
        
        # Get a unique beam set name
        existing_beam_set_names = [beam_set.DicomPlanLabel for beam_set in self.plan.BeamSets]
        print(f"Existing Beam Set Names: {existing_beam_set_names}")
        self.beam_set_name = self.base_name
        count = 1
        while self.beam_set_name in existing_beam_set_names:
            suffix = f"_{count}"
            num_chr_suffix = len(suffix)
            if len(self.base_name) > self.max_name_length - num_chr_suffix:
                index = self.max_name_length - num_chr_suffix
                self.beam_set_name = f"{self.base_name[:index]}{suffix}"
            else:
                self.beam_set_name = f"{self.base_name}{suffix}"
            count += 1
        
        # Get the tolerance table if exists
        try:
            self.tolerance = beam_set.PatientSetup.ToleranceTable.ToleranceTableLabel
        except:
            self.tolerance = None
            
        # Create new beam set    
        beam_set_new = self.plan.AddNewBeamSet(Name=self.beam_set_name, 
                                ExaminationName=self.exam_name, 
                                MachineName=self.beam_set.MachineReference.MachineName, 
                                Modality=self.beam_set.Modality, 
                                TreatmentTechnique=self.beam_set.GetTreatmentTechniqueType(), 
                                PatientPosition=self.beam_set.PatientPosition, 
                                NumberOfFractions=self.beam_set.FractionationPattern.NumberOfFractions, 
                                CreateSetupBeams=False, 
                                UseLocalizationPointAsSetupIsocenter=False, 
                                UseUserSelectedIsocenterSetupIsocenter=False, 
                                Comment="", 
                                RbeModelName=None, 
                                EnableDynamicTrackingForVero=False, 
                                NewDoseSpecificationPointNames=[], 
                                NewDoseSpecificationPoints=[], 
                                MotionSynchronizationTechniqueSettings=self.mts_settings, 
                                Custom=None, 
                                ToleranceTableLabel=self.tolerance)
        
        # Copy each beam to new beam set
        for beam in beam_set.Beams:
            beam_set_new.CopyBeamsFromBeamSet(BeamSetToCopyFrom=beam_set, BeamsToCopy=[beam.Name])
        
        
        # Set new beam set to current
        get_current("Patient").Save()
        beam_set_new.SetCurrent()       
