# -*- coding: utf-8 -*-
"""
Created on Tue Mar 18 14:34:05 2025

@author: clanco01
"""

from connect import *

class SelectPlanDesign:
    """
    A class to select a plan and beam set open to Plan design in the UI.
    
    Attributes:
        plan_name (str): The name of the plan to select.
        beam_set_name (str): The name of the beam set to select.
    """
    
    def __init__(self, plan_name, beam_set_name, menu_item = "Plan design"):

        # Get current UI data
        self.ui = get_current('ui')
        self.case = get_current("Case")
        self.plan_name = plan_name
        self.beam_set_name = beam_set_name
        self.menu_item = menu_item
        
        try:
            # Load the plan's beam set
            infos = self.case.TreatmentPlans[self.plan_name].QueryBeamSetInfo(Filter = {'Name': self.beam_set_name})
            self.case.TreatmentPlans[self.plan_name].LoadBeamSet(BeamSetInfo = infos[0])
            print(f"Selected Plan: {self.plan_name}")
            print(f"Selected Beam set: {self.beam_set_name}")

            # Select menu item
            self.ui.TitleBar.Navigation.MenuItem[self.menu_item].Button.Click()
            print(f"Opened menu item: {self.menu_item}")
            

        except KeyError as e:
            print(f"Error: Unable to find UI element - {str(e)}")
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            
        # Set the scripting tab visable to the user
        self.ui.ToolPanel.TabItem['Scripting'].Select()

# # Example Usage
# plan = get_current("Plan")
# beam_set = get_current("BeamSet")
# SelectPlanDesign('zzzDelete', 'zzzDelete')
