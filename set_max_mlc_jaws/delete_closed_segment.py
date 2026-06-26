"""
set_max_mlc_jaws\delete_closed_segment.py

Created on Mon Apr  7 10:31:07 2025

@author: clanco01
"""

from connect import *
import tkinter as tk
from tkinter import messagebox
import numpy as np

class DeleteClosedSegment:
    def __init__(self, beam):
        self.beam = beam
        to_delete = []
        for segment in self.beam.Segments:
            if np.array_equal(segment.LeafPositions[0], segment.LeafPositions[1]):
                to_delete.append(segment.SegmentNumber)
        print(f"Segments to delete: {to_delete}")
        for i in sorted(to_delete, reverse=True):
            print(f"Checking segment number: {i}")
            if len(self.beam.Segments) > 1:
                try:
                    self.beam.DeleteSegment(SegmentNumber=i)
                    print(f"Segment Deleted -   Beam: {self.beam.Name}   Segment #: {i}")
                except:
                    root = tk.Tk()
                    root.withdraw()  # Hide the root window
                    messagebox.showerror("Error", f"Something went wrong!  Unable to delete beam {self.beam.Name} segment number {i}.")
                    root.destroy()
            else:
                root = tk.Tk()
                root.withdraw()  # Hide the root window
                messagebox.showerror("Error", f"Attempted to delete a single segment in a beam {self.beam.Name}.  Not allowed!")
                root.destroy()
                

