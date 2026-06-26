# -*- coding: utf-8 -*-
""" Front-end to run CreateProstateFusion class

Created on Thu Apr 10 08:23:08 2025

@author: clanco01
"""


import sys

# Correct the script directory (use the folder, not the file)
script_dir = r"\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD\Fusion_Prostate"
sys.path.append(script_dir)

from CreateProstateFusion import CreateProstateFusion

prostate_fusion = CreateProstateFusion()
prostate_fusion.run_fusion()

exit()