try:
    from connect import *
except:
    pass


class Prescription:
    def __init__(self, totalDose, target, doseVol,autoScale):
        
        self.totalDose = totalDose
        self.target    = target
        self.doseVol   = doseVol
        self.autoScale = autoScale
        
    def setRx(self):
        bs = get_current("BeamSet")
        bs.AddRoiPrescriptionDoseReference(RoiName =  self.target,
                                           DoseVolume = self.doseVol,
                                           PrescriptionType = "DoseAtVolume",
                                           DoseValue = self.totalDose)
        if self.autoScale:
            bs.SetAutoScaleToPrimaryPrescription(AutoScale = True)
        else:
            bs.SetAutoScaleToPrimaryPrescription(AutoScale = False)
        return

