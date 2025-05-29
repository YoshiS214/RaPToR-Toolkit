# sensors.py
import subprocess
import threading
import tkinter as tk
import json
import os
from sensor_websocket import update_sensor_state


def parse_sensor_output_to_json(output: str):
    """
    Parses the sensor output into a dictionary format, like the Save button does
    Args:
        output (str): The sensor output string
    Returns:
        dict: A dictionary containing the parsed sensor data
    """
    data:dict[str,str] = {}
    for line in output.splitlines():
        if ": " in line:
            key, value = line.split(": ", 1)
            data[key.strip()] = value.strip()
    return data


def monitor_sensor(topic, var, textbox):
    """
    Monitor a ROS2 topic and update the textbox with the output
    Args:
        topic (str): The ROS2 topic to monitor
        var (tk.BooleanVar): The variable to control the monitoring
        textbox (tk.Text): The textbox to update with the output
    Returns:
        None
    """
    def fetch():
        while var.get():
            try:
                # Run the command to fetch the topic data
                process = subprocess.run(
                    f"ros2 topic echo --once {topic}",
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    check=True
                )

                output = process.stderr.strip() or process.stdout.strip()

                def update():
                    textbox.config(state=tk.NORMAL)
                    textbox.delete("1.0", tk.END)
                    textbox.insert(tk.END, output.strip())
                    num_lines = output.count('\n') + 1
                    textbox.config(height=num_lines)
                    textbox.config(state=tk.DISABLED)
                    content = textbox.get("1.0", tk.END).strip()

                    # Parse the content and update the sensor state
                    data = parse_sensor_output_to_json(content)
                    update_sensor_state(topic, var.get(), data.__str__())

                textbox.after(0, update)

            except Exception as e:
                textbox.after(0, lambda e=e: textbox.insert(
                    tk.END, f"Error: {e}"))

    threading.Thread(target=fetch, daemon=True).start()


def toggle_sensor(topic, var, textbox_frame, textbox):
    """
    Toggle the sensor monitoring on or off
    Args:
        topic (str): The ROS2 topic to monitor
        var (tk.BooleanVar): The variable to control the monitoring
        textbox_frame (tk.Frame): The frame containing the textbox
        textbox (tk.Text): The textbox to update with the output
    Returns:
        None
    """
    hovering = {"value": False}

    def save_to_json(topic, textbox, button):
        """
        Save the content of the textbox to a JSON file
        Args:
            topic (str): The ROS2 topic to monitor
            textbox (tk.Text): The textbox to save the content from
            button (tk.Button): The button to update the status
        Returns:
            None
        """
        content = textbox.get("1.0", tk.END).strip()
        if content:
            try:
                data = parse_sensor_output_to_json(content)

                os.makedirs("sensors", exist_ok=True)
                filename = os.path.join(
                    "sensors", f"{topic.replace('/', '')}.json")
                with open(filename, "w") as f:
                    json.dump(data, f, indent=4)

                button.config(text="Saved!", bg="green",
                              activebackground="green")

            except Exception as e:
                print(f"Error saving JSON: {e}")
                button.config(text="Try again!", bg="red",
                              activebackground="red")
        else:
            button.config(text="Try again!", bg="red", activebackground="red")

    def on_enter(_):
        '''
        Change button color and text on hover
        Args:
            _ (tk.Event): The event object
        Returns:
            None
        '''
        hovering["value"] = True

    def on_leave(event, button):
        '''
        Change button color and text on leave
        Args:
            event (tk.Event): The event object
            button (tk.Button): The button to update the status
        Returns:
            None
        '''
        hovering["value"] = False
        button.config(text="Save to JSON", bg="lightblue",
                      activebackground="lightblue")

    # Create button only once and reuse
    if not hasattr(textbox_frame, "save_btn"):
        save_btn = tk.Button(
            textbox_frame,
            text="Save to JSON",
            bg="lightblue",
            fg="black",
            command=lambda t=topic, tx=textbox: save_to_json(
                t, tx, textbox_frame.save_btn)
        )
        save_btn.bind("<Enter>", on_enter)
        save_btn.bind("<Leave>", lambda e, b=save_btn: on_leave(e, b))
        textbox_frame.save_btn = save_btn

    save_btn = textbox_frame.save_btn

    # Update button text and color based on hover state
    if var.get():
        textbox_frame.pack(fill="x", padx=30, pady=(2, 10))
        textbox.config(state=tk.NORMAL)
        textbox.delete("1.0", tk.END)
        textbox.insert(tk.END, "Fetching...")
        textbox.config(state=tk.DISABLED)

        if not save_btn.winfo_ismapped():
            save_btn.pack(pady=5)

        monitor_sensor(topic, var, textbox)

    else:
        textbox_frame.pack_forget()
        save_btn.pack_forget()
