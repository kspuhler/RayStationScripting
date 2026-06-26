from connect import *

class RenameSetupFields():
    def __init__(self, beam_set, gantry_angles=[0, 270, 90]):
        self.beam_set = beam_set
        self.gantry_angles = gantry_angles
        
        # Update setup beams in beamset
        self.beam_set.UpdateSetupBeams(ResetSetupBeams = 'TRUE', SetupBeamsGantryAngles=self.gantry_angles)
        
        # Loop over and update each setup field
        for idx, ii in enumerate(self.gantry_angles):
            self.beam_set.PatientSetup.SetupBeams[idx].Name = "SETUP " + "g" + str(ii)
            self.beam_set.PatientSetup.SetupBeams[idx].Description = "g" + str(ii)
        
        
        
# # Example usage
# beam_set = get_current("BeamSet")
# gantry_angles=[0, 270, 90]
# beam_set.UpdateSetupBeams(ResetSetupBeams = 'TRUE', SetupBeamsGantryAngles=gantry_angles)
# RenameSetupFields(beam_set)