#testing pat = 11789585


#'F:\\SHARING\\Radiation Oncology Physics\\RaystationScriptingPROD\\AutoPlanningBeta\\Pipelines\\Devel'

import sys
sys.path.append("\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
sys.path.append("F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")



from connect import *

import tkinter as tk

from AutoPlanningBeta.Classes.Optimizer.MachineOptimizers import TrueBeamOptimizer, RadixactOptimizer
from AutoPlanningBeta.Classes.PlanSetup.Prescription import Prescription
from AutoPlanningBeta.Classes.PlanSetup.GeneratePlan import GeneratePlan
from AutoPlanningBeta.Classes.Structures.ContouringSetup import ContouringSetup
from Planning.Structures.Functions.croppingShortcuts import *

from RSutil.CommonLibrary.Classes.RsNavigator import RsNavigator

from AutoPlanningBeta.Pipelines.Pipeline import Pipeline




class TC_Lung_6000(Pipeline):
    
    _REQUISITE_CONTOURS = ["PTV6000"]
    
    _PARAMS = {**Pipeline._PARAMS,
               'PROTOCOL_NAME': "TC_Lung_200x30",
              'NUM_BEAMSETS': 1,
              'PLAN_NAME': 'Lung6000',
              'BEAM_SET_NAMES': ['Lung6000'],
              'BEAM_TEMPLATE': None,
              'STRUCTURE_TEMPLATE': {'Name': 'PLAN TEMPLATE: TC LUNG 200x30', 'Structures': ['SpinalCord','Esophagus','Heart',
                                                                                             'Lung_L','Lung_R','zNTO', 'zShell', 
                                                                                             'Cord+5mm', 'Lungs', 'zXHeart', 'zXEsophagus', 
                                                                                             'zZHeart', 'zZEsophagus', 'zz_BrachPlex']},
              'TARGET': ["PTV6000"],
              'TOTAL_DOSE': [6000],
              'PERCENT_VOL':[95],
              'FRACTIONS': [30],  
              'CLINICAL_GOAL_TEMPLATE': "TC Lung 200x30 PRF",
              'OPTIMIZATION_TEMPLATE': None
              }
    
    def __init__(self):
        super().__init__()
        
        
        self.contouring_workspace()
        self.plan_generation()
        self.optimization_workspace()
        
    
    #overrides
    
    def run_precondition_checks(self):
        super().run_precondition_checks()
        self.infer_plan_laterality() 
        self.process_plan_laterality()

    def infer_plan_laterality(self,rt_lim = -1.0, lt_lim = 1.0):
        '''Infers whether lt lung or rt lung based on the coordinates of the center of the target'''
        print("infer")
        tmp = self._PARAMS['TARGET'][0]
        xyz = self.case.PatientModel.StructureSets[self.exam.Name].RoiGeometries[tmp].GetCenterOfRoi()
        x = xyz['x']
        print(x)
        
        if x <= rt_lim:
            self.lat = 'RIGHT'
        elif x >= lt_lim:
            self.lat = 'LEFT'
        else:
            self.lat = self.ask_left_right()
        
        print(self.lat)
            
    def process_plan_laterality(self):
        
        '''Set various params based on laterality of gtv'''
        if self.lat == 'LEFT':
            self._PARAMS['PLAN_NAME'] = 'Lt' + self._PARAMS['PLAN_NAME']
            self._PARAMS['BEAM_SET_NAMES'][0] = 'Lt' + self._PARAMS['BEAM_SET_NAMES'][0]
            self._PARAMS['BEAM_TEMPLATE'] = 'SCRIPT TEMPLATE: LT SIDE HALF ARC'
            return
        elif self.lat == "RIGHT":
            self._PARAMS['PLAN_NAME'] = 'Rt' + self._PARAMS['PLAN_NAME']
            self._PARAMS['BEAM_SET_NAMES'][0] = 'Rt' + self._PARAMS['BEAM_SET_NAMES'][0]
            self._PARAMS['BEAM_TEMPLATE'] = 'SCRIPT TEMPLATE: RT SIDE HALF ARC'
            return
        elif self.lat == "MEDIAL":
            self._PARAMS['BEAM_TEMPLATE'] = "2 Arcs dual"
            return
        
    def ask_left_right(self, title="Select Side", prompt="Select a side:"):
        result = {"value": None}
    
        win = tk.Toplevel(self.tk_root)
        win.title(title)
        win.resizable(False, False)
    
        tk.Label(win, text=prompt).pack(padx=12, pady=(12, 6))
    
        var = tk.StringVar(value="MEDIAL")
        tk.Radiobutton(win, text="LEFT",   variable=var, value="LEFT").pack(anchor="w", padx=12)
        tk.Radiobutton(win, text="RIGHT",  variable=var, value="RIGHT").pack(anchor="w", padx=12)
        tk.Radiobutton(win, text="MEDIAL", variable=var, value="MEDIAL").pack(anchor="w", padx=12)
    
        def close():
            try:
                win.destroy()
            except Exception:
                pass
    
        def submit():
            result["value"] = var.get()
            close()
    
        tk.Button(win, text="Submit", command=submit).pack(pady=12)
        win.protocol("WM_DELETE_WINDOW", close)
    
        # ---- Force it to actually show (RayStation/Windows quirks) ----
        win.update_idletasks()
        win.deiconify()
        win.lift()
        win.focus_force()
        try:
            win.attributes("-topmost", True)
            win.update_idletasks()
            win.update()
            win.after(250, lambda: win.attributes("-topmost", False))
        except Exception:
            pass
    
        # Avoid grab_set at first; it can fail silently in some hosts
        # try:
        #     win.grab_set()
        # except Exception:
        #     pass
    
        # ---- Block until closed, while pumping events ----
        while True:
            try:
                if not win.winfo_exists():
                    break
                self.tk_root.update_idletasks()
                self.tk_root.update()
            except Exception:
                break
    
        return result["value"]
    
    def contouring_workspace(self):
        super().contouring_workspace()
        
        del self.ss
        
        await_user_input('''Suggested actions:\n
                         1. Verify couch placement.''')

        
        
        

def main():

    a = TC_Lung_6000()
    
if __name__ == '__main__':
    main()
    
    
    
