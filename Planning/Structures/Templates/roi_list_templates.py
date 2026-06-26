import sys

sys.path.append("\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
sys.path.append("F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")

from Planning.Structures.Templates.oar_list_definitions import *


def appendSIB(roiList):
    out = roiList.copy()
    return out.append(("SIB", "Red", "GTV"))

prostNodes4500 = [prostate, ltNode, rtNode, seminalVes,
                       bladder,  rectum,  spacer, fiducial, bowelBag]

prostNodes4500SIB = appendSIB(prostNodes4500)

prostSBRT = [prostate, seminalVes, spacer, rectum, bladder, smallBowel, largeBowel, testes]

prostSBRT_SIB = appendSIB(prostSBRT)

haasHeadAndNeck = [("GTV", "Red", "Gtv"), haasLtHN, haasRtHN]



tailorBreastAll = [ctv_wb, ptv_wb, ptv_wb_eva, lumpectomy, ctv_lump, ptv_lump, ptv_lump_eva, tailorLungL, tailorLungR, heart, thyroid]
tailor1A = tailorBreastAll
tailor1B = tailorBreastAll

# Define tailor2A after tailorBreastAll is defined
tailor2A = [ctvn_scl, ptvn_scl, ctvn_ax, ptvn_ax, ctvn_imn, ptvn_imn]
tailor2A = tailorBreastAll + tailor2A  # Combine them here


# Same for tailor2B
tailor2B = [ctv_cw, ptv_cw, ptv_cw_eva, scar, ctv_scar, ptv_scar, ptv_scar_eva]
tailor2B = tailorBreastAll + tailor2B + tailor2A  # Combine correctly