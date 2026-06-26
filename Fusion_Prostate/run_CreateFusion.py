# -*- coding: utf-8 -*-
""" Front-end to run CreateFusion class

Created on Thu Apr 10 09:54:02 2025

@author: clanco01
"""


import sys

# Correct the script directory (use the folder, not the file)
script_dir = r"\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD\Fusion_Prostate"
sys.path.append(script_dir)

from CreateFusion import CreateFusion

fusion = CreateFusion()
fusion.run_fusion()

exit()