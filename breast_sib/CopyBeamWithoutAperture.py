from connect import *

class CopyBeamWithoutAperture:
    def __init__(self, beam_set, beam_set_to_copy, beam_name_to_copy, new_beam_name="1", new_beam_energy="6"):
        # Set initial parameters
        self.case = get_current("Case")
        self.beam_set = beam_set
        self.beam_to_copy = beam_set_to_copy.Beams[beam_name_to_copy]
        self.beam_set_to_copy = beam_set_to_copy
        self.beam_name_to_copy = beam_name_to_copy
        self.beam_name_to_delete = 'Delete'
        self.new_beam_name = new_beam_name
        self.new_beam_energy = new_beam_energy
        
        # Set treatment technique to match beam_set_to_copy
        self.beam_set.SetTreatmentTechnique(Technique=beam_set_to_copy.PlanGenerationTechnique)
        
        # Copy beam parameters to create a new beam
        self.create_beam()
        
        # Copy jaws and leaf positions
        self.copy_jaws_and_leaves()
        
        # Delete directly copied beam
        self.delete_copied_beam()

    def create_beam(self):
        # Copy beam into current beam set as a temporary beam and copy its beam parameters to create a new beam
        self.beam_set.CopyBeamsFromBeamSet(BeamSetToCopyFrom=self.beam_set_to_copy, BeamsToCopy=[self.beam_name_to_copy])
        self.beam_set.Beams[self.beam_name_to_copy].Name = self.beam_name_to_delete
        self.iso_data = self.beam_set.GetIsocenterData(Name=self.beam_set.Beams[self.beam_name_to_delete].Isocenter.Annotation.Name)
        self.beam = self.beam_set.CreatePhotonBeam(BeamQualityId=self.new_beam_energy, CyberKnifeCollimationType="Undefined", CyberKnifeNodeSetName=None, 
						  CyberKnifeRampVersion=None, 
                          CyberKnifeAllowIncreasedPitchCorrection=None, GimbalPanAngle=0, GimbalTiltAngle=0, 
                          IsocenterData=self.iso_data, Name=self.new_beam_name, Description="", 
                          GantryAngle=self.beam_to_copy.GantryAngle, 
                          CouchRotationAngle=self.beam_to_copy.CouchRotationAngle, 
                          CouchPitchAngle=self.beam_to_copy.CouchPitchAngle, 
                          CouchRollAngle=self.beam_to_copy.CouchRollAngle, 
                          CollimatorAngle=self.beam_to_copy.InitialCollimatorAngle)
        self.beam.SetBolus(BolusName="")
        self.beam.BeamMU = 0
        self.beam.SetInitialJawPositions(X1=self.beam_to_copy.InitialJawPositions[0], 
                                         X2=self.beam_to_copy.InitialJawPositions[1], 
                                         Y1=self.beam_to_copy.InitialJawPositions[2], 
                                         Y2=self.beam_to_copy.InitialJawPositions[3])

    def copy_jaws_and_leaves(self):
        # Select the beam that needs to be deleted based upon the name
        initial_beam = self.beam_set.Beams[self.beam_name_to_delete]
        
        # Set technique to COnformal for conforming MLC shapes
        self.beam_set.SetTreatmentTechnique(Technique="Conformal")
        
        # Clear all treat and protect to correctly conform MLC to virtual block or jaws
        [self.beam_set.ClearROIFromTreatOrProtectUsageForAllBeams(RoiName=roi.Name) for roi in self.case.PatientModel.RegionsOfInterest]
        
        # Conform initial beam if Segments is empty
        if not initial_beam.Segments:
            initial_beam.ConformMlc()
        
        # Set new beam equal to jaws and leaf positions of beam to delete
        self.beam.ConformMlc()
        self.beam.Segments[0].JawPositions = initial_beam.Segments[0].JawPositions
        self.beam.Segments[0].LeafPositions = initial_beam.Segments[0].LeafPositions

    def delete_copied_beam(self):
        self.beam_set.DeleteBeam(BeamName=self.beam_name_to_delete)



# Example usage
# case = get_current("Case")
# beam_set_to_copy = case.TreatmentPlans['zzzTest_Sim'].BeamSets['zzzTest_Sim']
# beam_name_to_copy = '1Rt Medial'
# beam_set = case.TreatmentPlans['Delete'].BeamSets['Delete']
# CopyBeamWithoutAperture(beam_set, beam_set_to_copy, beam_name_to_copy)
