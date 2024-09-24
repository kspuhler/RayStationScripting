import tkinter as tk
from tkinter import MULTIPLE, SINGLE

class DropdownMenuWindow(tk.Toplevel):
    def __init__(self, parent, items, allow_multiple=False, title = "Dropdown Menu Example", label = "Select Items:"):
        super().__init__(parent)
        self.title = title
        self.parent = parent
        
        self.selection_mode = MULTIPLE if allow_multiple else SINGLE
        
        self.label = tk.Label(self, text=label)
        self.label.pack(pady=10)
        
        self.listbox = tk.Listbox(self, selectmode=self.selection_mode, height=5)
        self.listbox.pack(padx=20, pady=10)
        
        # Insert items passed to the constructor
        for item in items:
            self.listbox.insert(tk.END, item)
        
        self.ok_button = tk.Button(self, text="OK", command=self.on_ok_button)
        self.ok_button.pack(pady=10)
        
        # Initialize variable to store selected items
        self.selected_items = None
        
    def on_ok_button(self):
        selected_indices = self.listbox.curselection()
        self.selected_items = [self.listbox.get(idx) for idx in selected_indices]
        
        if self.selection_mode == SINGLE:
            self.selected_items = self.selected_items[0] if self.selected_items else None
        
        self.destroy()  # Close the window after selection

        # Destroy the main root window after the dropdown window closes
        self.parent.destroy()
        
    def get_selected_items(self):
        return self.selected_items

# Example usage
if __name__ == "__main__":
    items = ["Apple", "Banana", "Orange", "Grapes", "Mango"]
    
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    
    dropdown_window = DropdownMenuWindow(root, items, allow_multiple=False)
    dropdown_window.grab_set()  # Make sure the dropdown window grabs focus
    root.wait_window(dropdown_window)  # Wait for the dropdown window to close
    
    selected_items = dropdown_window.get_selected_items()
    print("Selected Items:", selected_items)
