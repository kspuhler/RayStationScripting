import sys
import os
import tkinter as tk

sys.path.append("F$\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")
sys.path.append("F:\SHARING\Radiation Oncology Physics\RaystationScriptingPROD")

from FrontEnd.GenericPopup import GenericPopup


class CheckWithUserWindow(GenericPopup):
    '''Window to check with the user whether to continue or terminate the script'''
    def __init__(self, title='CheckWithUserWindow', message='Do you want to continue or terminate?'):
        super().__init__(title, message)
        
        # Override the buttons
        self.okButton.pack_forget()  # Remove the okay button from the parent class
        
        self.continueButton = tk.Button(self, text="Continue", command=self.continueEvent)
        self.continueButton.pack(side=tk.LEFT, padx=10, pady=10)
        
        self.terminateButton = tk.Button(self, text="Terminate", command=self.terminateEvent)
        self.terminateButton.pack(side=tk.RIGHT, padx=10, pady=10)
        
    def continueEvent(self):
        self.destroy()

    def terminateEvent(self):
        self.destroy()
        sys.exit(0)  # Forcefully terminate the script


class CheckWithUserWindowBoolean(GenericPopup):
    '''Popup window with Yes and No buttons returning True or False'''

    def __init__(self, title='CheckWithUserWindow', message='Are you sure?'):
        super().__init__(title, message)

        self.buttonFrame = tk.Frame(self, bg='darkgrey')
        self.buttonFrame.pack(pady=10)

        self.okButton.pack_forget()  # Remove the okay button from the parent class


        self.yesButton = tk.Button(self.buttonFrame, text="Yes", command=lambda: self.returnChoice(True))
        self.yesButton.pack(side='left', padx=5)

        self.noButton = tk.Button(self.buttonFrame, text="No", command=lambda: self.returnChoice(False))
        self.noButton.pack(side='left', padx=5)

        # Override the closeEvent method to terminate the script on 'x' button click
        self.protocol("WM_DELETE_WINDOW", self.terminateScript)

        # Flag to store user choice
        self.userChoice = None

    def returnChoice(self, choice):
        self.userChoice = choice
        self.destroy()  # Close the window after choice is made

    def terminateScript(self):
        self.userChoice = None  # No valid choice made
        self.destroy()  # Close the window and terminate the script
        sys.exit(0)

    def showPopup(self):
        self.mainloop()  # Show the popup window and wait for user interaction

        # After the window is closed, return the user's choice
        return self.userChoice

def main():
    # Create an instance of CheckWithUserWindowBoolean
    popup = CheckWithUserWindowBoolean(message="Do you want to proceed?")

    # Show the popup and get the user's choice
    user_choice = popup.showPopup()

    # Process the user's choice
    if user_choice is None:
        print("Script terminated.")
    elif user_choice:
        print("User chose: Yes")
        # Add your action for Yes here
    else:
        print("User chose: No")
        # Add your action for No here

if __name__ == "__main__":
    main()