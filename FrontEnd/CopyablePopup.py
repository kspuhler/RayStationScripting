import sys
import os
import tkinter as tk

sys.path.append("F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
sys.path.append("F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")

from FrontEnd.GenericPopup import GenericPopup

class CopyablePopup(GenericPopup):
    '''Subclass of GenericPopup with an additional button to copy the message to the clipboard'''
    def __init__(self, title='GenericPopupWindow', message='GenericMessageNoKwargGiven'):
        super().__init__(title, message)

        # Remove the existing OK button
        self.okButton.pack_forget()

        # Add the copy button first
        self.copyButton = tk.Button(self.buttonFrame, text="Copy Message", command=self.copyMessage)
        self.copyButton.pack(side='left', padx=5)

        # Add the renamed close button
        self.closeButton = tk.Button(self.buttonFrame, text="Close", command=self.closeEvent)
        self.closeButton.pack(side='left', padx=5)

    def copyMessage(self):
        self.clipboard_clear()
        self.clipboard_append(self.message)
        self.update()  # Keep the clipboard updated

# Example usage
if __name__ == "__main__":
    popup = CopyablePopup(title="Copyable Popup", message="This is a message that can be copied.")
    popup.showPopup()
