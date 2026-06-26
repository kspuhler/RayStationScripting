import sys
sys.path.append(r"\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
sys.path.append(r"F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")

try:
    from connect import *
    from System.Drawing import Color
except:
    pass
    
def get_prescription():
    beam_set = get_current("BeamSet")
    return beam_set.Prescription.PrimaryPrescriptionDoseReference.DoseValue

def get_dmax():
    
    beam_set = get_current("BeamSet")
    dmax =  beam_set.FractionDose.ForBeamSet.FractionDose.GetDoseAtRelativeVolumes(RoiName='External', RelativeVolumes=[0.0])
    fractions = beam_set.FractionationPattern.NumberOfFractions
    return dmax * fractions
    
def get_rx_idl():
    rx_cGy = float(get_prescription())
    dmax   = float(get_dmax())
    print(f'Rx: {rx_cGy}')
    print(f'dmax: {dmax}')
    
    rx_idl = rx_cGy/dmax
    rx_idl *= 100.0
    rx_idl = round(rx_idl,3)
    print(f'rx_idl: {rx_idl}')
    return rx_idl
    

def set_isodose_template_for_cyber_report(template=""):
    '''entry point for external scripts'''
    
    rx_idl = get_rx_idl()
    template = get_current("Case")
    template = template.CaseSettings.DoseColorMap
    
    template.ColorMapReferenceType = 'MaxValue'
    template.ColorTable = {rx_idl: Color.FromArgb(255, 255, 0, 0),
                           100.0: Color.FromArgb(255, 255, 255, 255),
                           50.0: Color.FromArgb(255, 0, 100, 250),
                           30.0: Color.FromArgb(255, 252, 230, 100)}
    
    template.IsDiscrete=True
    template.IsHighValuesClipped = False
    template.IsLowValuesClipped = True
    template.PresentationType = 'Relative'
    template.ReferenceValue = 100

    
    rx_idl = get_rx_idl()
    

    
if __name__ == "__main__":
    set_isodose_template_for_cyber_report()