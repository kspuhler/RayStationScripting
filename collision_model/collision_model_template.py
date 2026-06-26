"""
collision_model/collision_model_template.py

Generates Collision_Model Varian ROIs with global settings

Usage: 
    Run script to generate a new set of Collision Model ROIs
    Save only the newly generated ROIs in structure template 'Collision_Model'
    Set 'Collsion_Model' properties to align image centers
    
Physical Assumptions (TrueBeam/EX):
    isocenter-to-collimator = 35 cm
    collimator head is a square of side length = 80 cm
    "safe" region defined by INNER_RAD_VARIAN in CONFIGURATION below

Created on Wed Jan  7 11:40:18 2026

@author: clanco01
"""

# === WORKING DIRECTORY ===
import sys
sys.path.append(r"\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
sys.path.append(r"F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")

# === Local imports ===
from RSutil.patient_data_util import PatientDataUtil


# ====== CONFIGURATION =======

# 1D Settings Varian
INNER_RAD_VARIAN = 33 # cm
OUTER_RAD_VARIAN = 50
CYL_LENGTH_VARIAN = 80
HP_LENGTH = 100 # Inf-Sup
HP_WIDTH = 120 # Left-Right
HP_HEIGHT = 80 # Ant-Post
HEAD_LENGTH = CYL_LENGTH_VARIAN
HEAD_WIDTH = CYL_LENGTH_VARIAN
HEAD_HEIGHT = 40

# Sizes
SIZE_HP = { 'x': HP_WIDTH, 'y': HP_HEIGHT, 'z': HP_LENGTH }
SIZE_HEAD = { 'x': CYL_LENGTH_VARIAN, 'y': HEAD_HEIGHT, 'z': CYL_LENGTH_VARIAN }

# Cylinder Axis Orientation
CYL_AXIS = { 'x': 0, 'y': 0, 'z': 1 }

# Centers
CENTER_ZERO = { 'x': 0, 'y': 0, 'z': 0 }
CENTER_HP = { 'x': 0, 'y': -HP_HEIGHT/2, 'z': 0 }
CENTER_HEAD = { 'x': 0, 'y': -INNER_RAD_VARIAN - HEAD_HEIGHT/2, 'z': 0 }

# ROI Names
RadialBand = "COLL_RadialBand"     
HPs = "COLL_HP_Start"
HPt = "COLL_HP_Stop"
Hs = "COLL_Head_Start"
Ht = "COLL_Head_Stop"

# ROI Names to delete
inner = "inner"
outer = "outer"
roi_to_delete = (inner, outer)

# Margin settings
ZERO_MARGIN = { 'Type': "Expand", 'Superior': 0, 'Inferior': 0, 'Anterior': 0, 'Posterior': 0, 'Right': 0, 'Left': 0 }


# ====== Open phantom ========
pdu = PatientDataUtil(
    patient_id="0000Collision",
    case_name="Model",
    plan_name="Collision_Model",
    beamset_name="CollisionModel",
)
case = pdu.get_current_case()
examination = pdu.get_current_exam()


# ====== CREATE MODEL ROIS ====

cyl_inner = case.PatientModel.CreateRoi(
    Name=inner, 
    Color="Green", 
    Type="Control", 
    TissueName=None, 
    RbeCellTypeName=None, 
    RoiMaterial=None
)
cyl_inner.CreateCylinderGeometry(
    Radius=INNER_RAD_VARIAN, 
    Axis=CYL_AXIS, 
    Length=CYL_LENGTH_VARIAN, 
    Examination=examination, 
    Center=CENTER_ZERO, 
    Representation="TriangleMesh", 
    VoxelSize=None
)


cyl_outer = case.PatientModel.CreateRoi(
    Name=outer, 
    Color="Pink", 
    Type="Control", 
    TissueName=None, 
    RbeCellTypeName=None, 
    RoiMaterial=None
)
cyl_outer.CreateCylinderGeometry(
    Radius=OUTER_RAD_VARIAN, 
    Axis=CYL_AXIS, 
    Length=CYL_LENGTH_VARIAN, 
    Examination=examination, 
    Center=CENTER_ZERO, 
    Representation="TriangleMesh", 
    VoxelSize=None
)


hp_start = case.PatientModel.CreateRoi(
    Name=HPs, 
    Color="0, 128, 255", 
    Type="Control", 
    TissueName=None, 
    RbeCellTypeName=None, 
    RoiMaterial=None
)
hp_start.CreateBoxGeometry(
    Size=SIZE_HP, 
    Examination=examination, 
    Center=CENTER_HP, 
    Representation="TriangleMesh", 
    VoxelSize=None
)


hp_stop = case.PatientModel.CreateRoi(
    Name=HPt, 
    Color="0, 255, 128", 
    Type="Control", 
    TissueName=None, 
    RbeCellTypeName=None, 
    RoiMaterial=None
)
hp_stop.CreateBoxGeometry(
    Size=SIZE_HP, 
    Examination=examination, 
    Center=CENTER_HP, 
    Representation="TriangleMesh", 
    VoxelSize=None
)


head_start = case.PatientModel.CreateRoi(
    Name=Hs, 
    Color="255, 128, 255", 
    Type="Control", 
    TissueName=None, 
    RbeCellTypeName=None, 
    RoiMaterial=None
)
head_start.CreateBoxGeometry(
    Size=SIZE_HEAD, 
    Examination=examination, 
    Center=CENTER_HEAD, 
    Representation="TriangleMesh", 
    VoxelSize=None
)


head_stop = case.PatientModel.CreateRoi(
    Name=Ht, 
    Color="Green", 
    Type="Control", 
    TissueName=None, 
    RbeCellTypeName=None, 
    RoiMaterial=None
)
head_stop.CreateBoxGeometry(
    Size=SIZE_HEAD, 
    Examination=examination, 
    Center=CENTER_HEAD, 
    Representation="TriangleMesh", 
    VoxelSize=None
)

# ===== CREATE RADIAL BANDS ========
radial_bands = case.PatientModel.CreateRoi(
    Name="COLL_RadialBand", 
    Color="Cyan", 
    Type="Control", 
    TissueName=None, 
    RbeCellTypeName=None, 
    RoiMaterial=None
)
radial_bands.CreateAlgebraGeometry(
    Examination=examination, 
    Algorithm="Auto", 
    ExpressionA={ 
        'Operation': "Union", 
        'SourceRoiNames': [outer], 
        'MarginSettings': ZERO_MARGIN 
    }, 
    ExpressionB={ 
        'Operation': "Union", 
        'SourceRoiNames': [inner], 
        'MarginSettings': ZERO_MARGIN 
    }, 
    ResultOperation="Subtraction", 
    ResultMarginSettings=ZERO_MARGIN
)


# ======== DELETE UNUSED ROIS ========
cyl_inner.DeleteRoi()

cyl_outer.DeleteRoi()

 






















