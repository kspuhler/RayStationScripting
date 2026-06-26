import difflib
import time
import tkinter as tk
from tkinter import messagebox

try:
    from connect import *
except:
    pass

UNMAPPED = "<UNMAPPED>"  # UI label; returned value will be ""


def get_roi_names_in_template(template):
    out = []
    for ii in template.FunctionToRoiMaps:
        name = ii.OrganData.ResponseFunctionTissueName
        if name not in out:
            out.append(name)
    return out


def _best_match(target, candidates):
    if not candidates:
        return None, 0.0

    t = (target or "").strip().lower()
    best = None
    best_score = -1.0
    for c in candidates:
        c_norm = (c or "").strip().lower()
        score = difflib.SequenceMatcher(None, t, c_norm).ratio()
        if score > best_score:
            best_score = score
            best = c
    return best, best_score


def prompt_template_roi_mapping(
    template_rois,
    available_rois,
    parent,
    title="Map Template ROIs",
    prompt="Map each template ROI to an existing ROI (or leave unmapped).",
    default_unmapped_below=0.60,      # if best-match score below this, default to unmapped for missing ROIs
    show_only_missing=True,           # if False: show all template ROIs in the UI
    enforce_unique=True,              # enforce uniqueness across non-unmapped selections
):
    """
    Returns:
        dict[str, str] mapping template ROI -> selected ROI name or "" (unmapped)
    """

    if not template_rois:
        return {}

    if not available_rois:
        raise ValueError("available_rois is empty; nothing to map to.")

    available_set = set(available_rois)

    # Decide which rows to show
    if show_only_missing:
        rows = [r for r in template_rois if r not in available_set]
    else:
        rows = list(template_rois)

    # If nothing missing and only missing requested, just return identity mapping
    if show_only_missing and not rows:
        return {r: r for r in template_rois}

    # Options list includes UNMAPPED first
    options = [UNMAPPED] + list(available_rois)

    # Pre-build defaults for EVERY template ROI (final dict keys)
    mapping_defaults = {}
    scores = {}

    for r in template_rois:
        if r in available_set:
            mapping_defaults[r] = r
            scores[r] = 1.0
        else:
            best, score = _best_match(r, available_rois)
            scores[r] = score
            if best is None or score < default_unmapped_below:
                mapping_defaults[r] = ""  # unmapped by default
            else:
                mapping_defaults[r] = best

    # Build UI
    root = parent  # you should pass your shared tk_root from launcher/pipeline

    result = {"mapping": None}
    win = tk.Toplevel(root)
    win.title(title)
    win.resizable(True, True)
    win.protocol("WM_DELETE_WINDOW", lambda: _cancel())

    tk.Label(win, text=prompt, justify="left").pack(anchor="w", padx=12, pady=(12, 6))

    container = tk.Frame(win)
    container.pack(fill="both", expand=True, padx=12, pady=6)

    canvas = tk.Canvas(container, borderwidth=0)
    scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
    scroll_frame = tk.Frame(canvas)

    scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    vars_by_template_roi = {}

    def _to_ui_value(v):
        return UNMAPPED if v == "" else v

    def _from_ui_value(v):
        return "" if v == UNMAPPED else v

    # Add one row per ROI we want user to decide
    for tmpl_roi in rows:
        row = tk.Frame(scroll_frame)
        row.pack(fill="x", pady=4)
    
        tk.Label(row, text=tmpl_roi, width=28, anchor="w").pack(side="left")
    
        default_ui = _to_ui_value(mapping_defaults[tmpl_roi])
    
        # Ensure the default is a valid OptionMenu value
        if default_ui not in options:
            default_ui = UNMAPPED
    
        v = tk.StringVar(master=win, value=default_ui)
        vars_by_template_roi[tmpl_roi] = v
    
        opt = tk.OptionMenu(row, v, *options)
        opt.configure(width=45)
        opt.pack(side="left", padx=(8, 0))
    
        tk.Label(row, text="{0:.2f}".format(scores[tmpl_roi]), width=6, anchor="e").pack(side="left", padx=(8, 0))

    btns = tk.Frame(win)
    btns.pack(fill="x", padx=12, pady=(6, 12))

    def _validate_unique(mapping):
        if not enforce_unique:
            return True, ""

        used = {}
        dups = []
        for tmpl, sel in mapping.items():
            if sel == "":
                continue
            if sel in used:
                dups.append((sel, used[sel], tmpl))
            else:
                used[sel] = tmpl

        if dups:
            lines = ["Duplicate mappings detected (must be unique):", ""]
            for sel, a, b in dups:
                lines.append(f'  "{sel}" selected for both "{a}" and "{b}"')
            lines.append("")
            lines.append('Fix duplicates or set one of them to "<UNMAPPED>".')
            return False, "\n".join(lines)

        return True, ""

    def _submit():
        # Start from defaults for ALL template ROIs
        final_map = dict(mapping_defaults)

        # Overwrite with user choices for rows shown
        for tmpl_roi, var in vars_by_template_roi.items():
            final_map[tmpl_roi] = _from_ui_value(var.get())

        ok, msg = _validate_unique(final_map)
        if not ok:
            messagebox.showerror("Invalid Mapping", msg)
            return

        result["mapping"] = final_map
        win.destroy()

    def _cancel():
        result["mapping"] = None
        win.destroy()

    tk.Button(btns, text="Submit", width=12, command=_submit).pack(side="right", padx=(6, 0))
    tk.Button(btns, text="Cancel", width=12, command=_cancel).pack(side="right")

    # Bring to front (RayStation-friendly)
    win.update_idletasks()
    win.deiconify()
    win.lift()
    win.focus_force()
    try:
        win.attributes("-topmost", True)
        win.after(250, lambda: win.attributes("-topmost", False))
    except Exception:
        pass

    # Block until closed (pump events)
    while win.winfo_exists():
        root.update_idletasks()
        root.update()
        time.sleep(0.01)

    return result["mapping"]


def user_prompt_for_missing_structures(template, structures=None, parent=None):
    """
    template: clinical goals template object (LoadTemplateClinicalGoals output)
    structures: list[str] of ROI names in current case (if None, tries to fetch from current Case)
    parent: optional tk root
    """
    template_rois = get_roi_names_in_template(template)
    print(template_rois)

    if structures is None:
        case = get_current("Case")
        # ROI names in case
        valid = ["ptv", "gtv", "ctv", "organ", "external"]
        structures = [roi.Name for roi in case.PatientModel.RegionsOfInterest if roi.Type.lower() in valid]
        print("Found", structures)

    # Find missing
    existing_set = set(structures)
    missing = [r for r in template_rois if r not in existing_set]
    print(missing)

    if not missing:
        return {}

    template_rois = get_roi_names_in_template(template)
    return prompt_template_roi_mapping(
        template_rois=template_rois,
        available_rois=structures,
        parent=parent,
        show_only_missing=True,   # only show missing in the UI
        enforce_unique=True,
)


if __name__ == "__main__":
    db = get_current("PatientDB")
    template = db.LoadTemplateClinicalGoals(templateName="TC Lung 200x30 PRF", lockMode="Read")
    root = tk.Tk()
    #root.withdraw()
    
    mapping = user_prompt_for_missing_structures(template, parent=root)
    print("Mapping returned:", mapping)

    try:
        root.destroy()
    except Exception:
        pass