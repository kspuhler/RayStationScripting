# -*- coding: utf-8 -*-
"""Creates a verification plan per beam set.  The QA plan and dose are exported to 
the IMRT QA folder.  If the verification plan is a Radixact plan, the QA plan is exported
to the iDMS via Raygateway.  User can apply shifts.

version 1.0

Created on Mon Mar  10 8:17 2025

@author: clanco01
"""

import os
import json
import tkinter as tk
from tkinter import messagebox
from connect import get_current, set_progress, await_user_input
import sys
from time import sleep
import math

# Add path to import machine names
sys.path.append("\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
from RSutil.variables import RADIXACTS, VARIAN_MACHINES


class CreateAndExportQAPlan:
    
    def __init__(self):
        
        # Get patient data
        self.case = get_current("Case")
        self.patient = get_current("Patient")
        self.plan = get_current("Plan")
        
        # Create path data for saving the exported DICOM files
        path = r"\\Client\F$\SHARING\Radiation Oncology Physics\IMRT QA"
        directory = self.patient.PatientID + "_" + self.patient.Name
        self.full_path = os.path.join(path, directory)
        os.makedirs(self.full_path, exist_ok=True)
        
        # Set maximum field size in cm
        self.field_size_limit = 14 # Current QA devce is PTW 1500
        
        # Parameters where gantry angle is set to zero
        self.machines_zero_gantry = ["21EX"]
        
        # Not supported treatment delivery technique
        self.delivery_technique_not_supported = ["TomoDirect"]
        
        # QA plan name parametes
        self.base_max_char = 14
        self.qa_plan_name_suffix = "_QA"

    def save_patient(self):
        # Save patient to update UI
        set_progress('Saving...', percentage = -1)
        self.patient.Save()
        
    def set_ui_to_current_qa_beamset(self, beam_set):
        # Save patient to update UI
        self.save_patient()
        
        # Set progress bar
        set_progress('Setting UI view to current QA beam set...', percentage = -1)
        
        # Load beam set associated with the verification plan
        infos = self.plan.QueryBeamSetInfo(Filter = {'Name': beam_set.DicomPlanLabel})
        self.plan.LoadBeamSet(BeamSetInfo = infos[0])
        
        # Set UI to current QA plan
        ui = get_current("ui")
        ui.TitleBar.Navigation.MenuItem['QA preparation'].Button.Click()
        ui.Workspace.TabControl['Beams'].TabItem['Beams'].Select()

    def ask_user_for_shifts(self, beam_set):
        
        # Get verification plan
        verification_plans = self.get_verification_plans(beam_set)
        
        # Loop through each verification plan
        for verification_plan in verification_plans:
            # Ask the user to make any shifts
            ask_for_shifts = True
            initial_message_flag = True
            while ask_for_shifts:
                # Set progress bar
                set_progress('User making shifts if needed...when done, hit the Script play execution button', percentage = -1)
                
                # Ask user for isocenter shifts
                if initial_message_flag:
                    await_user_input('If needed, shift isocenter.  Then, hit the Scipt execution play button.')
                    initial_message_flag = False
                else:
                    await_user_input('Verify isocenter shifts.  If needed, shift isocenter again.  Then, hit the Scipt execution play button.')
                
                if verification_plan.BeamSet.FractionDose.DoseValues is not None: #Exit flag of while loop
                    print("No shifts made")
                    ask_for_shifts = False
                else: # Compute dose again
                    print("Shifts made and re-calculating dose")
                    set_progress('Calculating dose with updated isocenter...', percentage = -1)
                    self.calc_dose(verification_plan.BeamSet)

    def get_verification_plans(self, beam_set):
        """Returns all verification plans associated with the beam set.
        Currently, only a singhle verification plan can be handled per beam set."""
        # Get verification plans for current plan
        verification_plans = [v for v in self.plan.VerificationPlans if v.OfRadiationSet.DicomPlanLabel == beam_set.DicomPlanLabel]
    
        return verification_plans


    def dose_and_plan_export_to_file(self, beam_set):
        """ DICOM QA export to file
    
        The parameter ignore_precondition_warnings can be used to handle possible warnings. Setting to false will generate exceptions for precondition warnings."""
    
        # Set progress bar
        set_progress('Exporting QA plan and dose to file...', percentage = -1)
        
        # Get the verification plans. This gets all verification plans connected to the beam set.
        verification_plans = self.get_verification_plans(beam_set)
    
        try:
            for verification_plan in verification_plans:
                
                # Make sure there is dose calculated 
                if verification_plan.BeamSet.FractionDose.DoseValues is None:
                    set_progress("Calculating dose...", percentage = -1)
                    self.calc_dose(verification_plan.BeamSet)
                    self.save_patient()
                    set_progress('Exporting QA plan and dose to file...', percentage = -1)
                
                # It is not necessary to assign all of the parameters, you only need to assign the
                # desired export items.
                result = verification_plan.ScriptableQADicomExport(ExportFolderPath = self.full_path,
                                                                   QaPlanIdentity = 'Patient',
                                                                   ExportExamination = False,
                                                                   ExportExaminationStructureSet = False,
                                                                   ExportBeamSet = True,
                                                                   ExportRtRadiationSet  = False,
                                                                   ExportRtRadiations  = False,
                                                                   ExportBeamSetDose = True,
                                                                   ExportBeamSetBeamDose = False,
                                                                   IgnorePreConditionWarnings = True)
                
                # It is important to read the result event if the script was successful.
                # This gives the user a chance to see possible warnings that were ignored, if for
                # example the IgnorePreConditionWarnings was set to True by mistake. The result
                # also contains other notifications the user should read.
                self.log_completed(result)
            
        
        except Exception as error:
            self.log_warning(error)
            self.user_message('Plan and dose export to file failed.  Check execution details for more info.')
            raise error

    def create_qa_plan(self, beam_set):
        
        # Verify no verification plan already exists for the beam set before proceeding
        verification_plans = self.get_verification_plans(beam_set)
        
        if len(verification_plans) == 0:
            # Set progress bar
            set_progress('Creating QA plan...', percentage = -1)
            
            # Set parameters for QA plan based upon the machine
            machine = beam_set.MachineReference.MachineName
            if machine in VARIAN_MACHINES:
                phantom_name = "Octavius Phantom - Exact Couch Rails In"
                phantom_id = "123456"
                iso_center = { 'x': -0.1172943, 'y': 0.09004741, 'z': -0.1 }
            elif machine in RADIXACTS:
                phantom_name = "Octavius Radixact"
                phantom_id = "04302024"
                iso_center = { 'x': -0.097669, 'y': 0.0976434, 'z': -0.225 }
            else:
                print("Machine not supported")
                exit()
            
            # Set gantry angle to zero for the 21EX and TomoDirect plans
            if machine in self.machines_zero_gantry:
                gantry_angle = 0
            else:
                gantry_angle = None
            
            # Set QA plan name
            base_name = str(beam_set.DicomPlanLabel)
            if len(base_name) > self.base_max_char:
                base_name = base_name[:self.base_max_char]
            qa_plan_name = base_name + self.qa_plan_name_suffix
            
            # Create QA verification plan (vp)
            beam_set.CreateQAPlan(PhantomName=phantom_name, 
                                       PhantomId=phantom_id, 
                                       QAPlanName=qa_plan_name,
                                       IsoCenter=iso_center,
                                       DoseGrid={ 'x': 0.25, 'y': 0.25, 'z': 0.25 },
                                       GantryAngle=gantry_angle, 
                                       CollimatorAngle=None, 
                                       CouchRotationAngle=0, 
                                       ComputeDoseWhenPlanIsCreated=True, 
                                       DesiredStatisticalUncertaintyForElectrons=None, 
                                       MotionSynchronizationTechniqueSettings={ 'DisplayName': None, 
                                                                               'MotionSynchronizationSettings': None, 
                                                                               'RespiratoryIntervalTime': None, 
                                                                               'RespiratoryPhaseGatingDutyCycleTimePercentage': None, 
                                                                               'MotionSynchronizationTechniqueType': "Undefined" }, 
                                       RemoveCompensators=False, 
                                       EnableDynamicTracking=False, 
                                       SetupBeamsSettings={ 'UseSetupBeams': False, 
                                                           'UseLocalizationPointAsSetupIsocenter': False, 
                                                           'UseUserSelectedIsocenterAsSetupIsocenter': False })
    
    def export_qa_to_raygateway(self, beam_set):
        """DICOM export to Raygateway"""
    
        # Set progress bar
        set_progress('Exporting QA plan to iDMS...', percentage = -1)
    
        # Get the verification plans. This gets all verification plans for a beam set.
        verification_plans = self.get_verification_plans(beam_set)
        
        for verification_plan in verification_plans:
            try:
                result = verification_plan.ScriptableQADicomExport(RayGatewayTitle = 'Raygateway',
                                                                    QaPlanIdentity = 'Phantom',
                                                                    ExportExamination = True,
                                                                    ExportExaminationStructureSet = True,
                                                                    ExportBeamSet = True,
                                                                    ExportRtRadiationSet  = False,
                                                                    ExportRtRadiations= False,
                                                                    ExportBeamSetDose = True,
                                                                    ExportBeamSetBeamDose = False,
                                                                    IgnorePreConditionWarnings = True)
                
                # It is important to read the result event if the script was successful.
                # This gives the user a chance to see possible warnings that were ignored, if for
                # example the IgnorePreConditionWarnings was set to True by mistake. The result
                # also contains other notifications the user should read.
                self.log_completed(result)
                
            except Exception as error:
                self.log_warning(error)
                self.user_message('Export to iDMS failed.  Verify the treatment plan successfully exported to the iDMS.  Check execution details for more info.')
                raise error

    @staticmethod
    def log_warning(error):
        """ Example on how to read the JSON error string."""
    
        try:
            json_errors = json.loads(str(error))
            # If the json.loads() works then the script was stopped due to
            # a non-blocking warning.
            print('WARNING! Export Aborted!')
            print('Comment:')
            print(json_errors['Comment'])
            print('Warnings:')
    
            # Here the user can handle the warnings. Continue on known warnings,
            # stop on unknown warnings.
            for warning in json_errors['Warnings']:
                print(warning)
        except ValueError:
            # The error was likely due to a blocking warning, and the details should be stated in the execution log. 
            print('Error occurred. Could not export.')
            
    @staticmethod
    def log_completed(result):
        """ This prints the successful result log in an ordered way. """
    
        try:
            json_result = json.loads(result)
            print('Completed!')
            print('Comment:')
            print(json_result['Comment'])
            print('Warnings:')
            for warning in json_result['Warnings']:
                print(warning)
            print('Export notifications:')
            # Export notifications is a list of notifications that the user should read.
            for notification in json_result['Notifications']:
                print(notification)
        except ValueError:
            print('Error reading completion messages.')

    @staticmethod
    def calc_dose(beam_set):
        beam_set.ComputeDose(ComputeBeamDoses=True, DoseAlgorithm="CCDose", ForceRecompute=False, RunEntryValidation=True)

    @staticmethod
    def user_message(message):
        
        # Create a temporary Tkinter window (it won't be shown)
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        
        # Make the temporary window topmost
        root.attributes('-topmost', True)
        
        # Display an information message box with an OK button
        messagebox.showinfo("Information", message)
        
        # Destroy the hidden Tkinter window
        root.destroy()
        
    @staticmethod
    def message_create_qa_plan_yes_no(beam_set):
        # Create a temporary Tkinter window
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        
        # Make the temporary window topmost
        root.attributes('-topmost', True)
        
        # Display Yes/No message box
        response = messagebox.askyesno(
            "Confirm QA Plan Creation",
            f"Do you want to create a QA plan for {beam_set.DicomPlanLabel} beam set even though it has a delivery technique of {beam_set.DeliveryTechnique}?"
        )
        
        # Destroy the hidden Tkinter window
        root.destroy()
        
        return response
    
    @staticmethod
    def user_no_verification_plan(beam_set):
        set_progress(f'User selected not to create a QA plan on {beam_set.DicomPlanLabel} beam set...')
        sleep(3)
    
    @staticmethod
    def calc_max_field_dist_from_iso(beam_set):
        '''Checks if the field is inside the QA device for a beam set.
            The max_field_size is the distance from the isocenter to the field edge
            in the sup-inf direction.'''
            
        # Store the maximum field size as measured in the sup-inf direction
        max_field_size = 0
        
        # Store the jaws to use for calculation
        inf = [0, 2]
        sup = [1, 3]
        
        # Check fields based upon machine type
        machine = beam_set.MachineReference.MachineName
    
        # Loop through all segments in each beam to find largest jaw position
        for beam in beam_set.Beams:
            if machine in VARIAN_MACHINES:
    
                # Get the colimator angle
                coll_angle_degree = beam.InitialCollimatorAngle
                if (coll_angle_degree >=0 and coll_angle_degree <= 90) or (coll_angle_degree >=180 and coll_angle_degree <=270):
                    inf = [0, 2]
                    sup = [1, 3]
                else:
                    inf = [0, 3]
                    sup = [1, 2]
                
                # Calculate collimator angle in radians
                coll_angle_rad = 2 * math.pi * beam.InitialCollimatorAngle / 360
                
                for segment in beam.Segments:
                    dist_sup = math.sqrt( ( segment.JawPositions[sup[0]] * math.cos(coll_angle_rad) )**2 + ( segment.JawPositions[sup[1]] * math.cos(coll_angle_rad) )**2 )
                    dist_inf = math.sqrt( ( segment.JawPositions[inf[0]] * math.cos(coll_angle_rad) )**2 + ( segment.JawPositions[inf[1]] * math.cos(coll_angle_rad) )**2 )
                    
                    # Set printing for debugging only
                    print(f"Sup distance: {dist_sup}       Inf distance: {dist_inf}")
                    
                    # Set max field size to largest sup-inf distance
                    if dist_sup > max_field_size:
                        max_field_size = dist_sup
                    if dist_inf > max_field_size:
                        max_field_size = dist_inf
            
    
            elif machine in RADIXACTS:
                
                # Printing for debugging only
                print(f"Sup distance: {abs(beam.Segments[0].CouchYOffset)}    Inf distance: {abs(beam.Segments[len(beam.Segments)-1].CouchYOffset)}")
                
                # Use couch positions for sup and inf dimensions
                if abs(beam.Segments[0].CouchYOffset) > max_field_size:
                    max_field_size = abs(beam.Segments[0].CouchYOffset)
                if abs(beam.Segments[len(beam.Segments)-1].CouchYOffset) > max_field_size:
                    max_field_size = abs(beam.Segments[len(beam.Segments)-1].CouchYOffset)
                
            else:
                print("Machine not supported")
                exit()
        
        return max_field_size

    def main(self):
        # Loop through each beam set in the plan
        for bs in self.plan.BeamSets:
            #Check for TomoDirect Plans and skip
            if bs.DeliveryTechnique in self.delivery_technique_not_supported:
                self.user_message(f"The delivery techinque {bs.DeliveryTechnique} of your beam set {bs.DicomPlanLabel} is not supported and will be skipped.")
                continue
            
            # Check plan for delivery techinque before proceeding with QA plan creation and export
            response = True # Default
            if bs.DeliveryTechnique in ["SMLC", "Conformal"]:
                # Display Yes/No message box
                response = self.message_create_qa_plan_yes_no(bs)
            
            if response: # Create and export QA plan
                # Set user UI to current QA beam set
                self.set_ui_to_current_qa_beamset(bs)
                
                # Create QA plan
                self.create_qa_plan(bs)
                            
                # Check if the fields are inside the QA device
                if self.calc_max_field_dist_from_iso(bs) > self.field_size_limit:
                    # Ask user for QA plan shifts
                    print("Asking user for shifts, if needed.")
                    self.ask_user_for_shifts(bs)
                
                # Save patient needed to be performed prior to export
                self.save_patient()
                
                # Export QA dose and plan to file
                self.dose_and_plan_export_to_file(bs)
                
                # Check for Radixact machine to export QA plan to iDMS
                if bs.MachineReference['MachineName'] in RADIXACTS:
                    self.export_qa_to_raygateway(bs)
                    
            else: # User does not want a verification plan for current beam set
                self.user_no_verification_plan(bs)

        