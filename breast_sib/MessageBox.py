import tkinter as tk

class MessageBox:
    def __init__(self, message_top="", message_body="", message_end="", title="Error", width=500, height=300):
        """
        Initializes a Tkinter message box with a title, message, and exit behavior.

        :param message_top: The top message (title of the message box).
        :param message_body: The main body message.
        :param message_end: The ending message (e.g., a final note or warning).
        :param title: The title of the message box window.
        :param width: The width of the message box.
        :param height: The height of the message box.
        """
        self.message_top = message_top
        self.message_body = message_body
        self.message_end = message_end
        self.title = title
        self.width = width
        self.height = height

    def show_message(self):
        """Displays the message box and exits the script after the user closes it."""
        # Initialize Tkinter
        root = tk.Tk()
        root.withdraw()  # Hide main Tkinter window

        # Create a custom Toplevel message box
        message_window = tk.Toplevel()
        message_window.title(self.title)
        message_window.geometry(f"{self.width}x{self.height}")  # Set window size

        # Centered Title Label
        title_label = tk.Label(message_window, text=self.message_top, wraplength=self.width-40, 
                               font=("Arial", 12, "bold"), justify="center")
        title_label.pack(pady=(10, 5))  # Extra padding to separate title from body

        # Left-Aligned Body Label
        body_label = tk.Label(message_window, text=self.message_body, wraplength=self.width-40, 
                              justify="left", anchor="w")
        body_label.pack(padx=20, pady=(0, 10), anchor="w")  # Anchor 'w' (west) aligns left

        # Centered End Message Label
        end_label = tk.Label(message_window, text=self.message_end, wraplength=self.width-40, 
                             font=("Arial", 10, "italic"), justify="center")
        end_label.pack(pady=(10, 5))  # Spacing before the OK button

        # OK Button to close the message box
        ok_button = tk.Button(message_window, text="OK", command=message_window.destroy)
        ok_button.pack(pady=10)

        # Wait for the user to close the window
        message_window.wait_window()

        # Destroy Tkinter instance
        root.destroy()

# Example usage:
# msg_box = MessageBox("Warning", "This is a critical error.", "Please contact support.", title="Critical Error")
# msg_box.show_and_exit()
