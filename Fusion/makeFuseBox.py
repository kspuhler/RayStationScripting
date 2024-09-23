try:
    from connect import *
except:
    pass

import sys
sys.path.append("\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD\Fusion")

from functions import makeBoxRoi


if __name__ == '__main__':
    makeBoxRoi()
