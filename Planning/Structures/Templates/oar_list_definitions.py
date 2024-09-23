#Tuples for standard ROIs we will add to plans
import sys

sys.path.append("\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
sys.path.append("F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
from RSutil.variables import OPT_STRUCTURE_COLOR



skin = ("Skin", "#f0f7f7", "Organ")
truncExternal = ("zzTruncExternal", OPT_STRUCTURE_COLOR, "Unknown" )

#Pelvis stuff
prostate    = ("GTVp", "red", "Gtv")
ltNode      = ("LtNode", "#db11ed", "Gtv")
rtNode      = ("RtNode", "#069921", "Gtv") 
seminalVes  = ("GTVsv", "#edbe58", "Gtv") 

spacer = ("Spacer", "#35baf2", "Control")
rectum = ("Rectum", "#17ad49", "Organ")
bowelBag = ("BowelBag", "White", "Organ")
bladder = ("Bladder", "Yellow", "Organ")
bladderMinGtvP = ("Bladder-GTVp", "Yellow", "Organ")
smallBowel = ("Small Bowel", "#35f2ee", "Organ")
largeBowel = ("Large Bowel", "#4b15d4", "Organ")
testes     = ("Testes", "Purple", "Organ")

#Abdominal stuff


#HN Stuff
haasLtHN = ("LtNeck", "#e6d709", "Organ")
haasRtHN = ("RtNeck", "#44e609", "Organ")

cord = ("SpinalCord", "#42f5e3", "Organ")






#Brain Stuff






