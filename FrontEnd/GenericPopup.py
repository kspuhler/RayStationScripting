import sys
import os
import tkinter as tk

class GenericPopup(tk.Tk):
    '''Generic window for displaying information to the user when running RS scripts'''
    def __init__(self, title='GenericPopupWindow', message='GenericMessageNoKwargGiven'):
        super().__init__()
        self.title(title)
        self.configure(bg='darkgrey')
        self.message = message

        self.messageLabel = tk.Label(self, text=self.message, bg='darkgrey', fg='black', padx=20, pady=20)
        self.messageLabel.pack(expand=True, fill='both')

        self.buttonFrame = tk.Frame(self, bg='darkgrey')
        self.buttonFrame.pack(pady=10)

        self.okButton = tk.Button(self.buttonFrame, text="Okay", command=self.closeEvent)
        self.okButton.pack(side='left', padx=5)

    def closeEvent(self):
        self.destroy()

    def showPopup(self):
        self.mainloop()

