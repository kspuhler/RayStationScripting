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
prostCTVn   = ("CTV Node", "#41d8fa", "Ctv" )

spacer = ("Spacer", "#35baf2", "Control")
fiducial = ("Fiducial", "White", "Control")
rectum = ("Rectum", "#17ad49", "Organ")
bowelBag = ("BowelBag", "White", "Organ")
bladder = ("Bladder", "Yellow", "Organ")
bladderMinGtvP = ("Bladder - GTVp", "Yellow", "Organ")
smallBowel = ("Small Bowel", "#35f2ee", "Organ")
largeBowel = ("Large Bowel", "#4b15d4", "Organ")
testes     = ("Testes", "Purple", "Organ")

#Abdom/Thorax stuff
heart   = ("Heart", "#d6891e", "Organ")
thyroid = ("Thyroid", "#4dd63e", "Organ")


#HN Stuff
haasLtHN = ("LtNeck", "#e6d709", "Organ")
haasRtHN = ("RtNeck", "#44e609", "Organ")

cord = ("SpinalCord", "#42f5e3", "Organ")

#Brain Stuff

#Breast Stuff
#Tailor Protocol
tailorGtvColor = "red"
tailorCtvColor = "#ebae34"
tailorPtvColor = "red"
tailorPtvEvaColor = "#50e5f2"

ctv_wb = ("CTV_WB_", tailorCtvColor, "Ctv")
ptv_wb = ("PTV_WB_", tailorGtvColor, "Ptv")
ptv_wb_eva = ("PTV_WB_EVA_", tailorPtvEvaColor, "Ptv")
lumpectomy = ("Lumpectomy_", tailorGtvColor, "Gtv")
ctv_lump = ("CTV_Lump_", tailorCtvColor, "Ctv")
ptv_lump = ("PTV_Lump_", tailorPtvColor, "Ptv")
ptv_lump_eva = ("PTV_Lump_EVA_", tailorPtvEvaColor, "Ptv")
ctv_cw = ("CTV_CW_", tailorCtvColor, "Ctv")
ptv_cw = ("PTV_CW_", tailorPtvColor, "Ptv")
ptv_cw_eva = ("PTV_CW_EVA_", tailorPtvEvaColor, "Ptv")
scar = ("Scar_", tailorGtvColor, "Gtv")
ctv_scar = ("CTV_Scar_", tailorCtvColor, "Ctv")
ptv_scar = ("PTV_Scar_", tailorPtvColor, "Ptv")
ptv_scar_eva = ("PTV_Scar_EVA_", tailorPtvEvaColor, "Ptv")
ctvn_scl = ("CTVn_SCL_", tailorCtvColor, "Ctv")
ptvn_scl = ("PTVn_SCL_", tailorPtvColor, "Ptv")
ctvn_ax  = ("CTVn_Ax_", tailorCtvColor, "Ctv")
ptvn_ax  = ("PTVn_Ax_", tailorPtvColor, "Ptv")
ctvn_imn  = ("CTVn_IMN_", tailorCtvColor, "Ctv")
ptvn_imn  = ("PTVn_IM_N", tailorPtvColor, "Ptv")

tailorLungL  = ("LUNG_L", "#edf1f2", "Organ")
tailorLungR  = ("LUNG_R", "#cbf7cd", "Organ")
tailorBreastL = ("BREAST_L", "#5e6fc4", "Organ")
tailorBreastR = ("BREAST_R", "#5e6fc4", "Organ")





