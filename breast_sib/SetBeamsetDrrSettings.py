# -*- coding: utf-8 -*-
"""
Created on Tue Mar  4 08:08:46 2025

@author: clanco01
"""

from connect import *

class SetBeamsetDrrSettings:
    """A class to apply DRR settings for a given beam set."""

    # Default DRR settings for 'Breast' type
    BREAST_SETTINGS = {
        'BoneEnhancementFactor': 5.3,
        'BoneThreshold': -146,
        'CropToExternal': False,
        'CtThresholdHigh': 3096,
        'CtThresholdLow': -758,
        'DrrCtFilterName': 'Flat',
        'DrrEngineVersion': 2,
        'HighlightMarkers': False,
        'InvertDrr': False,
        'Name': 'Default',
        'ShowTextInExportedDrr': True,
        'UseBoneEnhancementFactor': False,
        'UseCtThreshold': False,
        'UseMipAsDrr': False
    }

    # Default DRR settings for 'Bone' type
    BONE_SETTINGS = {
        'BoneEnhancementFactor': 3.1,
        'BoneThreshold': 634,
        'CropToExternal': True,
        'CtThresholdHigh': 3096,
        'CtThresholdLow': -1000,
        'DrrCtFilterName': 'Only Bones',
        'DrrEngineVersion': 2,
        'HighlightMarkers': False,
        'InvertDrr': False,
        'Name': 'Default',
        'ShowTextInExportedDrr': True,
        'UseBoneEnhancementFactor': True,
        'UseCtThreshold': False,
        'UseMipAsDrr': False
    }

    def __init__(self, beam_set, drr_type='Bone'):
        """
        Initializes the DRR settings based on the specified type.
        
        Args:
            beam_set: The beam set object to which the settings will be applied.
            drr_type: The type of settings to apply ('Bone' or 'Breast').
        """
        self.drr_settings = beam_set.DrrSettings[0]

        # Apply settings based on drr_type
        if drr_type.lower() == 'breast':
            self.apply_settings(self.BREAST_SETTINGS)
        elif drr_type.lower() == 'bone':
            self.apply_settings(self.BONE_SETTINGS)
        else:
            print(f"Unknown DRR type '{drr_type}'. Defaulting to 'Bone'.")
            self.apply_settings(self.BONE_SETTINGS)

    def apply_settings(self, settings):
        """
        Applies the specified settings to the DRR configuration.
        
        Args:
            settings (dict): A dictionary of settings to apply.
        """
        for setting, value in settings.items():
            if hasattr(self.drr_settings, setting):
                setattr(self.drr_settings, setting, value)
            else:
                print(f"Warning: '{setting}' is not a valid DRR setting.")

    def show_settings(self):
        """Prints the current DRR settings."""
        print("Current DRR Settings:")
        for setting in self.BREAST_SETTINGS.keys():
            value = getattr(self.drr_settings, setting, 'N/A')
            print(f"  {setting}: {value}")

    def update_settings(self, **kwargs):
        """
        Updates the DRR settings dynamically.
        
        Args:
            **kwargs: Arbitrary keyword arguments for settings to update.
        """
        for setting, value in kwargs.items():
            if hasattr(self.drr_settings, setting):
                setattr(self.drr_settings, setting, value)
            else:
                print(f"Warning: '{setting}' is not a valid DRR setting.")
