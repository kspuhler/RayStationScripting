'''
collision_model/main_collision_model.py

An ROI is created as a geometric model of EX, TrueBeams, and Radixact machines.
The overlap of the model with External, Fixation, Support, and Bolus ROIs determines
the binary output of Pass/Fail.  

Varian machines uses the 'Collision_Model' in Raystation.  To uppdate the model 
in Structure Templates:
    
    Run 'collision_model_template.py'
    See docstring in that module.

The Radixact model is built per patient.

Physical Assumptions:
    
    TrueBeam/EX:
        isocenter-to-collimator = 35 cm
        collimator head is a square of side length = 80 cm
        "safe" region defined by INNER_RAD_VARIAN in collision_model_template.py
        Default "safe" is the an isocenter-to-collimator distance of 33 cm
    
    Radixact:
        Bore Radius = 42.5 cm
        "Safe" Bore Radius = 40.5 cm
        Bore length (sup-inf) = length of patient CT

'''

from __future__ import annotations

# === DEBUG SETTINGS ===
_DEBUG_THIS_MODULE = False
_ALERT_PHYSICIST_ON_ALL_USES = True

# === Raystation import ===
try:
    from connect import set_progress, await_user_input
except Exception:
    pass

# === WORKING DIRECTORY ===
import sys
sys.path.append(r"\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
sys.path.append(r"F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
ss = "\\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD\SantoroSleekStylesheet.css"

# === Standard Imports ===
import math
from typing import Optional
import time
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt

# === Local imports ===
from RSutil.patient_data_util import PatientDataUtil
from RSutil.LogUtil.rs_logging import LOGGERS, set_logger_mode
from RSutil.ErrorsUtil.error_dispatcher import DispatcherConfig
from RSutil.ErrorsUtil.rs_errors import report_error
from RSutil.ErrorsUtil.error_codes import PROMPT_USER, ALERT_PHYSICIST, ABORT_SCRIPT
from RSutil.variables import RADIXACTS, EX, VARIAN_MACHINES

# === Setup Logger ===
_logger = LOGGERS["collision_model"]
if _DEBUG_THIS_MODULE:
    set_logger_mode(_logger, "debug")


# === Helper Functions ===
def show_message(message="Pass!", title="Collision Model Message"):
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    with open(ss, "r", encoding="utf-8") as f:
        app.setStyleSheet(f.read())

    app.setStyle("Fusion")

    box = QMessageBox()
    box.setWindowTitle(title)
    box.setText(message)
    box.setIcon(QMessageBox.Information)
    box.setStandardButtons(QMessageBox.Ok)
    box.setWindowFlag(Qt.WindowStaysOnTopHint, True)
    box.show()
    app.processEvents()

    return box


# === Error Handling ===
def _alert_physicist_error(
        exc: Exception, 
        metadata: Optional[dict] = None, 
        message: Optional[str] = None
):
    if not _DEBUG_THIS_MODULE:                                           
        cfg = DispatcherConfig()
        cfg.alert_recipients = ["owen.clancey@nyulangone.org"]
        report_error(
                error_def=ALERT_PHYSICIST.SYSF_UNHANDLED_EXCEPTION, 
                original_exception=exc, 
                context={"module": "main_collision_model.py"},
                metadata=metadata,
                message=message,
                dispatcher_config=cfg,
            )

if _ALERT_PHYSICIST_ON_ALL_USES:
    message = "Running main_collision_model"
    e = RuntimeError("INFO ONLY - Collision Model initialized.  Review patient data in logs.")
    _alert_physicist_error(e, message=message)
    
def _abort_script_error(
        exc: Exception, 
        metadata: Optional[dict] = None, 
        message: Optional[str] = None
):
    
    report_error(
            error_def=ABORT_SCRIPT.DATA_REQUIRED_MISSING, 
            original_exception=exc, 
            context={"module": "main_collision_model.py"},
            metadata={},
            message=message,
        )
    raise RuntimeError(str(exc))


def _prompt_user_acknowledge(
        exc: Exception, 
        metadata: Optional[dict] = None, 
        message: Optional[str] = None
):                                                  
    outcome = report_error(
            error_def=PROMPT_USER.UIUX_USER_ACKNOWLEDGE, 
            original_exception=exc, 
            context={"module": "main_collision_model.py"},
            metadata={},
            message=message,
        )
    return outcome

# ================== CONSTANTS / CONFIG ======================

# Shared Collision Model ROIs
COLLISION_ROI = "COLL_ROI"
COLLISION_MODEL = "COLL_Model"

# User message for PASS/FAIL
MSG_PASS = "Pass!"
MSG_FAIL = "[FAILED] - Review COLL_ROIs.  Possible collision detected at the following isocenters:"

# Gantry->XY rotation angle calibration (one-time)
SIGN = 1.0
OFFSET = 0
OFFSET_HP = 90

# Zero margin geometry algebra dictionary
ZERO_MARGIN = { 
    'Type': "Expand", 
    'Superior': 0, 
    'Inferior': 0, 
    'Anterior': 0, 
    'Posterior': 0, 
    'Right': 0, 
    'Left': 0 
}

# ---------Varian -----------
# See Collision Model in RayStation Structure Template Manager
RADIALBAND = "COLL_RadialBand"     
HPs = "COLL_HP_Start"
HPt = "COLL_HP_Stop"
Hs = "COLL_Head_Start"
Ht = "COLL_Head_Stop"
COLLISION_MODEL_VISUAL = "COLL_Model_Visual"


ROI_SET_VARIAN = {
    RADIALBAND, 
    HPs, 
    HPt, 
    Hs, 
    Ht, 
    COLLISION_MODEL, 
    COLLISION_MODEL_VISUAL,
}

COLL_VARIAN_TEMPLATE_ROIS = [
    "COLL_HP_Start",
    "COLL_HP_Stop",
    "COLL_Head_Start",
    "COLL_Head_Stop",
    "COLL_RadialBand",
]
COUCH_TB_TEMPLATE_ROIS = [
    "CouchRailLeft_In",
    "CouchSurface",
    "CouchRailRight_In",
    "CouchInterior",    
]

TEMPLATE_EXAM_NAME = "CT 1"
COUCH_TB_TEMPLATE_NAME = "TB Couch Clinical - Rails In"
VARIAN_COLL_TEMPLATE_NAME = "Collision_Model"

# ------ Radixact ------
CYL_AXIS = { 'x': 0, 'y': 0, 'z': 1 }
INNER_RAD_RADIXACT = 40.5
OUTER_RAD_RADIXACT = 55
CYL_INNER = "inner"
CYL_OUTER = "outer"

ROI_SET_RADIXACT = {CYL_INNER, CYL_OUTER, COLLISION_MODEL}

COUCH_RAD_TEMPLATE_ROIS = [
    "Lower pallet",
    "Upper pallet",
]
COUCH_RAD_TEMPLATE_NAME = "Radixact Couch"


# ================== MAIN CLASS ======================

class CollisionModel:
        
    def __init__(self, display_output: bool = True):
        # Supress user outputs when False
        self.display_output = display_output
    
        # Patient Data
        try:
            self.pdu = PatientDataUtil()
            self.plan = self.pdu.get_current_plan()
            self.plan_name = self.pdu.get_current_plan_name()
            self.beamset_names = self.pdu.get_beamset_names_in_plan(self.plan_name)
            self.beamsets = self.pdu.get_beamsets_in_plan(self.plan_name)
            self.exam = self.pdu.get_current_exam()
            self.exam_name = self.pdu.get_current_exam_name()
            self.pm = self.pdu.get_current_patient_model()
            self.db = self.pdu.get_current_patient_db()
        except Exception as e:
            _prompt_user_acknowledge(
                exc=e, 
                message="[FAILED] to initialize script.  Verify a plan with a beamset is open."
            )
            raise RuntimeError(e)
        
        
        # Loop counter and user final message
        self.user_msg = []
        self.iso_index = 0
        
        # Flag for deleting an inserted couch
        self.delete_couch = False
        
        # Output result dictionary
        self.result = {
            "passed": True,
            "machine_name": "",
            "plan_name": self.plan_name,
            "failures": [], 
                # Example dictionary syntax: 
                #     {
                #         "iso_index": 0, 
                #         "iso_pos": iso, 
                #         "collision_volume_cc": vol,
                #         "collision_roi_name": name,
                #     }
            "message": ""
        }

    # ------------------ TRANSFORMS ------------------
    
    def theta_from_gantry(self, g):
        result = (SIGN*g + OFFSET) % 360.0
        _logger.debug("Gantry Theta: %s", result)
        return result
    
    @staticmethod
    def _xyz(p):
        try:
            return float(p.x), float(p.y), float(p.z)
        except Exception:
            return float(p["x"]), float(p["y"]), float(p["z"])
    
    def T(self, p):
        x, y, z = self._xyz(p)
        return {
            'M11':1,'M12':0,'M13':0,'M14':x,
            'M21':0,'M22':1,'M23':0,'M24':y,
            'M31':0,'M32':0,'M33':1,'M34':z,
            'M41':0,'M42':0,'M43':0,'M44':1
        }
    
    def Rz_about(self, p, deg):
        x0, y0, _ = self._xyz(p)
        th = math.radians(deg)
        c, s = math.cos(th), math.sin(th)
        r11, r12 = c, -s
        r21, r22 = s,  c
        tx = x0 - (r11*x0 + r12*y0)
        ty = y0 - (r21*x0 + r22*y0)
        return {
            'M11':r11,'M12':r12,'M13':0,'M14':tx,
            'M21':r21,'M22':r22,'M23':0,'M24':ty,
            'M31':0,  'M32':0,  'M33':1,'M34':0,
            'M41':0,  'M42':0,  'M43':0,'M44':1
        }
    
    @staticmethod
    def span_ccw(a, b):
        return (b - a) % 360.0

    def _matmul(self, A, B):
        def g(M, r, c): return float(M[f"M{r}{c}"])
        C = {}
        for r in range(1, 5):
            for c in range(1, 5):
                C[f"M{r}{c}"] = (
                    g(A,r,1)*g(B,1,c) + g(A,r,2)*g(B,2,c) +
                    g(A,r,3)*g(B,3,c) + g(A,r,4)*g(B,4,c)
                )
        return C

    def transform_model_template(self, iso, th_s, th_t):
        
        Tiso = self.T(iso)

        M_HPs = self._matmul(self.Rz_about(iso, th_s + OFFSET_HP), Tiso)
        M_HPt = self._matmul(self.Rz_about(iso, th_t - OFFSET_HP), Tiso)
        M_Hs  = self._matmul(self.Rz_about(iso, th_s),            Tiso)
        M_Ht  = self._matmul(self.Rz_about(iso, th_t),            Tiso)
        
        self.pm.RegionsOfInterest[HPs].TransformROI3D(Examination=self.exam, TransformationMatrix=M_HPs)
        self.pm.RegionsOfInterest[HPt].TransformROI3D(Examination=self.exam, TransformationMatrix=M_HPt)
        self.pm.RegionsOfInterest[Hs ].TransformROI3D(Examination=self.exam, TransformationMatrix=M_Hs)
        self.pm.RegionsOfInterest[Ht ].TransformROI3D(Examination=self.exam, TransformationMatrix=M_Ht)
        self.pm.RegionsOfInterest[RADIALBAND].TransformROI3D(Examination=self.exam, TransformationMatrix=Tiso)  
    
    # ----------------- PLAN HELPERS --------
    @staticmethod
    def _iso_key(pos, mm_tol=0.5):
        """Bucket isocenters by rounding in mm (RayStation coords are mm)."""
        q = float(mm_tol)
        return (round(pos.x / q) * q, round(pos.y / q) * q, round(pos.z / q) * q)
    
    @staticmethod
    def _norm_deg(a):
        return float(a) % 360.0

    def check_for_dose(self):
        beamset_names = self.pdu.get_beamset_names_in_plan(self.plan_name)
        for bs_name in beamset_names:
            if self.pdu.has_dose_on_plan_beamset(self.plan_name, bs_name):
                return True
        return False

    def check_for_approval(self):
        try:
            if self.plan.Review.ApprovalStatus == "Approved":
                return True
        except Exception:
            pass
        
        beamsets = self.pdu.get_beamsets_in_plan(self.plan_name)
        try:
            for beamset in beamsets:
                if beamset.Review.ApprovalStatus == "Approved":
                    return True
        except Exception:
            pass
        
        return False

    def get_radixact_iso(self, tol=1):
        """
        Angles collected per beam:
          - DynamicArc: beam.GantryAngle and beam.ArcStopGantryAngle
          - else:       beam.GantryAngle (static)
        """
        _logger.debug("Retrieving Radixact Isocenters...")
        results = {}
        
        for bs in self.beamsets:
            for b in bs.Beams:
                if getattr(b, "IsSetupBeam", False):
                    continue
        
                iso = self.pdu.get_iso_in_beam(b)
                iso_key = (round(iso["x"]/tol)*tol, round(iso["y"]/tol)*tol, round(iso["z"]/tol)*tol)
                iso_rounded = {k: round(float(iso[k]), 2) for k in ("x", "y", "z")}
                results[iso_key] = {"iso_pos": iso_rounded}
        
        _logger.debug("Retrieved Radixact Isocenters: %s", results)
        return results
    
    def get_varian_iso_start_stop(self, tol=1.0):
        """
        Angles collected per beam:
          - DynamicArc: beam.GantryAngle and beam.ArcStopGantryAngle
          - else:       beam.GantryAngle (static)
        """
        
        results = {}
        angles_by_iso = {}   # iso_bucket -> {"iso_pos": {...}, "angles": set()}
        
        for bs in self.beamsets:
            for b in bs.Beams:
                if getattr(b, "IsSetupBeam", False):
                    continue
        
                iso = self.pdu.get_iso_in_beam(b)
                _logger.debug("Retrieved Isocenter: %s", iso)
                key = (round(iso["x"]/tol)*tol, round(iso["y"]/tol)*tol, round(iso["z"]/tol)*tol)
        
                s = angles_by_iso.setdefault(key, {"iso_pos": iso, "angles": set()})["angles"]
        
                gantry = round(float(b.GantryAngle) % 360.0, 6)
                if getattr(b, "DeliveryTechnique", "") == "DynamicArc":
                    if getattr(b, "ArcRotationDirection", "") == "Clockwise" and gantry == 180.0:
                        gantry = 180.1
                    if getattr(b, "ArcRotationDirection", "") == "CounterClockwise" and gantry == 180.0:
                        gantry = 179.9
                    
                    
                # always include gantry angle
                s.add(gantry)
        
                # if arc, include stop gantry too
                if getattr(b, "DeliveryTechnique", "") == "DynamicArc":
                    gantry_stop = round(float(b.ArcStopGantryAngle) % 360.0, 6)
                
                    if getattr(b, "ArcRotationDirection", "") == "Clockwise" and gantry_stop == 180.0:
                        gantry_stop = 179.9
                    if getattr(b, "ArcRotationDirection", "") == "CounterClockwise" and gantry_stop == 180.0:
                        gantry_stop = 180.1
                
                    s.add(gantry_stop)
        
        for iso_key, v in angles_by_iso.items():
            angles = sorted(v["angles"])
            iso = v["iso_pos"]
            iso_rounded = {k: round(float(iso[k]), 2) for k in ("x", "y", "z")}
            _logger.debug("Angles: %s", angles)
            if not angles:
                continue
            
            is_ap_pa = set(round(a % 360.0, 6) for a in angles) == {0.0, 180.0}
            if is_ap_pa:
                results[iso_key] = {
                    "iso_pos": iso_rounded,
                    "start_gantry": 0.0,
                    "stop_gantry":  180.0,
                    "is_ap_pa": is_ap_pa,
                }
                continue
               
            eps = 0.1
            tol = 1e-6
            nearest = min((a for a in angles if abs(a - 180.0) > tol),
              key=lambda a: (abs(a - 180.0), 0 if a > 180.0 else 1))
    
            nudged_180 = 180.0 + eps if nearest > 180.0 else 180.0 - eps
    
            angles = [nudged_180 if abs(a - 180.0) <= tol else a for a in angles]    
    
            angles_ge_180 = [a for a in angles if a >= 180.0]
            angles_le_180 = [a for a in angles if a <= 180.0]
        
            # Angles on both sides of 180 
            if angles_ge_180 and angles_le_180:
                start_gantry = min(angles_ge_180)
                stop_gantry  = max(angles_le_180)
        
            # ALL angles are <= 180 
            elif angles_le_180:
                start_gantry = min(angles_le_180)
                stop_gantry  = max(angles_le_180)
        
            # ALL angles are >= 180
            else:
                start_gantry = min(angles_ge_180)
                stop_gantry  = max(angles_ge_180)
        
            results[iso_key] = {
                "iso_pos": iso_rounded,
                "start_gantry": start_gantry,
                "stop_gantry":  stop_gantry,
                "is_ap_pa": is_ap_pa,
            }
        
        _logger.debug("Iso Start Stop Results: %s", results)
        
        return results
    
    
    # ----------------- ROI HELPERS ------------------
    
    def no_beams_exist(self, iso):
        if not iso:
            msg = "The plan contains no beams for the collision model.  Script will exit."
            _logger.debug(msg)
            self.result["passed"] = False
            self.result["message"] = msg
            if self.display_output:
                set_progress("Waiting on user hit play button...", percentage = -1)
                await_user_input(message=msg)
            return True
        return False
          
    def import_template(self, template_name, source_roi_names):
        try:
            self.delete_rois(source_roi_names)
            
            template_pm = self.db.LoadTemplatePatientModel(
                templateName=template_name,  # template name in your RS DB
                lockMode='Read'  # or 'Write' / None as needed
            )
        
            self.pm.CreateStructuresFromTemplate(
                SourceTemplate=template_pm,
                SourceExaminationName=TEMPLATE_EXAM_NAME,  # must match the exam name in the template
                SourceRoiNames=source_roi_names,
                SourcePoiNames=[],             # add POIs here if you want any
                AssociateStructuresByName=True,
                TargetExamination=self.exam,
                InitializationOption="AlignImageCenters"  # or "EmptyGeometries", "RigidRegistration", etc.
            )
        except Exception as e:
            await_user_input(message=f"Failed to import Collision Model template.  Make sure the following structures do not exist: {source_roi_names}")
            raise RuntimeError(e)

    def delete_rois(self, delete_roi_names):
        for roi_name in delete_roi_names:
            _logger.debug("ROI name to delete: %s", roi_name)
            try:
                self.pm.RegionsOfInterest[roi_name].DeleteRoi()
            except Exception:
                _logger.debug("Deletion of roi_name not in ROI_SET_VARIAN due to AP-PA collsion model.")
                pass

    def has_support_rois(self):
        want = ("Support")
        rois = self.pdu.get_rois_with_contours_on_ct(self.exam_name)
        for roi in rois:
            name = roi.OfRoi.Name
            if name.startswith("COLL_"):
                continue
            if str(roi.OfRoi.Type) in want:
                return True
        
        return False

    def has_couch(self, couch_roi_names):
        roi_names = self.pdu.get_roi_names_with_contours_on_ct(self.exam_name)
        missing = [x for x in couch_roi_names if x not in roi_names]
        _logger.info("Missing Couch ROIs in has_couch: %s", missing)
        return not missing       

        
    # -------------- COLLISION MODELS -------------------
    
    def varian_collision_model(self, span):
        
        Operation = "Intersection" if span < 180 else "Union"

        try:
            roi_model = self.pm.CreateRoi(
                Name=COLLISION_MODEL, 
                Color="Magenta", 
                Type="Control", 
                TissueName=None, 
                RbeCellTypeName=None, 
                RoiMaterial=None
            )
        except Exception:
            roi_model = self.pm.RegionsOfInterest[COLLISION_MODEL]
            _logger.warning("Failed to create %s.  Likely already exists.", COLLISION_MODEL)

        roi_model.CreateAlgebraGeometry(
            Examination=self.exam, 
            Algorithm="Auto", 
            ExpressionA={ 
                'Operation': Operation, 
                'SourceRoiNames': [HPs, HPt], 
                'MarginSettings': ZERO_MARGIN,
            }, 
            ExpressionB={ 
                'Operation': "Union", 
                'SourceRoiNames': [RADIALBAND], 
                'MarginSettings': ZERO_MARGIN,
            }, 
            ResultOperation="Intersection", 
            ResultMarginSettings=ZERO_MARGIN,
        )

        _logger.debug("Full [Non-AP-PA] Collision model created...")
        
   
    def varian_collision_model_appa(self):
        try:
            roi_model = self.pm.CreateRoi(
                Name=COLLISION_MODEL, 
                Color="Magenta", 
                Type="Control", 
                TissueName=None, 
                RbeCellTypeName=None, 
                RoiMaterial=None
            )
        except Exception:
            roi_model = self.pm.RegionsOfInterest[COLLISION_MODEL]
            _logger.warning("Failed to create %s.  Likely already exists.", COLLISION_MODEL)
         
        roi_model.CreateAlgebraGeometry(
            Examination=self.exam, 
            Algorithm="Auto", 
            ExpressionA={ 
                'Operation': "Union", 
                'SourceRoiNames': [Hs, Ht], 
                'MarginSettings': ZERO_MARGIN,
            }, 
            ExpressionB={ 
                'Operation': "Union", 
                'SourceRoiNames': [], 
                'MarginSettings': ZERO_MARGIN, 
            }, 
            ResultOperation="None", 
            ResultMarginSettings=ZERO_MARGIN,
        )
        
        _logger.debug("AP-PA Collision model created...")

    def radixact_collision_model(self, iso):
        ct_length = abs(self.exam.Series[0].ImageStack.SlicePositions[-1] - self.exam.Series[0].ImageStack.SlicePositions[0])
        cyl_length = ct_length + 2
        z_coord = ct_length/2 + self.exam.Series[0].ImageStack.Corner.z
        center = { 'x': iso["x"], 'y': iso["y"], 'z': z_coord }
        
        try:
            cyl_inner = self.pm.CreateRoi(
                Name=CYL_INNER, 
                Color="Green", 
                Type="Control", 
                TissueName=None, 
                RbeCellTypeName=None, 
                RoiMaterial=None
            )
        except Exception:
            cyl_inner = self.pm.RegionsOfInterest[CYL_INNER]
            _logger.warning("Failed to create %s.  Likely already exists.", CYL_INNER)
            
        cyl_inner.CreateCylinderGeometry(
            Radius=INNER_RAD_RADIXACT, 
            Axis=CYL_AXIS, 
            Length=cyl_length, 
            Examination=self.exam, 
            Center=center, 
            Representation="TriangleMesh", 
            VoxelSize=None
        )
        
        try:
            cyl_outer = self.pm.CreateRoi(
                Name=CYL_OUTER, 
                Color="Pink", 
                Type="Control", 
                TissueName=None, 
                RbeCellTypeName=None, 
                RoiMaterial=None
            )
        except Exception:
            cyl_outer = self.pm.RegionsOfInterest[CYL_OUTER]
            _logger.warning("Failed to create %s.  Likely already exists.", CYL_OUTER)
            
        cyl_outer.CreateCylinderGeometry(
            Radius=OUTER_RAD_RADIXACT, 
            Axis=CYL_AXIS, 
            Length=cyl_length, 
            Examination=self.exam, 
            Center=center, 
            Representation="TriangleMesh", 
            VoxelSize=None
        )
    
        # Create radial bands
        try:
            roi_model = self.pm.CreateRoi(
                Name=COLLISION_MODEL, 
                Color="Magenta", 
                Type="Control", 
                TissueName=None, 
                RbeCellTypeName=None, 
                RoiMaterial=None
            )
        except Exception:
            roi_model = self.pm.RegionsOfInterest[COLLISION_MODEL]
            _logger.warning("Failed to create %s.  Likely already exists.", COLLISION_MODEL)
    
        roi_model.CreateAlgebraGeometry(
            Examination=self.exam, 
            Algorithm="Auto", 
            ExpressionA={ 
                'Operation': "Union", 
                'SourceRoiNames': [CYL_OUTER], 
                'MarginSettings': ZERO_MARGIN
            }, 
            ExpressionB={ 
                'Operation': "Union", 
                'SourceRoiNames': [CYL_INNER], 
                'MarginSettings': ZERO_MARGIN
            }, 
            ResultOperation="Subtraction", 
            ResultMarginSettings=ZERO_MARGIN
        )

    def get_obstacle_roi_names(self):
        want = ("External", "Fixation", "Support", "Bolus")
        out = []
        rois = self.pdu.get_rois_on_ct(self.exam_name)
        
        for roi in rois:
            name = roi.OfRoi.Name
            if name.startswith("COLL_"):
                continue
            if str(roi.OfRoi.Type) in want:
                out.append(name)
        
        return out
    

    def check_machine_name(self):
        machine_names = []
        for bs_name in self.beamset_names:
            machine_names.append(self.pdu.get_machine_in_plan_beamset(self.plan_name, bs_name))
            
        return list(set(machine_names))
    
    def create_collision_roi(self, coll_roi_list=[COLLISION_MODEL]):
        
        obstacle_names = self.get_obstacle_roi_names()
        _logger.debug("Obstacles ROI list: %s", obstacle_names)
        try:
            roi_collision = self.pm.CreateRoi(
                Name=COLLISION_ROI, 
                Color="Red", 
                Type="Control", 
                TissueName=None, 
                RbeCellTypeName=None, 
                RoiMaterial=None
            )
            _logger.debug("Created empty Collision ROI...")
        except Exception:
            roi_collision = self.pm.RegionsOfInterest[COLLISION_ROI]
            _logger.warning("Failed to create %s.  Likely already exists.", COLLISION_ROI)
        
        # For visualization
        if _DEBUG_THIS_MODULE:
            try:
                _logger.debug("Creating a Collsion Model Visualization ROI for debugging...")
                roi_visual = self.pm.CreateRoi(
                    Name=COLLISION_MODEL_VISUAL, 
                    Color="Red", 
                    Type="Control", 
                    TissueName=None, 
                    RbeCellTypeName=None, 
                    RoiMaterial=None
                )
                _logger.debug("Created empty Collision Model Visualization ROI...")
            except Exception:
                roi_visual = self.pm.RegionsOfInterest[COLLISION_MODEL_VISUAL]
                _logger.warning("Failed to create %s.  Likely already exists.", COLLISION_MODEL_VISUAL)
            
            
            roi_visual.CreateAlgebraGeometry(
                Examination=self.exam, 
                Algorithm="Auto", 
                ExpressionA={ 
                    'Operation': "Union", 
                    'SourceRoiNames': coll_roi_list, 
                    'MarginSettings': ZERO_MARGIN,
                }, 
                ExpressionB={ 
                    'Operation': "Union", 
                    'SourceRoiNames': [], 
                    'MarginSettings': ZERO_MARGIN, 
                }, 
                ResultOperation="None", 
                ResultMarginSettings=ZERO_MARGIN,
            )
        
        roi_collision.SetAlgebraExpression(
            ExpressionA={ 
                'Operation': "Union", 
                'SourceRoiNames': obstacle_names, 
                'MarginSettings': ZERO_MARGIN,
            }, 
            ExpressionB={ 
                'Operation': "Union", 
                'SourceRoiNames': coll_roi_list, 
                'MarginSettings': ZERO_MARGIN,
            }, 
            ResultOperation="Intersection", 
            ResultMarginSettings=ZERO_MARGIN,
        )
        _logger.debug("Geometry Algebra completed for Collision ROI...")
    
        roi_collision.UpdateDerivedGeometry(Examination=self.exam, Algorithm="Auto")
        _logger.debug("Updated derived geometry for Collision ROI...")
        
        
    def detect_collision(self, iso, ):
        
        # Get final collision ROI volume
        vol = self.pdu.get_volume_of_roi_on_ct(COLLISION_ROI, self.exam_name)
        collision_detected = self.pdu.has_contours_on_ct(COLLISION_ROI, self.exam_name)
        
        if collision_detected:
            _logger.info(f"Collision ROI: {COLLISION_ROI}, cc: {round(vol, 2)}")
            name = COLLISION_ROI + "_" + str(self.iso_index)
            unique_name = self.pm.GetUniqueRoiName(DesiredName=name)
            self.user_msg.append(
                f"Iso_{self.iso_index}: {iso}\n\nCollision Vol {unique_name}: {round(vol, 2)} cc"
            )
            self.pm.RegionsOfInterest[COLLISION_ROI].Name = unique_name
            self.result["passed"] = False
            self.result["failures"].append({
                "iso_index": self.iso_index, 
                "iso_pos": iso, 
                "collision_volume_cc": vol,
                "collision_roi_name": unique_name,
            })
            
            self.iso_index += 1
            
        else:
            self.pm.RegionsOfInterest[COLLISION_ROI].DeleteRoi()
        
    # ------------------ MAIN ------------------
    
    def main(self):
    
        try:
            t0_main = time.perf_counter()
            set_progress("Running collision model...", percentage = -1)
            
            _logger.info("Running main loop...")
            
            if len(self.beamset_names) < 1:
                msg = "The plan contains no beamsets for the collision model.  Script will exit."
                _logger.debug(msg)
                self.result["passed"] = False
                self.result["message"] = msg
                if self.display_output:
                    set_progress("Waiting on user hit play button...", percentage = -1)
                    await_user_input(message=msg)
                return self.result
            
            machine_name_list = self.check_machine_name()
            
            if len(machine_name_list) != 1:
                msg = f"Multiple or zero machines are not supported: {machine_name_list}"
                _logger.debug(msg)
                self.result["passed"] = False
                self.result["message"] = msg
                if self.display_output:
                    set_progress("Waiting on user hit play button...", percentage = -1)
                    await_user_input(message=msg)
                return self.result
            
            machine_name = machine_name_list[0]
            
            self.result["machine_name"] = machine_name
            
            if machine_name in RADIXACTS:
                _logger.info("Radixact machine collision model being used.")
                if not self.has_couch(COUCH_RAD_TEMPLATE_ROIS):
                    self.import_template(COUCH_RAD_TEMPLATE_NAME, COUCH_RAD_TEMPLATE_ROIS)
                    set_progress("Waiting on user finalize Radixact couch...", percentage = -1)
                    await_user_input(message="Finalize placement of Radixact couch.  Then, hit Play.")
                
                set_progress("Running collision model...", percentage = -1)
                t0 = time.perf_counter()
                iso_dict = self.get_radixact_iso()
                dt = time.perf_counter() - t0
                _logger.debug("Time to complete get_radixact_iso():  %.1f sec", dt)
                
                if self.no_beams_exist(iso_dict):
                    return self.result
                
                for key, v in iso_dict.items():
                    iso = v["iso_pos"]
                    
                    # Create collsion model
                    t0 = time.perf_counter()
                    self.radixact_collision_model(iso)
                    dt = time.perf_counter() - t0
                    _logger.debug("Time to complete radixact_collision_model():  %.1f sec", dt)
                    
                    # Create the collision overlap ROI
                    self.create_collision_roi()
                    _logger.info("Overlap Collision ROI created...")
                    
                    # Detect collision
                    t0 = time.perf_counter()
                    self.detect_collision(iso)
                    dt = time.perf_counter() - t0
                    _logger.debug("Time to complete detect_collision():  %.1f sec", dt)
                    
                    # Delete ROIs
                    t0 = time.perf_counter()
                    self.delete_rois(ROI_SET_RADIXACT)
                    dt = time.perf_counter() - t0
                    _logger.debug("Time to complete delete_rois():  %.1f sec", dt)
                    
                    _logger.info("Finished collision model for iso: %s", iso)
                    
                
            elif machine_name in VARIAN_MACHINES:
                _logger.info("Varian machine collision model being used.")
                
            
                if machine_name in EX:
                    if self.check_for_approval():
                        _logger.info("Plan or BeamSet approved for %s.  Unable to complete script.", machine_name)
                        set_progress("Waiting on user input...", percentage = -1)
                        message = (
                            f"The collision model requires a couch for the {machine_name}.\n"
                            "The plan or beamset is approved, so no couch can be imported.\n"
                            "Script will exit."
                        )
                        await_user_input(message=message)
                        raise RuntimeError(message)
                        
                    if self.check_for_dose() and self.display_output:
                        outcome = _prompt_user_acknowledge(
                            ValueError(str("Dose detected prior to couch placement")), 
                            message=(
                                "To continue, a couch must be inserted, and the dose will be invalidated.\n\n"
                                "Do you want to continue?"
                            )
                        )
                        _logger.debug("Outcome for prompt user: %s", outcome)
                        if outcome.user_choice == "cancel":
                            raise RuntimeError("User elected to cancel script.")    
                    
                    if not self.has_couch(COUCH_TB_TEMPLATE_ROIS):
                        _logger.info("Importing couch template...")
                        self.import_template(COUCH_TB_TEMPLATE_NAME, COUCH_TB_TEMPLATE_ROIS)
                        set_progress("Waiting on user to finalize couch position...", percentage = -1)
                        if self.display_output:
                            msg = (
                                "Finalize the couch placement for collision detection.\n\n"  
                                "Then, hit Play"
                            )
                            await_user_input(message=msg)
                        self.delete_couch = True
                
                set_progress("Running collision model...", percentage = -1)
                t0 = time.perf_counter()
                angles_by_iso = self.get_varian_iso_start_stop()
                dt = time.perf_counter() - t0
                _logger.debug("Time to complete get_varian_iso_start_stop():  %.3f sec", dt)
                
                if self.no_beams_exist(angles_by_iso):
                    return self.result
                
                for key, v in angles_by_iso.items():
                    
                    iso = v["iso_pos"]
            
                    # Rotate start/stop half-planes + head boxes
                    th_s = self.theta_from_gantry(v["start_gantry"])
                    th_t = self.theta_from_gantry(v["stop_gantry"])
                    
                    # Import collisioin model template
                    t0 = time.perf_counter()
                    self.import_template(VARIAN_COLL_TEMPLATE_NAME, COLL_VARIAN_TEMPLATE_ROIS)
                    dt = time.perf_counter() - t0
                    _logger.debug("Time to complete import_template():  %.1f sec", dt)
                    
                    # Transform model template
                    t0 = time.perf_counter()
                    self.transform_model_template(iso, th_s, th_t)
                    dt = time.perf_counter() - t0
                    _logger.debug("Time to complete transform_model_template():  %.1f sec", dt)
                    
                    # Create the collision model ROI
                    t0 = time.perf_counter()
                    coll_roi_list=[]
                    span = self.span_ccw(th_s, th_t)
                    if v["is_ap_pa"]:
                        self.varian_collision_model_appa()
                        coll_roi_list=[COLLISION_MODEL]
                    else:
                        self.varian_collision_model(span)
                        coll_roi_list=[COLLISION_MODEL, Hs, Ht]
                        
                    dt = time.perf_counter() - t0
                    _logger.debug("Time to complete varian collision model:  %.1f sec", dt)
                    
                    # Create the collision overlap ROI
                    self.create_collision_roi(coll_roi_list=coll_roi_list)
                    _logger.info("Overlap Collision ROI created...")
                    
                    # Detect collision
                    t0 = time.perf_counter()
                    self.detect_collision(iso)
                    dt = time.perf_counter() - t0
                    _logger.debug("Time to complete detect_collision():  %.1f sec", dt)
                    
                    # Delete ROIs
                    t0 = time.perf_counter()
                    self.delete_rois(ROI_SET_VARIAN)
                    dt = time.perf_counter() - t0
                    _logger.debug("Time to complete delete_rois():  %.1f sec", dt)
                    
                    _logger.info("Finished collision model for iso: %s", iso)
            
            else:
                self.result["passed"] = False
                msg = f"Machine not supported: {machine_name}"
                _logger.debug(msg)
                if self.display_output:
                    set_progress("Waiting on user hit play button...", percentage = -1)
                    await_user_input(message=msg)
                return self.result                        
            
            # Delete couch if flag is true
            if self.delete_couch:
                self.delete_rois(COUCH_TB_TEMPLATE_ROIS)
            
            msg = "\n".join(self.user_msg or [])
            message = (MSG_FAIL if msg else MSG_PASS) + (("\n\n" + msg) if msg else "")
            self.result["message"] = message
            _logger.info("Final Result: %s", self.result)
            
            dt_main = time.perf_counter() - t0_main
            _logger.info("Time to complete main collision model:  %.1f sec", dt_main)
            
            if self.display_output:
                set_progress("Finished...", percentage = -1)
                _prompt_user_acknowledge(
                    exc=RuntimeError("User acknowledge message."), 
                    message=message
                )
                # show_message(message=message)
            
            if self.user_msg:
                _alert_physicist_error(ValueError(message))
                set_progress("Sending physicist alert of possible collision...", percentage = -1)
                _logger.info("Physicist alerted about possible collision!")
                time.sleep(3)
            
            return self.result
    
        except Exception as e:
            _alert_physicist_error(e, message=__name__)
            _logger.error("[FAILED] in %s.  Email notification sent.  Exception: %s", __name__, str(e))
            set_progress("Waiting for user to hit play button...", percentage = -1)
            await_user_input(message="[FAILED] script.  Physicist alerted to address the issue.")
            set_progress("Sending physicist notification...", percentage = -1)
            time.sleep(3)
            _abort_script_error(exc=e, message=str(e))
    




