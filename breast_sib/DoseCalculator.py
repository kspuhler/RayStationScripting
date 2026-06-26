class DoseCalculator:
    def __init__(self, beam_set, beam_mu={}):
        """
        Initialize the DoseCalculator with a beam set.

        :param beam_set: The beam set object from RayStation.
        """
        self.beam_set = beam_set
        self.beam_mu = beam_mu
        
        # Create a list of the beam MU if empty
        if not beam_mu:
            for beam in beam_set.Beams:
                beam_mu[beam.Name] = 1 # Default value

    def compute_dose(self):
        """
        Attempts to compute dose using SetMUAndComputeDose().
        If it fails, sets MU to 1 for all beams and retries ComputeDose().
        """
        try:
            self.beam_set.SetMUAndComputeDose(ForceRecompute=False)
        except Exception as e:
            print(f"SetMUAndComputeDose failed: {e}, falling back to manual MU adjustment.")
            
            for beam in self.beam_set.Beams:
                beam.BeamMU = self.beam_mu[beam.Name]

            self.beam_set.ComputeDose(
                ComputeBeamDoses=True,
                DoseAlgorithm="CCDose",
                ForceRecompute=False,
                RunEntryValidation=True
            )

        return self.beam_set  # Return the updated beam set

# Example usage:
# beam_set_tangents = get_current("BeamSet")
# dose_calculator = DoseCalculator(beam_set_tangents)
# updated_beam_set = dose_calculator.compute_dose()
