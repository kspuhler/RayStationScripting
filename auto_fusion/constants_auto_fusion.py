"""
RaystationScriptingPROD\\AutoFusion\\constants_auto_fusion.py

Created on Wed Oct  1 09:50:27 2025

@author: clanco01


Constants for AutoFusion

"""
from typing import Optional, Dict
from enum import Enum

SKIP_POPUP_ROI_NAMES = ["GTVp", "Prostate", "Brain"]

REGISTRATION_TYPES = ["Frame of Reference", "Image Registration"]

ALLOWED_IMAGE_TYPES = ["CT", "MR"]

class DlsModel(Enum):
    MALE_PELVIS = "RSL DLS Male Pelvic CT"
    HEAD_NECK   = "RSL DLS Head and Neck CT"
    THORAX_ABD  = "RSL DLS Thorax-Abdomen CT"

# Primary mapping: model -> allowed structures (use frozenset for immutability)
DLS_MODEL_TO_STRUCTURES = {
    DlsModel.MALE_PELVIS: frozenset({"Prostate", "Femur_Head_L", "Femur_Head_R"}),
    DlsModel.HEAD_NECK:   frozenset({"Brain", "Bone_Mandible", "Trachea"}),
    DlsModel.THORAX_ABD:  frozenset({"Esophagus", "Heart", "Kidney_L", "Kidney_R", "Liver"}),
}

# Guard against ambiguous overlaps
_seen = {}
for model, names in DLS_MODEL_TO_STRUCTURES.items():
    for n in names:
        k = n.strip().replace(" ", "_").casefold()
        if k in _seen and _seen[k] != model:
            raise ValueError(
                f"Structure '{n}' is assigned to multiple models: "
                f"{_seen[k].name} and {model.name}"
            )
        _seen[k] = model

# Aliases or synonyms -> canonical names
STRUCTURE_ALIASES = {
    "Mandible": "Bone_Mandible",
    "FemoralHead_L": "Femur_Head_L",
    "FemoralHead_R": "Femur_Head_R",
}

# Name normalization (case-insensitive, strip spaces/underscores variants)
def normalize_name(name: str) -> str:
    return name.strip().replace(" ", "_")

# Reverse lookup: structure -> model
STRUCTURE_TO_MODEL: Dict[str, DlsModel] = {}
for model, names in DLS_MODEL_TO_STRUCTURES.items():
    for raw in names:
        STRUCTURE_TO_MODEL[normalize_name(raw).casefold()] = model

# Load aliases into reverse map
for alias, canonical in STRUCTURE_ALIASES.items():
    STRUCTURE_TO_MODEL[normalize_name(alias).casefold()] = STRUCTURE_TO_MODEL[
        normalize_name(canonical).casefold()
    ]

def dls_model_for(structure_name: str) -> Optional[DlsModel]:
    """Return the DlsModel to use for a given structure, or None if unsupported."""
    key = normalize_name(structure_name).casefold()
    return STRUCTURE_TO_MODEL.get(key)


ALLOWED_DLS_NAMES = sorted({
    n for names in DLS_MODEL_TO_STRUCTURES.values() for n in names
})
DLS_MODEL_NAMES = [m.value for m in DlsModel]

ALLOWED_PATIENT_POSITIONS = ["HFS", "HFP", "FFS", "FFP"]

ALIGNMENT_ROTATIONS = {
    # Head First Supine
    "HFS-HFS": {'YawDegrees': 0, 'PitchDegrees': 0, 'RollDegrees': 0},
    "HFP-HFS": {'YawDegrees': 0, 'PitchDegrees': 0, 'RollDegrees': 180},
    "FFS-HFS": {'YawDegrees': 180, 'PitchDegrees': 0, 'RollDegrees': 0},
    "FFP-HFS": {'YawDegrees': 180, 'PitchDegrees': 0, 'RollDegrees': 180},
    
    # Head First Prone
    "HFS-HFP": {'YawDegrees': 0, 'PitchDegrees': 0, 'RollDegrees': 180},
    "HFP-HFP": {'YawDegrees': 0, 'PitchDegrees': 0, 'RollDegrees': 0},
    "FFS-HFP": {'YawDegrees': 180, 'PitchDegrees': 0, 'RollDegrees': 180},
    "FFP-HFP": {'YawDegrees': 180, 'PitchDegrees': 0, 'RollDegrees': 0},
    
    # Feet First Supine
    "HFS-FFS": {'YawDegrees': 180, 'PitchDegrees': 0, 'RollDegrees': 0},
    "HFP-FFS": {'YawDegrees': 180, 'PitchDegrees': 0, 'RollDegrees': 180},
    "FFS-FFS": {'YawDegrees': 0, 'PitchDegrees': 0, 'RollDegrees': 0},
    "FFP-FFS": {'YawDegrees': 0, 'PitchDegrees': 0, 'RollDegrees': 180},
    
    # Feet First Supine
    "HFS-FFP": {'YawDegrees': 180, 'PitchDegrees': 0, 'RollDegrees': 180},
    "HFP-FFP": {'YawDegrees': 180, 'PitchDegrees': 0, 'RollDegrees': 0},
    "FFS-FFP": {'YawDegrees': 0, 'PitchDegrees': 0, 'RollDegrees': 180},
    "FFP-FFP": {'YawDegrees': 0, 'PitchDegrees': 0, 'RollDegrees': 0},
}


