# Auto-generated template with sensor getters and action senders
import asyncio
import threading
import json
import websockets
import subprocess
import time

# --- Global Variables ---
sensor_values = {}
sensor_lock = threading.Lock()

# --- Sensor Accessors ---
def get_battery_state():
    with sensor_lock:
        value = sensor_values.get('/battery_state')
        if value is None or value == '':
            return None
        return sensor_values.get('/battery_state')

def get_cliff_intensity():
    with sensor_lock:
        value = sensor_values.get('/cliff_intensity')
        if value is None or value == '':
            return None
        return sensor_values.get('/cliff_intensity')

def get_cmd_audio():
    with sensor_lock:
        value = sensor_values.get('/cmd_audio')
        if value is None or value == '':
            return None
        return sensor_values.get('/cmd_audio')

def get_cmd_lightring():
    with sensor_lock:
        value = sensor_values.get('/cmd_lightring')
        if value is None or value == '':
            return None
        return sensor_values.get('/cmd_lightring')

def get_cmd_vel():
    with sensor_lock:
        value = sensor_values.get('/cmd_vel')
        if value is None or value == '':
            return None
        return sensor_values.get('/cmd_vel')

def get_dock_status():
    with sensor_lock:
        value = sensor_values.get('/dock_status')
        if value is None or value == '':
            return None
        return sensor_values.get('/dock_status')
    
def get_hazard_detection():
    with sensor_lock:
        value = sensor_values.get('/hazard_detection')
        if value is None or value == '':
            return None
        return sensor_values.get('/hazard_detection')

def get_imu():
    with sensor_lock:
        value = sensor_values.get('/imu')
        if value is None or value == '':
            return None
        return sensor_values.get('/imu')

def get_interface_buttons():
    with sensor_lock:
        value = sensor_values.get('/interface_buttons')
        if value is None or value == '':
            return None
        return sensor_values.get('/interface_buttons')

def get_ir_intensity():
    with sensor_lock:
        value = sensor_values.get('/ir_intensity')
        if value is None or value == '':
            return None
        return sensor_values.get('/ir_intensity')

def get_ir_opcode():
    with sensor_lock:
        value = sensor_values.get('/ir_opcode')
        if value is None or value == '':
            return None
        return sensor_values.get('/ir_opcode')

def get_kidnap_status():
    with sensor_lock:
        value = sensor_values.get('/kidnap_status')
        if value is None or value == '':
            return None
        return sensor_values.get('/kidnap_status')
    
def get_mobility_monitor_transition_event():
    with sensor_lock:
        value = sensor_values.get('/mobility_monitor/transition_event')
        if value is None or value == '':
            return None
        return sensor_values.get('/mobility_monitor/transition_event')

def get_mouse():
    with sensor_lock:
        value = sensor_values.get('/mouse')
        if value is None or value == '':
            return None
        return sensor_values.get('/mouse')

def get_odom():
    with sensor_lock:
        value = sensor_values.get('/odom')
        if value is None or value == '':
            return None
        return sensor_values.get('/odom')

def get_parameter_events():
    with sensor_lock:
        value = sensor_values.get('/parameter_events')
        if value is None or value == '':
            return None
        return sensor_values.get('/parameter_events')

def get_robot_state_transition_event():
    with sensor_lock:
        value = sensor_values.get('/robot_state/transition_event')
        if value is None or value == '':
            return None
        return sensor_values.get('/robot_state/transition_event')

def get_rosout():
    with sensor_lock:
        value = sensor_values.get('/rosout')
        if value is None or value == '':
            return None
        return sensor_values.get('/rosout')

def get_slip_status():
    with sensor_lock:
        value = sensor_values.get('/slip_status')
        if value is None or value == '':
            return None
        return sensor_values.get('/slip_status')

def get_static_transform_transition_event():
    with sensor_lock:
        value = sensor_values.get('/static_transform/transition_event')
        if value is None or value == '':
            return None
        return sensor_values.get('/static_transform/transition_event')

def get_stop_status():
    with sensor_lock:
        value = sensor_values.get('/stop_status')
        if value is None or value == '':
            return None
        return sensor_values.get('/stop_status')

def get_tf():
    with sensor_lock:
        value = sensor_values.get('/tf')
        if value is None or value == '':
            return None
        return sensor_values.get('/tf')

def get_tf_static():
    with sensor_lock:
        value = sensor_values.get('/tf_static')
        if value is None or value == '':
            return None
        return sensor_values.get('/tf_static')

def get_wheel_status():
    with sensor_lock:
        value = sensor_values.get('/wheel_status')
        if value is None or value == '':
            return None
        return sensor_values.get('/wheel_status')

def get_wheel_ticks():
    with sensor_lock:
        value = sensor_values.get('/wheel_ticks')
        if value is None or value == '':
            return None
        return sensor_values.get('/wheel_ticks')

def get_wheel_vels():
    with sensor_lock:
        value = sensor_values.get('/wheel_vels')
        if value is None or value == '':
            return None
        return sensor_values.get('/wheel_vels')


# --- Action Senders ---
def send_audio_note_sequence(param=None):
    _send_action("audio_note_sequence", "/audio_note_sequence irobot_create_msgs/action/AudioNoteSequence", param)

def send_dock(param=None):
    _send_action("dock", "/dock irobot_create_msgs/action/Dock", param)

def send_drive_arc(param=None):
    _send_action("drive_arc", "/drive_arc irobot_create_msgs/action/DriveArc", param)

def send_drive_distance(param=None):
    _send_action("drive_distance", "/drive_distance irobot_create_msgs/action/DriveDistance", param)

def send_led_animation(param=None):
    _send_action("led_animation", "/led_animation irobot_create_msgs/action/LedAnimation", param)

def send_navigate_to_position(param=None):
    _send_action("navigate_to_position", "/navigate_to_position irobot_create_msgs/action/NavigateToPosition", param)

def send_rotate_angle(param=None):
    _send_action("rotate_angle", "/rotate_angle irobot_create_msgs/action/RotateAngle", param)

def send_undock(param=None):
    _send_action("undock", "/undock irobot_create_msgs/action/Undock", param)

def send_wall_follow(param=None):
    _send_action("wall_follow", "/wall_follow irobot_create_msgs/action/WallFollow", param)

# --- Internal Functions ---
def start_ws_listener():
    """
    Start a WebSocket listener in a separate thread.
    This function connects to a WebSocket server and updates the sensor values.
    """
    print("Starting WebSocket listener...")
    async def listen():
        print("Connecting to WebSocket server...")
        uri = 'ws://localhost:6789'
        async with websockets.connect(uri) as websocket:
            print(f"Connected to {uri}")
            while True:
                message = await websocket.recv()
                print(message)
                data = json.loads(message)
                with sensor_lock:
                    sensor_values.update(data)

    def run():
        asyncio.new_event_loop().run_until_complete(listen())

    thread = threading.Thread(target=run, daemon=True)
    thread.start()

def _send_action(name, path, param):
    """
    Send a command to a ROS2 action and display the output in the terminal.
    Args:
        name (str): The name of the action.
        path (str): The action path.
        param (str): The parameter to send.
    Returns:
        None
    """
    if param is None:
        param_str = '"{}"'
    else:
        param_str = f'"{{{param}}}"'

    command = f"ros2 action send_goal {path} {param_str}"
    print(f"[Action] {name}: {command}")

    process = subprocess.Popen(
        command, shell=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    for line in process.stdout:
        print(line, end="")
    process.wait()
    if process.returncode != 0:
        print("Error:", process.stderr.read())

if __name__ == '__main__':
    # Start the background listener
    start_ws_listener()

    # Example usage of sensor getters
    # You can replace this with your own code
    print('Waiting for sensor data...')
    for _ in range(10):
        val = get_battery_state()
        if val is not None:
            print('Battery State:', val)
            break
        time.sleep(1)
    else:
        print('Battery state not received within timeout.')

