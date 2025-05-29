# actions.py
import subprocess
import threading
import tkinter as tk
from getters import get_all_actions


terminal_output: tk.Text|None = None


def set_terminal_output(output_widget:tk.Text):
    """
    Set the terminal output widget for displaying command results
    Args:
        output_widget (tk.Text): The Text widget to display terminal output
    Returns:
        None
    """
    global terminal_output
    terminal_output = output_widget


def send_action_command(action, param_entry):
    """
    Send a command to a ROS2 action and display the output in the terminal
    Args:
        action (list): The action to send the command to
        param_entry (tk.Entry): The Entry widget for user input
    Returns:
        None
    """
    # Format the parameter string
    if not param_entry.get().strip():
        param = '"{}"'
    else:
        param = '"{' + param_entry.get().strip() + '}"'

    if terminal_output is None:
        return
    # Display the command in the terminal output
    terminal_output.config(state=tk.NORMAL)
    terminal_output.insert(
        tk.END, f"\n$ Sending {action[0][1:]} with param: {param}\n\n")
    terminal_output.config(state=tk.DISABLED)

    def run_command():
        """
        Run the command in a separate thread to avoid blocking the GUI
        This function captures the output and error messages from the command
        Args:
            None
        Returns:
            None
        """
        process = subprocess.Popen(
            f"ros2 action send_goal {action[1]} {param}",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if process.stdout is None or terminal_output is None:
            return
        # Display the output in the terminal
        for line in process.stdout:
            terminal_output.config(state=tk.NORMAL)
            terminal_output.insert(tk.END, line)
            terminal_output.see(tk.END)
            terminal_output.config(state=tk.DISABLED)

        process.wait()
        if process.returncode != 0 and process.stderr is not None:
            error_message = process.stderr.read()
            terminal_output.config(state=tk.NORMAL)
            terminal_output.insert(tk.END, f"Error: {error_message}")
            terminal_output.see(tk.END)
            terminal_output.config(state=tk.DISABLED)

    threading.Thread(target=run_command, daemon=True).start()


def create_action_buttons(action_buttons_frame):
    """
    Create action buttons in the given frame
    Args:
        action_buttons_frame (tk.Frame): The frame to place the action buttons in
    Returns:
        None
    """
    actions = get_all_actions()

    for widget in action_buttons_frame.winfo_children():
        widget.destroy()

    for action in actions:
        row_frame = tk.Frame(action_buttons_frame, bg="white")
        row_frame.pack(fill="x", pady=5)

        param_entry = tk.Entry(row_frame, font=("Arial", 12))
        param_entry.pack(side="right", fill="both", expand=True, padx=5)

        action_name = action[0][1:].replace("_", " ")

        action_button = tk.Button(
            row_frame, text=action_name,
            command=lambda a=action, p=param_entry: send_action_command(a, p),
            bg="lightblue", fg="black", font=("Arial", 12),
            wraplength=0, justify="left", width=15, height=1,
            padx=10, pady=5
        )
        action_button.pack(side="left", fill="both", expand=True, padx=5)

        # Binding keyboard shortcuts to the parameter input boxes
        shortcuts = {
            "<Control-c>": "<<Copy>>",
            "<Control-x>": "<<Cut>>", 
            "<Control-v>": "<<Paste>>", 
            "<Control-z>": "<<Undo>>", 
            "<Control-y>": "<<Redo>>", 
            "<Control-a>": "<<SelectAll>>", 
        }

        for shortcut, action_event in shortcuts.items():
            param_entry.bind(shortcut, lambda e, a=action_event,
                             entry=param_entry: entry.event_generate(a))
