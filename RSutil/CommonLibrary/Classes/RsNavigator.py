from connect import *
import inspect


class RsNavigator(object):
    
    TOP_BAR_TAB_ITEM_COMBOS = {'Patient data management': ['Patient information'], 
                  'Patient modeling': ['Image registration', 'Structure definition', 'Deformable registration'],
                  'Plan design':  ['Plan setup', '3D-CRT beam design', 'Electron beam design', 'Brachy planning'],
                  'Plan optimization': ['Plan optimization', 'Multi-criteria optimization'],
                  'Plan evaluation': ['Plan evaluation', 'Robust evaluation'],
                  'QA preparation': ['QA preparation'],
                  'Treatment delivery': ['Dose tracking', 'Adaptive replanning']}
    
    def __init__(self):
        
        self.ui = get_current("ui")
        
    def switch_side(self, go_to = None):
        #go_to = the sidebar item to be chosen
        VALID_ARGS = ['ROIs', 'POIs', 'Registrations', 'Scripting', 'Protocols', 'Visualization']
        
        method_name = inspect.currentframe().f_code.co_name
        
        if not go_to:
            raise Exception(f'Class {self.__class__.__name__} called method {method_name} without an input argument.\n '
                            f'Input argument must be one of {VALID_ARGS}')
        if not go_to in VALID_ARGS:
            raise Exception(f'Class {self.__class__.__name__} called method {method_name} with invalid argument go_to = {go_to}.\n '
                            f'go_to must be one of {VALID_ARGS}')
        else:
            self.ui.ToolPanel.TabItem[go_to].Select()
        return
    
    def switch_top(self, go_to = None):
        VALID_ARGS = [key for key in self.TOP_BAR_TAB_ITEM_COMBOS]
        method_name = inspect.currentframe().f_code.co_name
        
        if not go_to:
            raise Exception(f'Class {self.__class__.__name__} called method {method_name} without an input argument.\n '
                            f'Input argument must be one of {VALID_ARGS}')
        if not go_to in VALID_ARGS:
            raise Exception(f'Class {self.__class__.__name__} called method {method_name} with invalid argument go_to = {go_to}.\n '
                            f'go_to must be one of {VALID_ARGS}')
        else:
            self.ui.TitleBar.Navigation.MenuItem[go_to].Button.Click()
        return
    
    def switch_tab(self, tab_go_to = None, top_bar_go_to = None):
            
        if not tab_go_to:
            raise Exception(f'Class {self.__class__.__name__} called method {method_name} without an input argument.\n '
                            f'Input argument must be one of the keys in {TOP_BAR_TAB_ITEM_COMBOS}')
        
        if not top_bar_go_to:
            #get the top bar item to navigate to if user does not provide
            for key, values in self.TOP_BAR_TAB_ITEM_COMBOS.items():
                if tab_go_to in values:
                    top_bar_go_to = key
                    
        self.switch_top(top_bar_go_to)
        self.ui.TabControl_Modules.TabItem[tab_go_to].Button.Click()
        
    def switch_sub_tab(self, sub_tab_go_to = None):
        
        try:
            self.ui.TabControl_ToolBar.TabItem[sub_tab_go_to].Select()
        except:
            raise Exception('Invalid subtab argument')
        
        
        
#unit testing
if __name__ == '__main__':
    test = RsNavigator()
    
    side_bar_args = ['ROIs', 'POIs', 'Registrations', 'Scripting', 'Protocols', 'Visualization']
    for ii in side_bar_args:
         test.switch_side(ii)

    top_bar_args = ['Patient data management', 'Patient modeling', 'Plan design', 'Plan optimization', 'Plan evaluation', 'QA preparation', "Treatment delivery"]
    for jj in top_bar_args:
         test.switch_top(jj)
        
        
    tab_test= {'Patient data management': ['Patient information'], 
                      'Patient modeling': ['Image registration', 'Structure definition', 'Deformable registration'],
                      'Plan design':  ['Plan setup', '3D-CRT beam design', 'Electron beam design', 'Brachy planning'],
                      'Plan optimization': ['Plan optimization', 'Multi-criteria optimization'],
                      'Plan evaluation': ['Plan evaluation', 'Robust evaluation'],
                      'QA preparation': ['QA preparation'],
                
                     'Treatment delivery': ['Dose tracking', 'Adaptive replanning']}
    
    tab_args = []
    for k,v in tab_test.items():
        
        for vv in v:
            test.switch_tab(tab_go_to=vv)
    # while True:
    #     test.switch_sub_tab('Plan setup')
    #     test.switch_sub_tab('Approval')
    #     test.switch_sub_tab('Optimization')    
    
            
            
            