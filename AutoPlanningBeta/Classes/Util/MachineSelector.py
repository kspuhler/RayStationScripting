# -*- coding: utf-8 -*-
import tkinter as tk
import traceback


class MachineSelector:
    def __init__(self, machine_list=None, parent=None, title="Select Machine", prompt="Select a machine:"):
        if machine_list is None:
            machine_list = ["TrueBeam", "Radixact"]
        if not isinstance(machine_list, (list, tuple)) or len(machine_list) == 0:
            raise ValueError("machine_list must be a non-empty list/tuple")

        self.machine_list = list(machine_list)

        self.own_root = False
        if parent is None:
            self.root = tk.Tk()
            self.root.withdraw()
            self.own_root = True
        else:
            self.root = parent

        self.choice = None

        self.window = tk.Toplevel(self.root)
        self.window.title(title)
        self.window.resizable(False, False)
        self.window.protocol("WM_DELETE_WINDOW", self._on_close)

        tk.Label(self.window, text=prompt).pack(pady=(10, 6), padx=12)

        # Dropdown variable
        default_value = self.machine_list[0]
        self.selection = tk.StringVar(master=self.window, value=default_value)

        # Dropdown (OptionMenu)
        dropdown = tk.OptionMenu(self.window, self.selection, *self.machine_list)
        dropdown.configure(width=max(20, min(50, max(len(str(x)) for x in self.machine_list) + 2)))
        dropdown.pack(padx=12, pady=(0, 10), anchor="w")

        btn_frame = tk.Frame(self.window)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Submit", width=10, command=self._submit).pack(side="left", padx=6)
        tk.Button(btn_frame, text="Cancel", width=10, command=self._on_close).pack(side="left", padx=6)

        # Bring to front
        self._raise_window()

        try:
            self.window.grab_set()
            self.window.transient(self.root)
        except tk.TclError:
            pass

    def _raise_window(self):
        self.window.update_idletasks()
        self.window.deiconify()
        self.window.lift()
        self.window.focus_force()
        try:
            self.window.attributes("-topmost", True)
            self.window.after(250, lambda: self.window.attributes("-topmost", False))
        except tk.TclError:
            pass

        # Important: one explicit paint cycle
        try:
            self.root.update_idletasks()
            self.root.update()
        except tk.TclError:
            pass

    def _submit(self):
        self.choice = self.selection.get()
        self._on_close()

    def _on_close(self):
        try:
            if self.window and self.window.winfo_exists():
                self.window.destroy()
        except tk.TclError:
            pass

        if self.own_root:
            try:
                self.root.quit()
            except tk.TclError:
                pass
            try:
                self.root.destroy()
            except tk.TclError:
                pass

    def show(self):
        """
        Blocks until the window closes and returns the selected choice (or None).
        Caller does NOT run mainloop().
        """
        self._raise_window()

        while self.window.winfo_exists():
            try:
                self.root.update_idletasks()
                self.root.update()
            except tk.TclError:
                traceback.print_exc()
                break

        return self.choice