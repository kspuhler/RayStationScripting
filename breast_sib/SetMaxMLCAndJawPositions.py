# -*- coding: utf-8 -*-
"""
Created on Tue Mar 26 09:34:50 2025

@author: clanco01
"""

from connect import *

class SetMaxMLCAndJawPositions:
    """Given the beam_max MLC and Jaws, beam can not have MLCs or Jaws larger than that in beam_max.
        Closed MLC leaf-pairs are ignored."""
    
    def __init__(self, beam, beam_max):
        
        self.beam = beam
        self.beam_max = beam_max
        
        # Get max jaw positiosn
        max_jaw_positions = self.beam_max.Segments[0].JawPositions
        
        # Loop over each segment
        for segment in self.beam.Segments:
            
            # Get leaf and jaw positions
            leaf_positions = segment.LeafPositions
            jaw_positions = segment.JawPositions
            
            # Loop over each jaw position
            for j in [0, 2]:
                if jaw_positions[j] < max_jaw_positions[j]:
                    jaw_positions[j] = max_jaw_positions[j]
                if jaw_positions[j+1] > max_jaw_positions[j+1]:
                    jaw_positions[j+1] = max_jaw_positions[j+1]
            
            
            # Loop over each leaf pair
            for i in range(len(leaf_positions[0])):
                
                # Check if leaf pair is open or closed
                if leaf_positions[0][i] < leaf_positions[1][i]:
                    
                    # Set MLC leaf to beam_max if larger
                    if leaf_positions[0][i] < self.beam_max.Segments[0].LeafPositions[0][i]:
                        print(f"Segment {segment.SegmentNumber}, Bank 0, Leaf {i}: Optimized value = {leaf_positions[0][i]}   Open Segment = {self.beam_max.Segments[0].LeafPositions[0][i]}  ")
                        leaf_positions[0][i] = self.beam_max.Segments[0].LeafPositions[0][i]
                        print(f"Segment {segment.SegmentNumber}, Bank 0, Leaf {i}:  New value = {leaf_positions[0][i]}")
                        if leaf_positions[1][i] < leaf_positions[0][i]:
                            leaf_positions[1][i] = leaf_positions[0][i]
                    if leaf_positions[1][i] > self.beam_max.Segments[0].LeafPositions[1][i]:
                        print(f"Segment {segment.SegmentNumber}, Bank 1, Leaf {i}: Optimized value = {leaf_positions[1][i]}   Open Segment = {self.beam_max.Segments[0].LeafPositions[1][i]} ")
                        leaf_positions[1][i] = self.beam_max.Segments[0].LeafPositions[1][i]
                        print(f"Segment {segment.SegmentNumber}, Bank 1, Leaf {i}: New value = {leaf_positions[1][i]}")
                        if leaf_positions[0][i] > leaf_positions[1][i]:
                            leaf_positions[0][i] = leaf_positions[1][i]
                
                     
            # Update beam with new leaf and jaw positions
            segment.LeafPositions = leaf_positions
            segment.JawPositions = jaw_positions
        
            
# # Example usage
# beam_set = get_current("BeamSet")
# beam = beam_set.Beams['2 Mod']
# beam_max = beam_set.Beams['2']
# SetMaxMLCAndJawPositions(beam, beam_max)