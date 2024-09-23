from .oar_list_definitions import *


def appendSIB(roiList):
    out = roiList.copy()
    return out.append(("SIB", "Red", "GTV"))

prostNodes4500 = [prostate, ltNode, rtNode, seminalVes, ("PTV4500", "Red", "Ptv"),
                       bladder, bladderMinGtvP, rectum, bowelBag, spacer]

prostNodes4500SIB = appendSIB(prostNodes4500)

prostSBRT = [prostate, seminalVes, spacer, rectum, bladder, bladderMinGtvP, smallBowel, largeBowel, testes]

prostSBRT_SIB = appendSIB(prostSBRT)

haasHeadAndNeck = [("GTV", "Red", "Gtv"), haasLtHN, haasRtHN]

