# A script that runs the console and shows the state tree 

import statetree
from connect import *

scriptInstallPath = System.IO.Path.GetDirectoryName(sys.argv[0])
os.chdir(scriptInstallPath)

statetree.RunStateTree()
run('run_console')