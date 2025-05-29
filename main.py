# main.py
import tkinter as tk
from tkinter import ttk
import threading
from getters import get_all_topics
from terminal import execute_terminal_command, stop_running_process, set_terminal_widgets
from actions import create_action_buttons, set_terminal_output
from sensors import toggle_sensor
from move import MovementController
from sensor_websocket import start_websocket_server, update_sensor_state
from template_generator import generate_template


def send_keypress(key):
    """
    Send a keypress to the movement controller
    Args:
        key (str): The key to send
    Returns:
        None
    """
    movement_controller.send_key(key)


def bind_movement_keys():
    """
    Bind the movement keys to the keypress events
    Args:
        None
    Returns:
        None
    """
    def on_keypress(event):
        '''
        Send the keypress to the movement controller
        Args:
            event (tk.Event): The event object
        Returns:
            None
        '''
        send_keypress(event.keysym.lower())

    def on_keyrelease(event):
        '''
        Send the keyrelease to the movement controller
        Args:
            event (tk.Event): The event object
        Returns:
            None
        '''
        send_keypress('x')

    for key in ['w', 'a', 's', 'd', 'q', 'e', 'z', 'c']:
        root.bind(f"<KeyPress-{key}>", on_keypress)
        root.bind(f"<KeyRelease-{key}>", on_keyrelease)


def unbind_movement_keys():
    """
    Unbind the movement keys from the keypress events
    Args:
        None
    Returns:
        None
    """
    for key in ['w', 'a', 's', 'd', 'q', 'e', 'z', 'c']:
        root.unbind(f"<KeyPress-{key}>")
        root.unbind(f"<KeyRelease-{key}>")


def toggle_movement():
    """
    Toggle the movement controller on or off
    Args:
        None
    Returns:
        None
    """
    if not movement_controller.is_running:
        movement_controller.start()
        toggle_btn.config(text="Stop Control", bg="red")
        bind_movement_keys()
    else:
        movement_controller.stop()
        toggle_btn.config(text="Start Control", bg="green")
        unbind_movement_keys()


def update_recordings_list():
    """
    Update the recordings listbox with the current recordings
    Args:
        None
    Returns:
        None
    """
    recordings_listbox.delete(0, tk.END)
    for name in movement_controller.recordings.keys():
        recordings_listbox.insert(tk.END, name)


def toggle_record():
    """
    Toggle the recording state
    Args:
        None
    Returns:
        None
    """
    if not movement_controller.recording:
        if not movement_controller.is_running:
            movement_controller.start()
        bind_movement_keys()
        movement_controller.start_recording()
        record_btn.config(text="Recording...", bg="red")
    else:
        movement_controller.stop_recording()
        record_btn.config(text="Record", bg="red")
        update_recordings_list()


def rename_recording():
    """
    Rename the selected recording
    Args:
        None
    Returns:
        None
    """
    selection = recordings_listbox.curselection()
    if selection:
        old_name = recordings_listbox.get(selection[0])
        new_name = rename_entry.get()
        if new_name and new_name not in movement_controller.recordings:
            movement_controller.recordings[new_name] = movement_controller.recordings.pop(
                old_name)
            movement_controller.save_recordings()
            update_recordings_list()
        rename_entry.delete(0, tk.END)


def play_selected_recording():
    """
    Play the selected recording
    Args:
        None
    Returns:
        None
    """
    selection = recordings_listbox.curselection()
    if selection:
        name = recordings_listbox.get(selection[0])
        if not movement_controller.is_running:
            movement_controller.start()
        threading.Thread(target=movement_controller.play_recording,
                         args=(name,), daemon=True).start()


def delete_selected_recording():
    """
    Delete the selected recording
    Args:
        None
    Returns:
        None
    """
    selection = recordings_listbox.curselection()
    if selection:
        name = recordings_listbox.get(selection[0])
        movement_controller.delete_recording(name)
        update_recordings_list()


def on_action_frame_configure(event):
    """
    Update the scroll region of the action canvas when the frame is resized
    Args:
        event (tk.Event): The event object
    Returns:
        None
    """
    action_canvas.configure(scrollregion=action_canvas.bbox("all"))


if __name__ == "__main__":
    # Setup the window
    root = tk.Tk()
    root.title("RaPToR: Rapid Prototyping Toolkit for Robotics")
    root.geometry("3200x1800")
    root.resizable(True, True)
    root.configure(bg="white")
    root.bind("<Control-c>", stop_running_process)
    root.bind("<Control-C>", stop_running_process)

    root.protocol("WM_DELETE_WINDOW", root.destroy)

    # Initialize the movement controller
    movement_controller = MovementController()

    # Start the WebSocket server
    start_websocket_server()

    container = tk.Frame(root, bg="white")
    container.pack(fill="both", expand=True)

    # Main Frame
    main_frame = tk.Frame(container, bg="white")
    main_frame.grid_rowconfigure(0, weight=1)
    for i in range(3):
        main_frame.grid_columnconfigure(i, weight=1, uniform="group")

    # --- Terminal Column ---
    terminal_frame = tk.Frame(main_frame, bg="white")
    terminal_frame.grid(row=0, column=0, sticky="nsew", padx=5)
    tk.Label(terminal_frame, text="Terminal", bg="white", font=(
        "Arial", 16, "bold")).pack(anchor="center", pady=5)

    # Terminal output
    terminal_output = tk.Text(terminal_frame, height=20, font=(
        "Arial", 12), state=tk.DISABLED, bg="black", fg="white", padx=5)
    terminal_output.pack(fill="both", expand=True)
    terminal_output.tag_config("error", foreground="red")

    # Terminal input
    input_frame = tk.Frame(terminal_frame, bg="white")
    input_frame.pack(fill="x", pady=5)
    terminal_input = tk.Entry(input_frame, font=("Arial", 12))
    terminal_input.pack(side="left", fill="x", expand=True, padx=5)
    tk.Button(input_frame, text="Execute", bg="blue", fg="white", font=(
        "Arial", 12), command=execute_terminal_command).pack(side="right")
    terminal_input.bind("<Return>", execute_terminal_command)
    set_terminal_widgets(terminal_output, terminal_input)
    set_terminal_output(terminal_output)

    # --- Actions Column ---
    action_frame = tk.Frame(main_frame, bg="white")
    action_frame.grid(row=0, column=1, sticky="nsew", padx=5)

    # Action Buttons (top half)
    action_buttons_top_frame = tk.Frame(action_frame, bg="white")
    action_buttons_top_frame.pack(fill="both", expand=True)

    tk.Label(action_buttons_top_frame, text="Actions", bg="white", font=(
        "Arial", 16, "bold")).pack(anchor="center", pady=(5, 10))
    action_canvas = tk.Canvas(action_buttons_top_frame,
                              bg="white", highlightthickness=0)
    action_scrollbar = ttk.Scrollbar(
        action_buttons_top_frame, orient="vertical", command=action_canvas.yview)
    action_canvas.configure(yscrollcommand=action_scrollbar.set)
    action_canvas.pack(side="left", fill="both", expand=True)
    action_scrollbar.pack(side="right", fill="y")

    # Frame for action buttons inside the canvas
    action_buttons_frame = tk.Frame(action_canvas, bg="white")
    action_canvas.create_window(
        (0, 0), window=action_buttons_frame, anchor="nw", tags="buttons_frame")
    action_buttons_frame.bind("<Configure>", on_action_frame_configure)
    action_canvas.bind("<Configure>", lambda e: action_canvas.itemconfig(
        "buttons_frame", width=e.width))
    create_action_buttons(action_buttons_frame)

    # Movement Control + Recordings (bottom half)
    movement_frame = tk.Frame(action_frame, bg="white",
                              height=root.winfo_screenheight()//3)
    movement_frame.pack(fill="x", pady=10)

    movement_frame.grid_columnconfigure(0, weight=1, uniform="group")
    movement_frame.grid_columnconfigure(1, weight=1, uniform="group")

    # Movement (left)
    left_frame = tk.Frame(movement_frame, bg="white")
    left_frame.grid(row=0, column=0, sticky="nsew", padx=10)

    tk.Label(left_frame, text="Movement Control", font=(
        "Arial", 16, "bold"), bg="white").pack(pady=5)
    tk.Label(left_frame, text="Control keys",
             font=("Courier", 12), bg="white").pack()

    instructions_frame = tk.Frame(left_frame, bg="white", relief="solid", bd=1)
    instructions_frame.pack(pady=5, fill="x")

    tk.Label(instructions_frame, text="Q - Forward + Left\n"
             "W - Forward\n"
             "E - Forward + Right\n"
             "A - Left\n"
             "S - Backward\n"
             "D - Right\n"
             "Z - Backward + Left\n"
             "C - Backward + Right\n"
             "X - Stop",
             font=("Courier", 12), bg="white", anchor="w", justify="left"
             ).pack(padx=10, pady=10, fill="both")

    toggle_btn = tk.Button(left_frame, text="Start Control", font=(
        "Arial", 14), bg="lightblue", fg="black", command=toggle_movement)
    toggle_btn.pack(pady=10)

    # Recordings (right)
    right_frame = tk.Frame(movement_frame, bg="white")
    right_frame.grid(row=0, column=1, sticky="nsew", padx=10)

    tk.Label(right_frame, text="Recordings", font=(
        "Arial", 16, "bold"), bg="white").pack(pady=5)

    record_btn = tk.Button(right_frame, text="Record",
                           bg="lightblue", fg="black", font=("Arial", 12))
    record_btn.pack(pady=5)

    # Scrollable listbox for recordings
    listbox_frame = tk.Frame(right_frame, bg="white")
    listbox_frame.pack(fill="both", expand=True, pady=5)
    recordings_scrollbar = tk.Scrollbar(listbox_frame, orient="vertical")
    recordings_listbox = tk.Listbox(listbox_frame, font=(
        "Arial", 12), height=5, yscrollcommand=recordings_scrollbar.set)
    recordings_scrollbar.config(command=recordings_listbox.yview)
    recordings_listbox.pack(side="left", fill="both", expand=True)
    recordings_scrollbar.pack(side="right", fill="y")

    update_recordings_list()

    # Recording controls
    rename_entry = tk.Entry(right_frame, font=("Arial", 12))
    rename_entry.pack(fill="x", pady=2)

    rename_btn = tk.Button(right_frame, text="Rename", font=(
        "Arial", 10), bg="lightblue", fg="black")
    rename_btn.pack(pady=2)

    play_btn = tk.Button(right_frame, text="Play Selected",
                         font=("Arial", 10), bg="lightblue", fg="black")
    play_btn.pack(pady=2)

    delete_btn = tk.Button(right_frame, text="Delete Selected", font=(
        "Arial", 10), bg="lightblue", fg="black")
    delete_btn.pack(pady=2)

    record_btn.config(command=toggle_record)
    rename_btn.config(command=rename_recording)
    play_btn.config(command=play_selected_recording)
    delete_btn.config(command=delete_selected_recording)

    # --- Sensors Column ---
    sensor_frame = tk.Frame(main_frame, bg="white")
    sensor_frame.grid(row=0, column=2, sticky="nsew", padx=5)
    tk.Label(sensor_frame, text="Sensors", bg="white", font=(
        "Arial", 16, "bold")).pack(anchor="center", pady=5)

    # Button to generate template file
    generate_template_btn = tk.Button(sensor_frame, text="Generate Template File", font=(
        "Arial", 12), bg="lightblue", fg="black", command=generate_template)
    generate_template_btn.pack(pady=(10, 15), anchor="n")

    # Scrollable frame for sensor data
    sensor_canvas = tk.Canvas(sensor_frame, bg="white", highlightthickness=0)
    sensor_scrollbar = ttk.Scrollbar(
        sensor_frame, orient="vertical", command=sensor_canvas.yview)
    sensor_scrollable_frame = tk.Frame(sensor_canvas, bg="white")
    sensor_canvas.create_window(
        (0, 0), window=sensor_scrollable_frame, anchor="nw")

    sensor_canvas.configure(yscrollcommand=sensor_scrollbar.set)
    sensor_canvas.pack(side="left", fill="both", expand=True)
    sensor_scrollbar.pack(side="right", fill="y")

    def on_sensor_frame_configure(event):
        sensor_canvas.configure(scrollregion=sensor_canvas.bbox("all"))

    sensor_scrollable_frame.bind("<Configure>", on_sensor_frame_configure)
    sensor_canvas.bind("<Enter>", lambda e: sensor_canvas.bind_all(
        "<MouseWheel>", on_sensor_frame_configure))
    sensor_canvas.bind(
        "<Leave>", lambda e: sensor_canvas.unbind_all("<MouseWheel>"))

    # Format the sensor data
    for topic in get_all_topics():
        wrapper_frame = tk.Frame(sensor_scrollable_frame, bg="white")
        wrapper_frame.pack(fill="x", padx=5, pady=(5, 0), anchor="nw")
        header_frame = tk.Frame(wrapper_frame, bg="white")
        header_frame.pack(fill="x", anchor="nw")
        var = tk.IntVar(value=0)
        cb = tk.Checkbutton(header_frame, variable=var, bg="white")
        cb.pack(side="left")
        label = tk.Label(header_frame, text=topic, bg="white",
                         font=("Arial", 12), anchor="w")
        label.pack(side="left", padx=5)

        textbox_frame = tk.Frame(wrapper_frame, bg="white")
        textbox = tk.Text(textbox_frame, height=1, wrap="word", font=(
            "Courier", 10), bg="#f5f5f5", relief="sunken", bd=1, width=50)
        textbox.pack(fill="x", expand=True)
        textbox.config(state=tk.DISABLED)
        textbox_frame.pack_forget()

        # Button action to save the sensor data
        def make_callback(t=topic, v=var, tf=textbox_frame, tx=textbox):
            def on_text_change(event=None):
                if v.get():
                    value = tx.get("1.0", tk.END).strip()
                    update_sensor_state(t, v.get(), value)

            def callback():
                toggle_sensor(t, v, tf, tx)

                if v.get():
                    # When sensor is turned on, bind the live text updates
                    tx.bind("<KeyRelease>", on_text_change)
                    value = tx.get("1.0", tk.END).strip()
                    update_sensor_state(t, v.get(), value)
                else:
                    # When sensor is turned off, unbind updates
                    tx.unbind("<KeyRelease>")
                    update_sensor_state(t, v.get(), "")

            # Use root.after() to update the Text widget on the main thread
            def update_sensor_value(value):
                if v.get():
                    tx.config(state=tk.NORMAL)  # Make it editable
                    tx.delete("1.0", tk.END)
                    tx.insert("1.0", value)
                    tx.config(state=tk.DISABLED)  # Make it read-only again

            def sensor_update_callback(new_value):
                root.after(0, update_sensor_value, new_value)

            update_sensor_state(t, True, "")
            threading.Timer(1.0, sensor_update_callback,
                            args=("New Sensor Value",)).start()

            return callback

        cb.config(command=make_callback())

    main_frame.pack(fill="both", expand=True)
    root.mainloop()
