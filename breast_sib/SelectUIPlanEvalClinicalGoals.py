# -*- coding: utf-8 -*-
"""
Created on Mon Mar  3 13:02:08 2025

@author: clanco01
"""

"""
Created on Mon Mar 3 2025

@author: clanco01
"""

try:
    from connect import get_current
except Exception:
    pass

import time

class SelectUIPlanEvalClinicalGoals:
    """
    A class to select a plan open to CLinical goals in Plan evaluation in the UI.
    
    Attributes:
        plan_name (str): The name of the plan to select.
    """
    
    def __init__(self, 
                 plan_name=None,  
                 menu_item="Plan evaluation",
                 tab_control_module="Plan evaluation",
                 tab_control_toolbar="Evaluation",
                 layout='DOSE 1_0',
                 dynamic_tab_page="Clinical goals",
                 layout_tab="Layout1",
                 tab_item="Scripting",
    ):
        self.time_delay = 0.1
        time.sleep(self.time_delay)
        self.ui = get_current('ui')
        self.case = get_current("Case")
        self.plan_name = plan_name
        self.menu_item = menu_item
        self.tab_control_module = tab_control_module
        self.tab_control_toolbar = tab_control_toolbar
        self.layout = layout
        self.dynamic_tab_page = dynamic_tab_page
        self.layout_tab = layout_tab
        self.tab_item = tab_item
        
        try:
            # Set current plan to view
            try:
                if self.plan_name is not None:
                    plan = self.case.TreatmentPlans[self.plan_name]
                    plan.SetCurrent()
            except Exception:
                pass
            
            # Select menu item
            time.sleep(self.time_delay)
            self.ui.TitleBar.Navigation.MenuItem[self.menu_item].Button.Click()
            print(f"Opened menu item: {self.menu_item}")
            
            # Select tab control module
            time.sleep(self.time_delay)
            self.ui.TabControl_Modules.TabItem[self.tab_control_module].Button.Click()
            print(f"Opened tab control module: {self.tab_control_module}")
            
            # Select tab control toolbar
            time.sleep(self.time_delay)
            self.ui.TabControl_ToolBar.TabItem[self.tab_control_toolbar].Select()
            print(f"Selected tab control toolbar: {self.tab_control_toolbar}")
            
            # Select layout
            time.sleep(self.time_delay)
            self.ui.TabControl_ToolBar.ToolBarGroup['_0'].DropDownButton_Select_layout.Click()
            time.sleep(self.time_delay)
            self.ui.TabControl_ToolBar.ToolBarGroup['_0'].DropDownButton_Select_layout.Popup.MenuItem[self.layout].Click()
            print(f"Selected layout: {self.layout}")
            
            # Select tab item
            time.sleep(self.time_delay)
            if self.layout_tab == "Layout1":
                self.ui.Workspace.NotifyingContentControl.Layout1.TabControl['DVH'].DynamicTabPage[self.dynamic_tab_page].Select()
            elif self.layout_tab == "Layout2":
                self.ui.Workspace.NotifyingContentControl.Layout2.TabControl['DVH'].DynamicTabPage[self.dynamic_tab_page].Select()
            print(f"Selected dynamic tab page: {self.dynamic_tab_page}")
            
            # Set the tab visable to the user
            time.sleep(self.time_delay)
            self.ui.ToolPanel.TabItem[self.tab_item].Select()

        except KeyError as e:
            print(f"Error: Unable to find UI element - {str(e)}")
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            
        

# Example Usage
# plan = get_current("Plan")
# clincal_goals = SelectUIPlanEvalClinicalGoals(plan.Name)
