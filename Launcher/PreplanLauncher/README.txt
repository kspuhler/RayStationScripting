Launcher for preplanning scripts.

gui.py is the script specifically uploaded to RS
it has a dictionary of kv pairs: {"Name Visible To User": Class}
for example: {"HaasProstateNodes180x25": HaasProstate}
it then calls an internal method to instantiate HaasProstate, which runs the script

dictionary of "approved" scripts is stored in this same directory 
 F:\\SHARING\\Radiation Oncology Physics\\RaystationScriptingPROD\\Launcher\\PreplanLauncher\\publishedscripts