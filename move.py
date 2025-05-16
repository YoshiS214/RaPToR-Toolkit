# move.py
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import threading
import json
import os
import time

RECORDINGS_FILE = "recordings.json"

KEYMAP = {
    'w': (1.0, 0.0),
    's': (-1.0, 0.0),
    'a': (0.0, 1.0),
    'd': (0.0, -1.0),
    'q': (0.5, 1.0),
    'e': (0.5, -1.0),
    'z': (-0.5, -1.0),
    'c': (-0.5, 1.0),
    'x': (0.0, 0.0)
}


class TeleopNode(Node):
    """
    A simple teleop-operation node that publishes velocity commands to the robot
    """

    def __init__(self):
        super().__init__('teleop_node')
        self.publisher_ = self.create_publisher(Twist, 'cmd_vel', 10)

    def send_command(self, key):
        """
        Send a command based on the key pressed
        Args:
            key (str): The key pressed
        Returns:
            None
        """
        if key in KEYMAP:
            linear, angular = KEYMAP[key]
            msg = Twist()
            msg.linear.x = linear
            msg.angular.z = angular
            self.publisher_.publish(msg)


class MovementController:
    """
    A class to control the movement of a robot using teleop-operation commands
    It can also record and play back sequences of commands
    """

    def __init__(self):
        self.node = None
        self.thread = None
        self.is_running = False
        self.is_initialized = False
        self.recording = False
        self.current_recording = []
        self.recordings = self.load_recordings()
        self.last_key = None
        self.last_time = None
        self.key_held = False
        self.idle_thread = None
        self.idle_monitoring = False
        self.key_held_flag = False

    def _spin(self):
        """
        Spin the ROS2 node in a separate thread
        This allows the node to process incoming messages and callbacks
        Args:
            None
        Returns:
            None
        """
        rclpy.spin(self.node)

    def start(self):
        """
        Start the teleop node and spin it in a separate thread
        Args:
            None
        Returns:
            None
        """
        if not self.is_running:
            if not self.is_initialized:
                rclpy.init()
                self.is_initialized = True
            self.node = TeleopNode()
            self.thread = threading.Thread(target=self._spin, daemon=True)
            self.thread.start()
            self.is_running = True

    def stop(self):
        """
        Stop the teleop node and clean up resources
        Args:
            None
        Returns:
            None
        """
        if self.is_running:
            if self.node:
                self.node.destroy_node()
            if self.is_initialized:
                rclpy.shutdown()
                self.is_initialized = False
            self.is_running = False

    def load_recordings(self):
        """
        Load recordings from a JSON file
        Args:
            None
        Returns:
            dict: A dictionary of recordings
        """
        # Check if the recordings file exists
        if os.path.exists(RECORDINGS_FILE):
            with open(RECORDINGS_FILE, "r") as f:
                return json.load(f)
        return {}

    def save_recordings(self):
        """
        Save recordings to a JSON file.
        Args:
            None
        Returns:
            None
        """
        # Ensure the directory exists
        os.makedirs(os.path.dirname(RECORDINGS_FILE), exist_ok=True)
        with open(RECORDINGS_FILE, "w") as f:
            json.dump(self.recordings, f)

    def start_recording(self):
        """
        Start recording the key presses and their durations
        Args:
            None
        Returns:
            None
        """
        self.recording = True
        self.current_recording = []
        self.last_key = None
        self.last_time = None
        self.key_held = False
        self._start_idle_monitor()

    def stop_recording(self):
        """
        Stop the recording and save it to a file
        Args:
            None
        Returns:
            None
        """
        if not self.recording:
            return

        self.recording = False
        self.idle_monitoring = False
        self.last_key = None
        self.last_time = None

        # Clean up recording
        cleaned = []
        for action in self.current_recording:
            key, duration = action
            # Skip short stop blips
            if key == 'x' and duration <= 0.01:
                continue

            # Merge with previous
            if cleaned and cleaned[-1][0] == key:
                cleaned[-1] = (key, cleaned[-1][1] + duration)
            else:
                cleaned.append((key, duration))

        self.current_recording = cleaned

        # Save recording
        name = f"Recording_{len(self.recordings) + 1}"
        self.recordings[name] = self.current_recording
        self.save_recordings()

    def play_recording(self, name):
        """
        Play a recording by sending the key commands to the robot
        Args:
            name (str): The name of the recording to play
        Returns:
            None
        """
        if name not in self.recordings:
            return

        if not self.is_running:
            self.start()

        while self.node is None:
            time.sleep(0.1)

        print(f"Playing recording: {name}")
        for key, duration in self.recordings[name]:
            print(f"Sending key: {key} for {duration:.2f}s")
            self._send_key_duration(key, duration)
        print("Finished playing recording.")

    def delete_recording(self, name):
        """
        Delete a recording by its name
        Args:
            name (str): The name of the recording to delete
        Returns:
            None
        """
        if name in self.recordings:
            del self.recordings[name]
            self.save_recordings()

    def send_key(self, key, record=True):
        """
        Send a key command to the robot and record it if needed
        Args:
            key (str): The key pressed
            record (bool): Whether to record the key press
        Returns:
            None
        """
        if self.node:
            self.node.send_command(key)

        if key == 'x':
            self.key_held_flag = False
        else:
            self.key_held_flag = True

        if self.recording and record:
            now = time.time()

            if self.last_key is None:
                self.last_key = key
                self.last_time = now

            elif key != self.last_key:
                duration = now - self.last_time
                self._append_action(self.last_key, duration)
                self.last_key = key
                self.last_time = now

    def _start_idle_monitor(self):
        """
        Start a thread to monitor idle time and send 'x' command if idle
        Args:
            None
        Returns:
            None
        """
        self.idle_monitoring = True
        self.idle_thread = threading.Thread(
            target=self._monitor_idle, daemon=True)
        self.idle_thread.start()

    def _stop_idle_monitor(self):
        """
        Stop the idle monitor thread.
        Args:
            None
        Returns:
            None
        """
        self.idle_monitoring = False
        if self.idle_thread:
            self.idle_thread.join()
            self.idle_thread = None

    def _monitor_idle(self):
        """
        Monitor idle time and send 'x' command if idle for too long
        Args:
            None
        Returns:
            None
        """
        while self.idle_monitoring:
            time.sleep(0.05)
            if not self.recording:
                break
            now = time.time()

            # Only send 'x' if no key is currently held
            if not self.key_held_flag and self.last_key is not None and now - self.last_time > 0.3:
                duration = now - self.last_time
                if self.last_key != 'x':
                    self._append_action(self.last_key, duration)
                    self.node.send_command('x')
                    self._append_action('x', 0.1)
                self.last_key = 'x'
                self.last_time = now

    def _append_action(self, key, duration):
        """
        Append an action to the current recording
        Args:
            key (str): The key pressed
            duration (float): The duration for which the key was pressed
        Returns:
            None
        """
        if not self.current_recording:
            self.current_recording.append([key, duration])
            return

        # Merge with the last action if it's the same key
        last_action, _ = self.current_recording[-1]
        if key == last_action:
            self.current_recording[-1][1] += duration
        else:
            self.current_recording.append([key, duration])

    def _send_key_duration(self, key, duration):
        """
        Send a key command for a specified duration
        Args:
            key (str): The key to send
            duration (float): The duration for which to send the key
        Returns:
            None
        """
        start = time.time()
        while time.time() - start < duration:
            self.send_key(key, record=False)
            time.sleep(0.1)
