# template_generator.py
import os
from Toolkit.sensor_websocket import sensor_data, sensor_data_lock
from Toolkit.getters import get_all_actions


def generate_template(output_path="template.py"):
    """
    Generate a Python template with sensor getters and action senders
    Args:
        output_path (str): The path to save the generated template
    Returns:
        None
    """
    # Gather active sensors
    with sensor_data_lock:
        enabled_sensors = {
            name: data for name, data in sensor_data.items()
            if data.get("enabled")
        }

    # Start building output content
    lines = [
        "# Auto-generated template with sensor getters and action senders",
        "import asyncio",
        "import threading",
        "import json",
        "import websockets",
        "import subprocess",
        "",
        "# --- Global Variables ---",
        "sensor_values = {}",
        "sensor_lock = threading.Lock()",
        "",
        "# --- Sensor Accessors ---"
    ]

    for name in enabled_sensors:
        safe_func_name = name.strip("/").replace("/", "_").replace("-", "_")
        lines.append(f"def get_{safe_func_name}():")
        lines.append(f"    with sensor_lock:")
        lines.append(f"        value = sensor_values.get('{name}')")
        lines.append(f"        if value is None or value == '':")
        lines.append(f"            return None")
        lines.append(f"        return sensor_values.get('{name}')")
        lines.append("")
        lines.append("")

    # Actions
    lines.append("# --- Action Senders ---")

    for action in get_all_actions():
        display_name = action[0][1:]
        action_path = action[1]
        func_name = display_name.replace("/", "_").replace("-", "_")

        lines.append(f"def send_{func_name}(param=None):")
        lines.append(
            f'    _send_action("{display_name}", "{action_path}", param)')
        lines.append("")

    # Action runner function
    lines.extend([
        "# --- Internal Functions ---",
        "def start_ws_listener():",
        "    \"\"\"",
        "    Start a WebSocket listener in a separate thread.",
        "    This function connects to the WebSocket server and updates the sensor values.",
        "    \"\"\"",
        "    async def listen():",
        "        uri = 'ws://localhost:6789'",
        "        async with websockets.connect(uri) as websocket:",
        "            while True:",
        "                message = await websocket.recv()",
        "                data = json.loads(message)",
        "                with sensor_lock:",
        "                    sensor_values.update(data)",
        "",
        "    def run():",
        "        asyncio.new_event_loop().run_until_complete(listen())",
        "",
        "    thread = threading.Thread(target=run, daemon=True)",
        "    thread.start()",
        "",
        "def _send_action(name, path, param):",
        "    \"\"\"",
        "    Send a command to a ROS2 action and display the output in the terminal.",
        "    Args:",
        "        name (str): The name of the action.",
        "        path (str): The action path.",
        "        param (str): The parameter to send.",
        "    Returns:",
        "        None",
        "    \"\"\"",
        "    if param is None:",
        '        param_str = \'"{}"\'',
        "    else:",
        '        param_str = f\'"{{{param}}}"\'',
        "",
        "    command = f\"ros2 action send_goal {path} {param_str}\"",
        "    print(f\"[Action] {name}: {command}\")",
        "",
        "    process = subprocess.Popen(",
        "        command, shell=True,",
        "        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True",
        "    )",
        "    for line in process.stdout:",
        "        print(line, end=\"\")",
        "    process.wait()",
        "    if process.returncode != 0:",
        "        print(\"Error:\", process.stderr.read())",
        "",
        "",
        "if __name__ == '__main__':",
        "    # Starting background threads",
        "    start_ws_listener()",
        "",
        "    # Example usage of sensor getters",
        "    # You can replace this with your own code",
        "    # print('Waiting for sensor data...')",
        "    # for _ in range(10):",
        "    #    val = get_battery_state()",
        "    #    if val is not None:",
        "    #        print('Battery State:', val)",
        "    #        break",
        "    #    time.sleep(1)",
        "    # else:",
        "    #    print('Battery state not received within timeout.')",
        "",

    ])

    # Write to file
    full_path = os.path.join(output_path)
    with open(full_path, "w") as f:
        f.write("\n".join(lines))

    print(f"Your template has been generated at {full_path}")
