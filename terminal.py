# terminal.py
import signal
import subprocess
import threading
import tkinter as tk

running_process: subprocess.Popen|None = None
terminal_output: tk.Text|None = None
terminal_input: tk.Entry|None = None


def set_terminal_widgets(output_widget:tk.Text, input_widget:tk.Entry):
    """
    Set the terminal output and input widgets for executing commands
    Args:
        output_widget (tk.Text): The Text widget for displaying terminal output
        input_widget (tk.Entry): The Entry widget for user input
    Returns:
        None
    """
    global terminal_output, terminal_input
    terminal_output = output_widget
    terminal_input = input_widget


def execute_terminal_command(event=None):
    """
    Execute a command in the terminal and display the output
    Args:
        event (tk.Event): The event that triggered the command execution
    Returns:
        None
    """
    global running_process
    if terminal_input is None or terminal_output is None:
        return

    if running_process:
        running_process.send_signal(signal.SIGINT)
        terminal_output.config(state=tk.NORMAL)
        terminal_output.insert(tk.END, "\nProcess stopped by user (Ctrl+C)\n")
        terminal_output.config(state=tk.DISABLED)
        running_process = None
        return

    command = terminal_input.get().strip()
    if not command:
        return

    if command.lower() == "clear":
        terminal_output.config(state=tk.NORMAL)
        terminal_output.delete("1.0", tk.END)
        terminal_output.config(state=tk.DISABLED)
        terminal_input.delete(0, tk.END)
        return

    terminal_output.config(state=tk.NORMAL)
    terminal_output.insert(tk.END, f"\n$ {command}\n")
    terminal_output.config(state=tk.DISABLED)

    def run_command():
        global running_process
        running_process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if terminal_input is None or terminal_output is None:
            return
        if running_process.stdout is not None:
            for line in running_process.stdout:
                terminal_output.config(state=tk.NORMAL)
                terminal_output.insert(tk.END, line)
                terminal_output.see(tk.END)
                terminal_output.config(state=tk.DISABLED)

        if running_process.stderr is not None:
            for line in running_process.stderr:
                terminal_output.config(state=tk.NORMAL)
                terminal_output.insert(tk.END, line, "error")
                terminal_output.see(tk.END)
                terminal_output.config(state=tk.DISABLED)

        running_process.wait()

    threading.Thread(target=run_command, daemon=True).start()
    terminal_input.delete(0, tk.END)


def stop_running_process(event=None):
    """
    Stop the currently running process in the terminal
    Args:
        event (tk.Event): The event that triggered the process stop
    Returns:
        None
    """
    global running_process
    if terminal_input is None or terminal_output is None:
        return
    if running_process:
        running_process.send_signal(signal.SIGINT)
        terminal_output.config(state=tk.NORMAL)
        terminal_output.insert(tk.END, "\nProcess stopped by user (Ctrl+C)\n")
        terminal_output.config(state=tk.DISABLED)
        running_process = None
