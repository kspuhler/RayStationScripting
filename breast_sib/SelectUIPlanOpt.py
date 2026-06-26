"""
Created on Mon Mar 3 2025

@author: clanco01
"""

from connect import *

class SelectUIPlanOpt:
    """
    A class to select a plan and beam set open to the Objectives/constraits tab in the UI.
    
    Attributes:
        plan_name (str): The name of the plan to select.
        beam_set_name (str): The name of the beam set to select.
    """
    
    def __init__(self, plan_name, beam_set_name, tab_item_dvh="DVH", tab_item_obj="Objectives/constraints"):

        # Get current UI data
        self.ui = get_current('ui')
        self.case = get_current("Case")
        self.plan_name = plan_name
        self.beam_set_name = beam_set_name
        self.menu_item = "Plan optimization"
        self.tab_control_module = "Plan optimization"
        self.tab_item_dvh = tab_item_dvh
        self.tab_item_obj = tab_item_obj
        
        try:
            # Load the plan's beam set
            infos = self.case.TreatmentPlans[self.plan_name].QueryBeamSetInfo(Filter = {'Name': self.beam_set_name})
            self.case.TreatmentPlans[self.plan_name].LoadBeamSet(BeamSetInfo = infos[0])
            print(f"Selected Plan: {self.plan_name}")
            print(f"Selected Beam set: {self.beam_set_name}")

            # Select menu item
            self.ui.TitleBar.Navigation.MenuItem[self.menu_item].Button.Click()
            print(f"Opened menu item: {self.menu_item}")
            
            # Select tab control module
            self.ui.TabControl_Modules.TabItem[self.tab_control_module].Select()
            print(f"Opened tab control module: {self.tab_control_module}")
            
            # Select tab item for DVH workspace
            self.ui.Workspace.TabControl['DVH'].TabItem[self.tab_item_dvh].Select()
            print(f"Selected tab item: {self.tab_item_obj}")
            
            # Select tab item for Objectives/constraints workspace
            self.ui.Workspace.TabControl['Objectives/constraints'].TabItem[self.tab_item_obj].Select()
            print(f"Selected tab item: {self.tab_item_obj}")

        except KeyError as e:
            print(f"Error: Unable to find UI element - {str(e)}")
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            
        # Set the scripting tab visable to the user
        self.ui.ToolPanel.TabItem['Scripting'].Select()

# # Example Usage
# plan = get_current("Plan")
# beam_set = get_current("BeamSet")
# SelectUIPlanOpt(plan.Name, beam_set.DicomPlanLabel)
