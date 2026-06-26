"""
Raystation Scripts: run_bladder_check, run_fiducial_test.

A class that provides methods for determining bladder volume as well as fiducial-related metrics.
Uses the auto contoured bladder and prostate to determine the volumes and ratio,
inserts  the fiducial marker points (POIs) and the determines the trackability and 
quality of the fiducial implant via an implementation of Accuray's minimum
angle test.

@author: Joseph P. Santoro
"""

