
from connect import *

import sys
sys.path.append(r"\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
sys.path.append(r"F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")

from RSutil.CommonLibrary.Classes.RsNavigator import RsNavigator
from Planning.Structures.Functions.checkForContour import checkForContour
from AutoPlanningBeta.Classes.Util.MachineSelector import MachineSelector
from AutoPlanningBeta.Classes.Structures.ContouringSetup import ContouringSetup
from AutoPlanningBeta.Classes.PlanSetup.Prescription import Prescription
from AutoPlanningBeta.Classes.PlanSetup.GeneratePlan import GeneratePlan
from AutoPlanningBeta.Classes.Optimizer.MachineOptimizers import TrueBeamOptimizer, RadixactOptimizer, CyberknifeOptimizer

import tkinter as tk

 

class Pipeline():
    
    _REQUISITE_CONTOURS = []
    
    _PARAMS = {'PROTOCOL_NAME': None,
              'NUM_BEAMSETS': 1,
              'PLAN_NAME': None,
              'BEAM_SET_NAMES': [None],
              'BEAM_TEMPLATE': None,
              'STRUCTURE_TEMPLATE': {'Name': None, 'Structures': None},
              'ISO_PLACEMENT': "setup",
              'TARGET': [None],
              'TOTAL_DOSE': [None],
              'PERCENT_VOL':[None],
              'FRACTIONS': [None],  
              'STEREOTACTIC': False,
              'CLINICAL_GOAL_TEMPLATE': None,
              'OPTIMIZATION_TEMPLATE': None
              }
    
    _MACHINES = ['TrueBeamSN1106', 
                 '4010100_1000MU']
    
    def __init__(self):
        self.patient = get_current("Patient")
        self.case = get_current("Case")
        self.exam = get_current("Examination")
        self.ui = RsNavigator()
        
        # Shared Tk root for ALL dialogs in this pipeline run
        self.tk_root = tk.Tk()
        self.tk_root.withdraw()


        self.run_precondition_checks()
        self.select_machine() 
        print(self.machine_type)
        

    def run_precondition_checks(self):
        #Check all contours are prensent
        if self._REQUISITE_CONTOURS:
            for ii in self._REQUISITE_CONTOURS:
                if not checkForContour(ii):
                    self.alert_user_of_warning(text=f"Contour {ii} not found, please contour and try to continue.")
    
    
    def select_machine(self):
        selector = MachineSelector(machine_list=self._MACHINES, parent=self.tk_root)
        selector.show()
    
        if not selector.choice:
            self.alert_user_of_failure("No machine selected. Exiting.")
            return
    
        self.machine_name = selector.choice
        self.machine_type, self.technique = self._machine_to_type_and_technique(self.machine_name)
    
    def _machine_to_type_and_technique(self, machine_name):
        if machine_name in ["TrueBeamSN1106"]:
            return "TrueBeam", "VMAT"
        if machine_name in ["4010100_1000MU"]:
            return "Radixact", "TomoHelical"
        if machine_name =='C0363':
            self.ck_ramp = "C0363-11.2.0-20240410-194122_110"
            return "Cyberknife", "Cyberknife"
        if machine_name =='C0480':
            self.ck_ramp = "C0480-11.2.0-20240326-191044_157"
            return "Cyberknife", "Cyberknife"
    
        self.alert_user_of_failure("Unknown machine: {0}".format(machine_name))
        return None, None
   
    def alert_user_of_failure(self, text):
        
        await_user_input(text)
        sys.exit()
    
    def alert_user_of_warning(self, text):
        await_user_input(text)
        
    def run_pipeline(self):
        pass
    
    def contouring_workspace(self):
        
        self.ui.switch_top('Patient modeling')
        self.ui.switch_tab('Structure definition')
        
        if self._PARAMS['STRUCTURE_TEMPLATE']:
            self.ss = ContouringSetup(machine=self.machine_name, templateName=self._PARAMS['STRUCTURE_TEMPLATE']['Name'],
                           templateStuctures=self._PARAMS['STRUCTURE_TEMPLATE']['Structures'],
                   )
        else:
            await_user_input("Contouring placeholder")
    
    def plan_generation(self):
        
        self.ui.switch_tab('Plan setup')
        
        self.set_rx()

        plan = GeneratePlan(planName = self._PARAMS['PLAN_NAME'], 
                         beamSetNames = self._PARAMS['BEAM_SET_NAMES'],
                         machineName = self.machine_name,
                         treatmentTechnique = self.technique,
                         isoPlacement = self._PARAMS['ISO_PLACEMENT'],
                         targetNameForIsocenter = self._PARAMS['TARGET'][0],
                         isStereotactic = self._PARAMS['STEREOTACTIC'],
                         beamTemplate = self._PARAMS['BEAM_TEMPLATE'])
        
        plan.generatePlan(numFractions = self._PARAMS['FRACTIONS'])
        
        rx.setRx()
        return
    
    def set_rx(self):
        rx = Prescription(totalDose=self._PARAMS['TOTAL_DOSE'][0],target=self._PARAMS['TARGET'][0],doseVol=self._PARAMS['PERCENT_VOL'][0],autoScale=False)
        rx.setRx()
    
    def optimization_workspace(self):
        self.ui.switch_top("Plan optimization")
        
        if self.machine_type == "TrueBeam":
            self.optimizer = TrueBeamOptimizer(tk_root = self.tk_root, clinicalGoalTemplate=self._PARAMS['CLINICAL_GOAL_TEMPLATE'], 
                                               optimizationTemplate = self._PARAMS['OPTIMIZATION_TEMPLATE'])
        elif self.machine_type == "Radixact":
            self.optimizer = RadixactOptimizer(tk_root = self.tk_root, clinicalGoalTemplate=self._PARAMS['CLINICAL_GOAL_TEMPLATE'], 
                                               optimizationTemplate = self._PARAMS['OPTIMIZATION_TEMPLATE'])
        
        elif self.machine_type == "Cyberknife":
            self.optimizer = CyberknifeOptimizer(tk_root = self.tk_root, clinicalGoalTemplate=self._PARAMS['CLINICAL_GOAL_TEMPLATE'], 
                                               optimizationTemplate = self._PARAMS['OPTIMIZATION_TEMPLATE'])
        
        self.optimizer.setOptimizationParameters()
        self.optimizer.loadOptimizationTemplate()
        self.optimizer.loadClinicalGoals()
        return
            
    
    def close_out(self):
        sys.exit()

        
    
    