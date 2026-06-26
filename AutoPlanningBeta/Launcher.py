# -*- coding: utf-8 -*-
"""
Created on Tue Jan 27 16:34:53 2026

@author: spuhlk01
"""

import sys
sys.path.append(r"\\Client\F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
sys.path.append(r"F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")

from connect import *

try:
    import Tkinter as tk
    import tkMessageBox as messagebox
except ImportError:
    import tkinter as tk
    from tkinter import messagebox
    
from AutoPlanningBeta.published import published
PIPELINES = published

def _import_module(module_path):
    return __import__(module_path, fromlist=["*"])  # IronPython-safe


class Launcher(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.title("AutoPlanning Launcher")
        self.resizable(False, False)

        self.listbox = tk.Listbox(self, width=55, height=10, exportselection=False)
        self.listbox.grid(row=0, column=0, padx=10, pady=10)

        for name, _, _ in PIPELINES:
            self.listbox.insert(tk.END, name)

        self.run_btn = tk.Button(self, text="Run", width=12, command=self.run_selected)
        self.run_btn.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="e")

        if self.listbox.size() > 0:
            self.listbox.selection_set(0)

    def run_selected(self):
        sel = self.listbox.curselection()
        if not sel:
            messagebox.showwarning("No selection", "Select a pipeline first.")
            return
    
        idx = int(sel[0])
        display_name, module_path, entrypoint = PIPELINES[idx]
    
        try:
            mod = _import_module(module_path)
            fn = getattr(mod, entrypoint)
        except Exception as e:
            messagebox.showerror("Load failed", "Could not load {0}\n\n{1}".format(display_name, str(e)))
            return
    
        context = {"pipeline_display_name": display_name}
    
        # Close/hide launcher BEFORE running pipeline
        self.withdraw()
        self.update_idletasks()
    
        try:
            fn()
        except Exception as e:
            messagebox.showerror("Pipeline error", "{0} failed:\n\n{1}".format(display_name, str(e)))
        finally:
            # Ensure launcher is gone even if pipeline errors
            try:
                self.destroy()
            except:
                pass



def main():
    Launcher().mainloop()


if __name__ == "__main__":
    main()
