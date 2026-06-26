from connect import *
import numpy as np


def getRoiMinDoseForBeamSet(roi, beamSet):
    fractions = beamSet.FractionationPattern.NumberOfFractions
    d = beamSet.FractionDose.GetDoseAtRelativeVolumes(RoiName = roi, RelativeVolumes=[1.0])
    return np.round(fractions*d, 1)

def getRoiMaxDoseForBeamSet(roi, beamSet):
    fractions = beamSet.FractionationPattern.NumberOfFractions
    d = beamSet.FractionDose.GetDoseAtRelativeVolumes(RoiName = roi, RelativeVolumes=[0.0])
    return np.round(fractions*d, 1)

def getRoiMinDoseForPlan(roi, plan):
    addThese = []
    for bs in plan.BeamSets:
        addThese.append(getRoiMinDoseForBeamSet(roi, beamSet = bs))
    return np.round(np.sum(addThese),1)
        

def getRoiMaxDoseForPlan(roi, plan):
    addThese = []
    for bs in plan.BeamSets:
        addThese.append(getRoiMaxDoseForBeamSet(roi, beamSet = bs))
    return np.round(np.sum(addThese),1)
    
if __name__ == "__main__":
    bs = get_current("BeamSet")
    dmax = getRoiMaxDoseForBeamSet(roi = 'CTV_45', beamSet=bs)
    print(f'PTV dmax: {dmax}')
    dmin = getRoiMinDoseForBeamSet(roi = 'CTV_50.4', beamSet=get_current("BeamSet"))
    print(f'PTV dmin: {dmin}')
    
    
    #dmax = getRoiMaxDoseForPlan(roi = 'PTV4500', plan=get_current("Plan"))
    #print(f'PTV  plan dmax: {dmax}')
    
    #dmin = getRoiMinDoseForPlan(roi = 'PTV4500', plan=get_current("Plan"))
    #print(f'PTV  plan dmin: {dmin}')