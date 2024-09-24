import tkinter as tk 
from tkinter import font

class MarginInputWindow:
    def __init__(self, parent, numColumns, headers, callback, templates=None):
        self.callback = callback  # Store the callback function
        self.numColumns = numColumns
        self.headers = headers
        self.entries = {header: {} for header in headers}  # Dictionary for each column
        self.templates = templates or {}  # Optional templates for default values

        self.window = tk.Toplevel(parent)
        self.window.title("Please provide PTV margins")
        
        #self.window.configure(bg='#2c3e50')

        # Define custom font
        self.customFont = font.Font(family="Helvetica", size=10)

        self.window.protocol("WM_DELETE_WINDOW", self.onClose)  # Handle window close event

        # Create headers
        for i, header in enumerate(headers):
            tk.Label(self.window, text=header).grid(row=0, column=i+1)

        # Define margin directions
        self.directions = ['Superior', 'Inferior', 'Left', 'Right', 'Anterior', 'Posterior']

        # Create labels for directions and input entries for each column
        for i, direction in enumerate(self.directions):
            tk.Label(self.window, text=direction).grid(row=i+1, column=0)

            # Create entries for each column
            for j, header in enumerate(headers):
                self.entries[header][direction] = tk.Entry(self.window)
                self.entries[header][direction].grid(row=i+1, column=j+1)

        # Add template listbox
        if self.templates:
            self.templateListBox = tk.Listbox(self.window)
            for templateName in self.templates.keys():
                self.templateListBox.insert(tk.END, templateName)
            self.templateListBox.grid(row=1, column=numColumns+1, rowspan=len(self.directions))
            self.templateListBox.bind("<<ListboxSelect>>", self.loadTemplate)

        # Submit button
        submitButton = tk.Button(self.window, text="Submit", command=self.submit)
        submitButton.grid(row=len(self.directions)+1, column=1, columnspan=numColumns)

    def loadTemplate(self, event):
        # Get the current selection from the listbox
        selected = self.templateListBox.curselection()

        # Check if any item is selected
        if not selected:
            return  # Exit the function if no selection is made

        selectedTemplate = self.templateListBox.get(selected[0])  # Get the first selected item
        templateValues = self.templates[selectedTemplate]

        # Populate the entries with the template values
        for header, values in templateValues.items():
            for direction, value in values.items():
                self.entries[header][direction].delete(0, tk.END)
                self.entries[header][direction].insert(0, str(value))

    def submit(self):
        # Gather the input values into dictionaries for each column
        result = {header: {direction: float(self.entries[header][direction].get()) for direction in self.directions}
                  for header in self.headers}

        # Call the callback with the result
        self.callback(result)
        self.onClose()

    def onClose(self):
        self.window.destroy()  # Properly destroy the Toplevel window
        
if __name__ == "__main__":
    def testCallback(result):
        print("Test callback received margins:")
        print(result)

    root = tk.Tk()
    root.withdraw()  # Hide the root window
    headers = ['ProstateMargin', 'NodeMargin']
    templates = {
        
        'Carpenter': {
            'ProstateMargin': {'Superior': 0.5, 'Inferior': 0.5, 'Anterior': 0.7, 'Posterior': 0.3, 'Right': 0.5, 'Left': 0.5},
            'NodeMargin': {'Superior': 0.7, 'Inferior': 0.7, 'Anterior': 0.7, 'Posterior': 0.7, 'Right': 0.7, 'Left': 0.7}
                     },
        
        'Haas': {
            'ProstateMargin': {'Superior': 0.7, 'Inferior': 0.7, 'Anterior': 0.7, 'Posterior': 0.5, 'Right': 0.7, 'Left': 0.7},
            'NodeMargin': {'Superior': 0.7, 'Inferior': 0.7, 'Anterior': 0.7, 'Posterior': 0.7, 'Right': 0.7, 'Left': 0.7}
                },
        'Custom': {
            'ProstateMargin': {'Superior': 0.0, 'Inferior': 0.0, 'Anterior': 0.0, 'Posterior': 0.0, 'Right': 0.0, 'Left': 0.0},
            'NodeMargin': {'Superior': 0.0, 'Inferior': 0.0, 'Anterior': 0.0, 'Posterior': 0.0, 'Right': 0.0, 'Left': 0.0}
            }
                }
    testWindow = MarginInputWindow(root, numColumns=2, headers=headers, callback=testCallback, templates=templates)
    root.mainloop()
