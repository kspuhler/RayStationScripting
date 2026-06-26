# -*- coding: utf-8 -*-
"""
Created on Mon Feb 10 06:57:14 2025

@author: clanco01
"""

class MLCMarginProcessor:
    def __init__(self, beam_set, rois, margin_value=0.7, roi_name="PTV_TB_Eval", final_technique="SMLC"):
        """
        Initialize the MLCMarginProcessor with a beam set, margin value, and ROI name.

        :param beam_set: The beam set object from RayStation.
        :param margin_value: The margin to apply to the MLCs.
        :param roi_name: The name of the region of interest (ROI) to use.
        """
        self.beam_set = beam_set
        self.margin_value = margin_value
        self.roi_name = roi_name
        self.beam_set.SetTreatmentTechnique(Technique="Conformal")
        self.final_technique = final_technique
        
        # Turn off all ROIs as treat or protect
        [self.beam_set.ClearROIFromTreatOrProtectUsageForAllBeams(RoiName=roi.Name) for roi in rois]

    def apply_margins(self):
        """Applies MLC margins to the beam set and returns the modified beam set."""
        if not self.beam_set:
            raise ValueError("No beam set provided. Ensure a valid beam set is passed.")

        # Turn off jaw setback
        self.beam_set.SetJawSetback(JawSetback=False)

        # Select the ROI to be used for margins
        self.beam_set.SelectToUseROIasTreatOrProtectForAllBeams(RoiName=self.roi_name)

        # Apply margins to all treat and protect ROIs
        for beam in self.beam_set.Beams:
            beam.SetTreatAndProtectMarginsForBeam(
                TopMargin=self.margin_value,
                BottomMargin=self.margin_value,
                LeftMargin=self.margin_value,
                RightMargin=self.margin_value,
                Roi=self.roi_name  # Apply to all selected Treat and Protect ROIs
            )

        # Conform all MLCs
        self.beam_set.TreatAndProtect(ShowProgress=True)
        
        # Finalize output treatment technique
        self.beam_set.SetTreatmentTechnique(Technique=self.final_technique)

        return self.beam_set  # Return the modified beam set

# Example usage:
# from connect import get_current
# beam_set = get_current("BeamSet")
# mlc_processor = MLCMarginProcessor(beam_set, margin_value=0.7, roi_name="PTV_TB_Eval")
# updated_beam_set = mlc_processor.apply_margins()
