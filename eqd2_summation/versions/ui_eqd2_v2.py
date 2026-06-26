r"""
RaystationScriptingPROD\EQD2_Summation\ui_eqd2.py

Created on Thu Oct  2 15:23:22 2025

User selection window for running EQD2 summation.  

@author: clanco01
"""
from __future__ import annotations

# === DEBUG SETTINGS ===
_DEBUG_THIS_MODULE = False

# === Raystation import ===
try:
    from connect import get_current
except Exception:
    pass

# === WORKING DIRECTORY ===
import sys
sys.path.append(r"\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
sys.path.append(r"F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")

# === Main library imports ===
from typing import Any, Dict, Optional
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QCheckBox,
    QLabel,
    QComboBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QListWidget,
    QListWidgetItem,
    QAbstractItemView,
    QHeaderView,
    QSpinBox,
    QDoubleSpinBox,
)
from PyQt5.QtGui import QPalette, QColor, QFont

# === Local imports ===
from RSutil.LogUtil.rs_logging import LOGGERS, set_logger_mode
from RSutil.ErrorsUtil.error_codes import PROMPT_USER, ABORT_SCRIPT
from RSutil.ErrorsUtil.rs_errors import report_error
from RSutil.patient_data_util import PatientDataUtil

# === Setup Logger ===
_logger = LOGGERS["eqd2_summation"]
if _DEBUG_THIS_MODULE:
    set_logger_mode(_logger, "debug")

# === GUI Size Policy ===
LEFT_GROUP_WIDTH = 320


class EQD2SelectionWindow(QWidget):
    
    def __init__(self):
        _logger.info("Initializing EQD2SelectionWindow...")
        super().__init__()
        
        self.setWindowTitle("EQD2 Dose Summation")
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        
        self.pdu = PatientDataUtil()
        self.external_default_roi_name = "External"
        self.external_roi_name = self.external_default_roi_name
        self.plan_data = self._build_flat_plan_data()
        
        self.priority_external = 48
        self.alpha_beta_default = 3.0 # Gy
        
        self.external_threshold_level = -250
        
        _logger.debug("Building UI....")
        self._apply_dark_theme()
        self._build_ui()
        
        _logger.debug("Loading data into UI....")
        self._load_into_form({})
        
        _logger.debug("EQD2SelectionWindow initialization complete!")
    
    # ===== Data helpers =====
    def _build_flat_plan_data(self) -> dict[str, dict]:
        """
        Flatten PDU plan data:
            {plan: {beamset: info}} -> {dose_id: info_with_plan_and_beamset}
        """
        nested = self.pdu.get_all_plan_data()
        _logger.debug("Plan Data from PDU: %s", nested)
        flat: dict[str, dict] = {}
    
        for plan_name, beamsets in nested.items():
            for beamset_name, info in (beamsets or {}).items():
                dose_id = f"{plan_name}_{beamset_name}"  # unique key
                flat[dose_id] = dict(info)
        
        _logger.debug("Flattened Plan Data: %s", flat)
                
        return flat

    def _create_external(self, ct_exam_name):
        try:
            ct_exam = next(
                (exam for exam in self.pdu.get_ct_exams() if exam.Name == ct_exam_name),
                None,
            )
            
            # Create external ROI
            external_name = None
            if not self.pdu.has_roi_external():
                _logger.debug("Creating an external ROI and contour on CT: %s", ct_exam_name)
                # Get unique name
                external_name = self.external_default_roi_name
                base_name = external_name
                suffix = 1
                while external_name in self.pdu.get_roi_names():
                    external_name = f"{base_name}_{suffix}"
                    suffix += 1
                
                external_roi = self.pdu.case.PatientModel.CreateRoi(
                    Name=external_name, 
                    Color="Green", 
                    Type="External", 
                    TissueName="", 
                    RbeCellTypeName=None, 
                    RoiMaterial=None,
                )
                external_roi.CreateExternalGeometry(
                    Examination=ct_exam, 
                    ThresholdLevel=self.external_threshold_level
                )
            elif not self.pdu.has_roi_external_contour_on_ct(ct_exam_name):
                _logger.debug("Creating an external geometry on CT: %s", ct_exam_name)
                external_name = self.pdu.get_roi_external_name()
                self.pdu.case.PatientModel.RegionsOfInterest[external_name].CreateExternalGeometry(
                    Examination=ct_exam, 
                    ThresholdLevel=self.external_threshold_level
                )
            else:
                _logger.debug("External geometry already exists on CT: %s", ct_exam_name)
                external_name = self.pdu.get_roi_external_name()
            
            self.external_roi_name = external_name
            
        except Exception as e:
            _logger.error("Failed to create external: %s", e)
    
    # === Error handling methods ===
    def _prompt_user_retry(
            self, 
            exc: Exception, 
            metadata: Optional[dict] = None, 
            message: Optional[str] = None
    ):                                                  
        outcome = report_error(
                error_def=PROMPT_USER.UIUX_SELECT_INVALID, 
                original_exception=exc, 
                context={"module": "ui_eqd2.py"},
                metadata={},
                message=message,
            )
        return outcome
    
    def _prompt_user_acknowledge(
            self, 
            exc: Exception, 
            metadata: Optional[dict] = None, 
            message: Optional[str] = None
    ):                                                  
        outcome = report_error(
                error_def=PROMPT_USER.UIUX_USER_ACKNOWLEDGE, 
                original_exception=exc, 
                context={"module": "ui_eqd2.py"},
                metadata={},
                message=message,
            )
        return outcome
        
    def _abort_script_error(
            self, 
            exc: Exception, 
            metadata: Optional[dict] = None, 
            message: Optional[str] = None
    ):                                                  
        report_error(
                error_def=ABORT_SCRIPT.DATA_REQUIRED_MISSING, 
                original_exception=exc, 
                context={"module": "ui_eqd2.py"},
                metadata={},
                message=message,
            )
        self.close()
        raise RuntimeError("Script aborted...")
            
                                                        
    # ===== Build UI =====
    def _apply_dark_theme(self):
        
        app = QApplication.instance()
        if app is not None:
            app.setStyle("Fusion")
        dark = QPalette()
        dark.setColor(QPalette.Window, QColor(53, 53, 53))
        dark.setColor(QPalette.WindowText, Qt.white)
        dark.setColor(QPalette.Base, QColor(35, 35, 35))
        dark.setColor(QPalette.AlternateBase, QColor(45, 45, 45))
        dark.setColor(QPalette.ToolTipBase, Qt.white)
        dark.setColor(QPalette.ToolTipText, Qt.white)
        dark.setColor(QPalette.Text, Qt.white)
        dark.setColor(QPalette.Button, QColor(53, 53, 53))
        dark.setColor(QPalette.ButtonText, Qt.white)
        dark.setColor(QPalette.BrightText, Qt.red)
        dark.setColor(QPalette.Highlight, QColor(90, 120, 200))
        dark.setColor(QPalette.HighlightedText, Qt.black)
        if app is not None:
            app.setPalette(dark)
        else:
            self.setPalette(dark)

        self.setStyleSheet(
            """
            QWidget { font-size: 11pt; }
            QGroupBox::title { font-size: 11pt; }
            QHeaderView::section { font-size: 10pt; }
            QPushButton { font-size: 10pt; }
            QWidget { color: #E0E0E0; background-color: #353535; }
            QGroupBox { border: 1px solid #555; border-radius: 6px; margin-top: 10px; }
            QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top left; padding: 0 6px; color: #E0E0E0; }
            QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox { background-color: #2b2b2b; border: 1px solid #666; border-radius: 4px; padding: 2px 6px; }
            QComboBox QAbstractItemView { background-color: #2b2b2b; selection-background-color: #3d3d3d; color: #E0E0E0; }
            QCheckBox { spacing: 8px; color: #FFFFFF; }
            QPushButton { background-color: #444; border: 1px solid #666; padding: 6px 10px; border-radius: 6px; }
            QPushButton:hover { background-color: #555; }
            QPushButton:pressed { background-color: #3d3d3d; }
            QHeaderView::section { background-color: #3d3d3d; color: #E0E0E0; border: 1px solid #555; padding: 4px; }
            QTableWidget { gridline-color: #555; background-color: #2b2b2b; alternate-background-color: #242424; }
            QScrollBar:vertical, QScrollBar:horizontal { background: #2b2b2b; }
            QScrollBar:vertical, QScrollBar:horizontal { background: #2b2b2b; }
            QTableWidget::item:selected {
                background-color: #1a73e8;  /* bold solid highlight */
                color: #ffffff;
                border: 2px solid #7aa2ff;  /* optional extra punch */
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
            }
            """
        )
                                                        
    def _build_ui(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(8, 8, 8, 8)
        outer.setSpacing(8)
        
        # === Top row: left (CT) | right (ROI table) ===
        top = QHBoxLayout()
        top.setContentsMargins(0, 0, 0, 0)
        top.setSpacing(8)
    
        LEFT_PANEL_WIDTH = 420  # ensures alignment between CT and Available Doses
    
        # --- LEFT: CT selection ---
        gb_ct = QGroupBox("Reference CT (final dose will reside here)")
        gb_ct.setToolTip(
            "This CT defines where the final dose will reside.\n"
            "It is the reference CT used for all deformable registrations and dose mappings."
        )
        gb_ct.setFont(QFont("Segoe UI", 12, QFont.Bold))
        gb_ct.setFixedWidth(LEFT_PANEL_WIDTH)
        gb_ct.setMinimumHeight(260)  # Match bottom group visually
        hl_ct = QHBoxLayout()
        hl_ct.setContentsMargins(8, 8, 8, 8)
        hl_ct.setSpacing(6)
        hl_ct.addWidget(QLabel("CT:"))
        self.cb_ct = QComboBox()
        self.cb_ct.setMinimumWidth(240)
        self.cb_ct.setToolTip(
            "Select the CT examination that will serve as the reference frame for dose calculations.\n"
            "All selected doses will be mapped or deformed into this CT’s coordinate system.\n"
            "In RayStation, this corresponds to the CT associated with the final evaluation dose, not individual plan names."
        )
        hl_ct.addWidget(self.cb_ct, 1)
        gb_ct.setLayout(hl_ct)
        
        # --- RIGHT: ROI table (ROI, Priority, Alpha/Beta) ---
        gb_roi = QGroupBox("Targets / Priorities / α/β")
        vl_roi = QVBoxLayout()
        vl_roi.setContentsMargins(8, 8, 8, 8)
        vl_roi.setSpacing(6)
        self.tbl_roi = QTableWidget(0, 3)
        self.tbl_roi.setHorizontalHeaderLabels(["ROI", "Priority", "α/β (Gy)"])
        self.tbl_roi.horizontalHeader().setSectionResizeMode(0, QHeaderView.Interactive)
        self.tbl_roi.setColumnWidth(0, 180)
        self.tbl_roi.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.tbl_roi.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.tbl_roi.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.tbl_roi.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tbl_roi.horizontalHeaderItem(0).setToolTip("ROI type External can not be deleted.")
        vl_btns_roi = QHBoxLayout()
        self.btn_add_roi = QPushButton("Add ROI")
        self.btn_del_roi = QPushButton("Delete Selected")
        vl_btns_roi.addWidget(self.btn_add_roi)
        vl_btns_roi.addWidget(self.btn_del_roi)
        vl_btns_roi.addStretch(1)
        vl_roi.addWidget(self.tbl_roi)
        vl_roi.addLayout(vl_btns_roi)
        gb_roi.setLayout(vl_roi)
    
        # Assemble top row
        top.addWidget(gb_ct, 0)
        top.addWidget(gb_roi, 1)
        outer.addLayout(top, 1)
    
        # === Bottom: Dose selection (spans full width) ===
        gb_dose = QGroupBox()
        gb_dose.setMinimumHeight(260)
        hl_dose = QHBoxLayout()
        hl_dose.setContentsMargins(8, 8, 8, 8)
        hl_dose.setSpacing(8)
        
        # Left: available dose evals
        left_v = QVBoxLayout()
        left_v.setContentsMargins(8, 8, 8, 8)
        left_v.setSpacing(6)
        left_v.addWidget(QLabel("Available Doses - PlanName_BeamSetName"))
        self.list_fraction_doses = QListWidget()
        self.list_fraction_doses.setSelectionMode(QAbstractItemView.ExtendedSelection)
        left_v.addWidget(self.list_fraction_doses, 1)
        
        left_panel = QWidget()
        left_panel.setLayout(left_v)
        left_panel.setFixedWidth(LEFT_PANEL_WIDTH)
        
        # MIDDLE: action buttons (stacked vertically)
        mid_v = QVBoxLayout()
        mid_v.setContentsMargins(0, 24, 0, 24)
        mid_v.setSpacing(12)
        self.btn_add_dose = QPushButton("Add →")
        self.btn_add_dose.setFixedWidth(120)
        self.btn_del_dose = QPushButton("← Remove")
        self.btn_del_dose.setFixedWidth(120)
        mid_v.addStretch(1)
        mid_v.addWidget(self.btn_add_dose, alignment=Qt.AlignHCenter)
        mid_v.addWidget(self.btn_del_dose, alignment=Qt.AlignHCenter)
        mid_v.addStretch(1)
        
        # Right: selected doses table
        right_v = QVBoxLayout()
        right_v.setContentsMargins(8, 8, 8, 8)
        right_v.setSpacing(6)
        right_v.addWidget(QLabel("Selected Doses"))
        self.tbl_sel_fraction_doses = QTableWidget(0, 2)
        self.tbl_sel_fraction_doses.setHorizontalHeaderLabels(["Dose", "Fractions"])
        self.tbl_sel_fraction_doses.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tbl_sel_fraction_doses.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.tbl_sel_fraction_doses.horizontalHeaderItem(1).setToolTip(
            "Number of fractions used for dose sum weighting.\n"
            "Defaults to the number of fractions in the plan but can be adjusted manually."
        )
        self.tbl_sel_fraction_doses.setSelectionBehavior(QAbstractItemView.SelectRows)
        right_v.addWidget(self.tbl_sel_fraction_doses, 1)
        
        # Assemble columns
        hl_dose.addWidget(left_panel, 0)
        hl_dose.addLayout(mid_v, 0)
        hl_dose.addLayout(right_v, 1)
        gb_dose.setLayout(hl_dose)
        outer.addWidget(gb_dose, 2)
    
        # === Bottom action row ===
        actions = QHBoxLayout()
        self.chk_create_sum = QCheckBox("Create Sum Plan for Evaluation?")
        self.chk_create_sum.setChecked(True)
        self.chk_create_sum.setToolTip(
            "This creates a dummy plan for populating clinical goals.\n"
            "Drop the final evaluation dose into the Compare 1 window and add clinical goals."
        )
        actions.addWidget(self.chk_create_sum)  
        actions.addStretch(1)
        self.btn_cancel = QPushButton("Cancel")
        self.btn_eqd2 = QPushButton("EQD2")
        self.btn_eqd2.setToolTip(
            "If a selected dose has a different CT, perform deformable registration to the Reference CT, \n"
            "then compute EQD2 and deform the resulting dose to the Reference CT."
        )  
        self.btn_dose_sum = QPushButton("Dose Sum")
        self.btn_dose_sum.setToolTip(
            "If a selected dose has a different CT, perform deformable registration to the Reference CT, \n"
            "then deform the dose and sum all selected doses on the Reference CT."
        )
        self.btn_eqd2_dose_sum = QPushButton("EQD2 + Dose Sum")
        self.btn_eqd2_dose_sum.setToolTip(
            "If a selected dose has a different CT, perform deformable registration to the Reference CT, \n"
            "then compute EQD2, deform the resulting doses, and sum all on the Reference CT."
        )
        actions.addWidget(self.btn_cancel)
        actions.addWidget(self.btn_eqd2)
        actions.addWidget(self.btn_dose_sum)
        actions.addWidget(self.btn_eqd2_dose_sum)
        outer.addLayout(actions)
    
        # --- Wire signals ---
        self.cb_ct.currentTextChanged.connect(self._on_ct_changed)
        self.btn_add_roi.clicked.connect(self._on_add_roi)
        self.btn_del_roi.clicked.connect(self._on_del_roi)
        self.btn_add_dose.clicked.connect(self._on_add_fraction_dose)
        self.btn_del_dose.clicked.connect(self._on_del_fraction_dose)
        self.btn_eqd2.clicked.connect(lambda: self._on_submit("eqd2"))
        self.btn_dose_sum.clicked.connect(lambda: self._on_submit("dose_sum"))
        self.btn_eqd2_dose_sum.clicked.connect(lambda: self._on_submit("eqd2_dose_sum"))
        self.btn_cancel.clicked.connect(self._on_cancel_clicked)
    
        # --- Double-click to add/remove doses ---
        self.list_fraction_doses.itemDoubleClicked.connect(self._on_available_dose_double_clicked)
        self.tbl_sel_fraction_doses.doubleClicked.connect(self._on_selected_dose_double_clicked)

    # ===== Populate UI =====
    def _load_into_form(self, s: Dict[str, Any]):
        """Populate widgets from current RayStation context and optional state dict.

        Expected *s* keys (all optional):
            ct_exam_name: str
            rois: list[tuple[str, int, float]]  # (roi_name, priority, alpha_beta)
            fraction_doses: list[tuple[str, float, int]] # (dose_name, dose_per_fx, n_fx)
        """
        # CTs
        _logger.debug("Inside _load_into_form()...")
        _logger.debug("Adding CT exam names to drop down list...")
        self.cb_ct.blockSignals(True)
        self.cb_ct.clear()
        for ct_exam_name in sorted(self.pdu.get_ct_exam_names()):
            self.cb_ct.addItem(ct_exam_name)
        # default
        _logger.debug("Setting default CT in dropdown list...")
        default_ct =  s.get("ct_name") or self.pdu.get_ct_exam_name_newest()
        if default_ct and (self.cb_ct.findText(default_ct) >= 0):
            self.cb_ct.setCurrentText(default_ct)
        _logger.debug("Creating external if needed...")
        self._create_external(self.cb_ct.currentText())
        self.cb_ct.blockSignals(False)

        # Structures and fraction doses depend on CT selection
        _logger.debug("Refershing structures and fraction doses in UI...")
        self._refresh_structures()
        self._refresh_fraction_doses()

        # ROI table
        _logger.debug("Populating ROI table...")
        self.tbl_roi.setRowCount(0)
        for roi_name, priority, ab in s.get("rois", []):
            self._append_roi_row(roi_name, priority, ab)
        # Default ROI if none provided: "External" with priority 48
        _logger.debug("Setting ROI table to include External...")
        if self.tbl_roi.rowCount() == 0:
            self._append_roi_row(
                self.external_roi_name, 
                priority=self.priority_external,
                alpha_beta=self.alpha_beta_default
            )

        # Selected fraction fraction_doses
        _logger.debug("Populating fraction doses table...")
        self.tbl_sel_fraction_doses.setRowCount(0)
        for dose_name, dpf, nfx in s.get("fraction_doses", []):
            self._append_selected_dose_row(dose_name, dpf, nfx)

    # ===== Helpers to (re)fill dependent widgets =====
    def _refresh_structures(self):
        ct = self.cb_ct.currentText()
        self._available_rois = self.pdu.get_roi_names_with_contours_on_ct(ct) if ct else []
        _logger.debug("Availabe ROIS: %s", self._available_rois)
        # Update existing ROI dropdowns to reflect current CT's structures
        for r in range(self.tbl_roi.rowCount()):
            w = self.tbl_roi.cellWidget(r, 0)
            if isinstance(w, QComboBox):
                current = w.currentText()
                w.blockSignals(True)
                w.clear()
                w.addItems(self._available_rois)
                if current in self._available_rois:
                    w.setCurrentText(current)
                elif self._available_rois:
                    w.setCurrentIndex(0)
                w.blockSignals(False)

    def _refresh_fraction_doses(self):
        self.list_fraction_doses.clear()
        self._dose_item_by_name = {}
    
        # Fill available list
        for name in sorted(self.plan_data.keys()):
            it = QListWidgetItem(name)
            self.list_fraction_doses.addItem(it)
            self._dose_item_by_name[name] = it
    
        # Disable already-selected doses in the list
        for name in self._selected_dose_names():
            it = self._dose_item_by_name.get(name)
            if it:
                it.setFlags(it.flags() & ~Qt.ItemIsEnabled)
    
        self._available_fraction_dose_names = set(self.plan_data.keys())

    # ===== ROI dropdown helper =====
    def _create_roi_combobox(self, selected: str | None) -> QComboBox:
        _logger.debug("Inside _create_roi_combobox() with selected as: %s", selected)
        cb = QComboBox()
        cb.addItems(self._available_rois if hasattr(self, "_available_rois") else [])
        if selected and (cb.findText(selected) >= 0):
            cb.setCurrentText(selected)
        elif cb.count() > 0 and (not selected):
            cb.setCurrentIndex(0)
        cb.setMinimumWidth(140)
        # When any ROI changes, re-filter all comboboxes to keep uniqueness
        cb.currentTextChanged.connect(self._on_roi_changed)
        return cb
    
    # ===== ROI priority helpers =====
    def _current_priorities(self):
        vals = []
        for r in range(self.tbl_roi.rowCount()):
            sp: QSpinBox = self.tbl_roi.cellWidget(r, 1)  # type: ignore
            if isinstance(sp, QSpinBox):
                vals.append(sp.value())
        return vals

    def _next_priority(self) -> int:
        """Return the smallest positive integer not already used (1,2,3,...)"""
        used = set(self._current_priorities())
        k = 1
        while k in used:
            k += 1
        return k

    # --- ROI helpers ---
    def _selected_roi_names(self) -> set[str]:
        names = set()
        for r in range(self.tbl_roi.rowCount()):
            w = self.tbl_roi.cellWidget(r, 0)
            if isinstance(w, QComboBox):
                names.add(w.currentText())
        return names
    
    def _refresh_roi_combobox_models(self):
        """Refilter each ROI combobox so that each ROI is selectable at most once."""
        selected = self._selected_roi_names()
        for r in range(self.tbl_roi.rowCount()):
            cb = self.tbl_roi.cellWidget(r, 0)
            if not isinstance(cb, QComboBox):
                continue
            cur = cb.currentText()
            cb.blockSignals(True)
            cb.clear()
            # Include all available ROIs except already-selected ones, BUT keep its own current value
            options = [roi for roi in getattr(self, "_available_rois", [])
                       if (roi == cur) or (roi not in selected)]
            cb.addItems(options)
            cb.setCurrentText(cur)  # safe even if cur is the only remaining
            cb.blockSignals(False)
            
    def _on_roi_changed(self, _txt: str):
        self._refresh_roi_combobox_models()

    
    # --- Dose helpers ---
    def _selected_dose_names(self) -> set[str]:
        names = set()
        for r in range(self.tbl_sel_fraction_doses.rowCount()):
            item = self.tbl_sel_fraction_doses.item(r, 0)
            if item:
                names.add(item.text())
        return names


    # ===== ROI table operations =====
    def _append_roi_row(self, roi_name: str, priority: int = 1, alpha_beta: float = 3.0):
        _logger.debug("Inside _append_roi_row()...")
        r = self.tbl_roi.rowCount()
        self.tbl_roi.insertRow(r)
        # ROI name as dropdown of all available ROIs
        cb = self._create_roi_combobox(roi_name)
        
        # Lock external
        _logger.debug("Locking external inside _append_roi_row()...")
        if roi_name == self.external_roi_name and r == 0:
            cb.setEnabled(False)  # make External uneditable
            cb.setStyleSheet("color: #AAAAAA; background-color: #444444;")  # visual cue it's fixed

        
        self.tbl_roi.setCellWidget(r, 0, cb)
        # Priority (spin box editor)
        sp = QSpinBox()
        sp.setRange(1, 100)
        sp.setValue(priority)
        sp.setAlignment(Qt.AlignCenter)
        self.tbl_roi.setCellWidget(r, 1, sp)
        # Alpha/Beta (double spin)
        dsp = QDoubleSpinBox()
        dsp.setDecimals(2)
        dsp.setRange(0.1, 99.9)
        dsp.setSingleStep(0.1)
        dsp.setValue(alpha_beta)
        dsp.setAlignment(Qt.AlignCenter)
        self.tbl_roi.setCellWidget(r, 2, dsp)

    def _on_add_roi(self):
        try:
            ct = self.cb_ct.currentText()
            rois = self.pdu.get_roi_names_with_contours_on_ct(ct) if ct else []
            _logger.debug("ROIs availalbe when adding an ROI: %s", rois)
            if not rois:
                return
            selected = self._selected_roi_names()
            candidates = [r for r in rois if r not in selected]
            if not candidates:
                return  # nothing left to add
            to_add = candidates[0]
            self._append_roi_row(to_add, priority=self._next_priority(), alpha_beta=3.0)
            self._refresh_roi_combobox_models()
        except Exception as e:
            _logger.exception("Failed to add ROI row: %s", e)

    def _on_del_roi(self):
        rows = sorted({idx.row() for idx in self.tbl_roi.selectedIndexes()}, reverse=True)
        blocked = False
        for r in rows:
            name = ""
            w0 = self.tbl_roi.cellWidget(r, 0)
            if isinstance(w0, QComboBox):
                name = w0.currentText()
            else:
                it = self.tbl_roi.item(r, 0)
                if it:
                    name = it.text()
            # Do NOT delete the external ROI row
            if name == self.external_roi_name:
                blocked = True
                continue
            self.tbl_roi.removeRow(r)
    
        if blocked:
            _logger.info("External ROI row is protected and was not deleted.")
        self._refresh_roi_combobox_models()

    # ===== Dose selection operations =====
    def _append_selected_dose_row(self, dose_name: str):
        # silently ignore duplicates / invalids
        if (dose_name not in getattr(self, "_available_fraction_dose_names", {dose_name})) \
           or (dose_name in self._selected_dose_names()):
            return
    
        r = self.tbl_sel_fraction_doses.rowCount()
        self.tbl_sel_fraction_doses.insertRow(r)
    
        # Column 0: Dose name
        name_item = QTableWidgetItem(dose_name)
        name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
        name_item.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        self.tbl_sel_fraction_doses.setItem(r, 0, name_item)
    
        # Column 1: Fractions (default 25)
        nfx = QSpinBox()
        nfx.setRange(1, 100)
        nfx.setValue(self.plan_data.get(dose_name, {}).get("fractions", 25))
        nfx.setAlignment(Qt.AlignCenter)
        self.tbl_sel_fraction_doses.setCellWidget(r, 1, nfx)
    
        # Disable this dose in the available list
        it = getattr(self, "_dose_item_by_name", {}).get(dose_name)
        if it:
            it.setFlags(it.flags() & ~Qt.ItemIsEnabled)


    def _on_add_fraction_dose(self):
        for it in self.list_fraction_doses.selectedItems():
            self._append_selected_dose_row(it.text())

    def _on_del_fraction_dose(self):
        rows = sorted({idx.row() for idx in self.tbl_sel_fraction_doses.selectedIndexes()}, reverse=True)
        for r in rows:
            item = self.tbl_sel_fraction_doses.item(r, 0)
            name = item.text() if item else None
            self.tbl_sel_fraction_doses.removeRow(r)
            # Re-enable in available list
            if name and hasattr(self, "_dose_item_by_name"):
                it = self._dose_item_by_name.get(name)
                if it:
                    it.setFlags(it.flags() | Qt.ItemIsEnabled)
            
    def _on_available_dose_double_clicked(self, item: QListWidgetItem):
        if item:
            self._append_selected_dose_row(item.text())

    def _on_selected_dose_double_clicked(self, index):
        if not index.isValid():
            return
        # Delegate to delete so we also re-enable the list item
        self.tbl_sel_fraction_doses.selectRow(index.row())
        self._on_del_fraction_dose()

    # ===== Dependency updates =====
    def _on_ct_changed(self, _txt: str):
        # Ensure external exists first
        self._create_external(self.cb_ct.currentText())
        
        # Refresh structures
        self._refresh_structures()
        
        # Rebuild the ROI table so it reflects the new CT's structure set
        try:
            self.tbl_roi.setRowCount(0)
            self._append_roi_row(
                self.external_roi_name, 
                priority=self.priority_external, 
                alpha_beta=self.alpha_beta_default)
        except Exception as e:
            _logger.exception("Failed to rebuild ROI rows on CT change: %s", e)
        
        self._refresh_roi_combobox_models()
        self._refresh_fraction_doses()
        

    # ===== Results collection & actions =====
    def _get_user_selections(self) -> dict[dict[str, Any]]:
        """
        Collect and return all user selections from the UI in a structured dictionary.
    
        Returns
        -------
        dict
            {
                "ct_exam_name": str,
                "rois": {roi_name: {"priority": int, "alpha_beta": float}},
                "plan_data": { 
                    "dose": dose_object, 
                    "fractions": fractions_from_GUI,
                    "fractions_rs": fractino_from_RayStation,
                    "plan_name": plan_name,
                    "beamset_name": beamset_name,
                    "beamset": beamset_object,
                    "ct_exam_name": ct_exam_name,
                    "ct_exam": ct_exam_object
                    }
                "create_sum_plan": bool,
                "external_info": external_info,
            }
        """
        _logger.info("Getting user's selected values...")
        errors = []
        
        # --- CT ---
        ct_exam_name = self.cb_ct.currentText()
        if not ct_exam_name:
            errors.append("Select a CT.")
    
        # --- ROIs ---
        rois = {}
        try:
            roi_names = []
            alpha_betas = []
            priorities = []
            for r in range(self.tbl_roi.rowCount()):
                roi_cb = self.tbl_roi.cellWidget(r, 0)
                pr_sb  = self.tbl_roi.cellWidget(r, 1)
                ab_sb  = self.tbl_roi.cellWidget(r, 2)
                
                roi_name   = roi_cb.currentText() or None
                priority   = int(pr_sb.value()) or None
                alpha_beta = float(ab_sb.value()) or None
                
                if roi_name == None or priority == None or alpha_beta == None:
                    raise
                roi_names.append(roi_name)
                priorities.append(priority)
                alpha_betas.append(alpha_beta)
                
                rois = {"roi_names": roi_names, "priorities": priorities, "alpha_betas": alpha_betas}
            
            if not rois:
                raise
        except Exception:
            errors.append("Enter all the Priorities and α/β values.")
        
        if len(rois["priorities"]) != len(set(rois["priorities"])):
            errors.append("Each ROI priority must be unique. Please assign distinct priority numbers.")
        
        external_info = {}
        if self.external_roi_name in rois["roi_names"]:
            # Get the index of the external ROI in the list
            idx_ext = rois["roi_names"].index(self.external_roi_name)
            ext_priority = rois["priorities"][idx_ext]
        
            # Get all non-external priorities
            other_priorities = [
                p for i, p in enumerate(rois["priorities"]) if i != idx_ext
            ]
        
            # External must be numerically largest (lowest importance)
            if any(p > ext_priority for p in other_priorities):
                errors.append(
                    f"'{self.external_roi_name}' must have the lowest priority (i.e., the largest priority number)."
                )
                
            # Track external ROI information for EQD2 calculation
            external_info = {
                "name": self.external_roi_name,
                "priority": ext_priority,
                "alpha_beta": rois["alpha_betas"][idx_ext],
            }
        else:
            message = "No external in list of ROIs.  External must be included."
            errors.append(message)
            _logger.warning(message)
        
        # --- Plan Data ---
        plan_data = {}
        try:
            if self.tbl_sel_fraction_doses.rowCount() < 1:
                raise
            try: 
                for row in range(self.tbl_sel_fraction_doses.rowCount()):
                    name_item  = self.tbl_sel_fraction_doses.item(row, 0)
                    dose_name = name_item.text()
                    dose_obj = self.plan_data[dose_name]["dose_object"]
                    
                    nfx_widget = self.tbl_sel_fraction_doses.cellWidget(row, 1)
                    nfx = int(nfx_widget.value())
                    
                    
                    plan_data[dose_name] = { 
                        "dose": dose_obj, 
                        "fractions": nfx,
                        "fractions_rs": self.plan_data[dose_name]["fractions"],
                        "plan_name": self.plan_data[dose_name]["plan_name"],
                        "beamset_name": self.plan_data[dose_name]["beamset_name"],
                        "beamset": self.plan_data[dose_name]["beamset"],
                        "ct_exam_name": self.plan_data[dose_name]["ct_exam_name"],
                        "ct_exam": self.plan_data[dose_name]["ct_object"]
                        }
            except Exception as e:
                _logger.error("Failed to get data from UI: %s", e)
                self._prompt_user_acknowledge(exc=e, message="Execution failure.  Script will abort.")
                self._abort_script_error(exc=e)
                
        except Exception:
            errors.append("Select an available dose.") 
            
        selected_values = {
            "ct_exam_name": ct_exam_name,
            "rois": rois,
            "plan_data": plan_data,
            "create_sum_plan": self.chk_create_sum.isChecked(),
            "external_info": external_info,
        }
        
        return selected_values, errors

    def _on_submit(self, mode: str):
        """
        Shared handler for EQD2, Dose Sum, and EQD2 + Dose Sum buttons.
    
        Parameters
        ----------
        mode : str
            One of {'eqd2', 'dose_sum', 'eqd2_dose_sum'} indicating the user’s choice.
        """
        try:
            self.selected_values, errors = self._get_user_selections()
            if errors:
                e = ValueError("Fix user selection errors.")
                message = "\n\n".join(errors)
                self._prompt_user_retry(exc=e, message=message)
                _logger.warning("%s: %s", e, message)
                self.selected_values = None
                return
            
            self.selected_values["operation_mode"] = mode
            
            changes = []
            for dose_name, plan_data in self.selected_values["plan_data"].items():
                user_n = plan_data["fractions"]
                plan_n = plan_data["fractions_rs"]
                if user_n != plan_n:
                    changes.append(f"• {dose_name}: {plan_n} → {user_n}")
            
            if changes:
                msg = (
                    "The script does not change the plan's fractions or scale the plan's dose! \n\nFractions differ from the plan(s) for:\n\n" +
                    "\n".join(changes) +
                    "\n\nThe dose summation will utilize the user input fractionation for the dose sum. Continue?"
                )
                e = ValueError("User asked to continue.")
                outcome = self._prompt_user_acknowledge(exc=e, message=msg)
                if outcome.user_choice == "cancel":
                    _logger.info("User returned to GUI to update fraction changes.")
                    self.selected_values = None
                    return
                
            self.close()
            
        except Exception as e:
            self.selected_values = None
            message = "Error occuring during getting user selections.  Script will exit."
            self._prompt_user_acknowledge(exc=e, message=message)
            _logger.warning("%s: %s", e, message)
            self._abort_script_error(exc=e, message=message)

    def _on_cancel_clicked(self):
        self.selected_values = None
        _logger.info("User cancelled...")
        self.close()

    

    # ===== Main method =====
    @staticmethod
    def main():
        app = QApplication(sys.argv)
        w = EQD2SelectionWindow()
        w.resize(1000, 600)
        w.show()
        app.exec_()
        if _DEBUG_THIS_MODULE:
            set_logger_mode(_logger)
        return getattr(w, "selected_values", None)


# === RUN LOCALLY FOR DEBUGGING ===
if __name__ == "__main__" and _DEBUG_THIS_MODULE:
    debug_logger = LOGGERS["debug"]
    debug_logger.info("Running ui_eqd2.py...")
    
    EQD2SelectionWindow().main()
    
    debug_logger.info("Closed ui_eqd2.py...")
