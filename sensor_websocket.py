# sensor_websocket.py
import asyncio
import websockets
import json
from threading import Thread, Lock

sensor_data = {}
sensor_data_lock = Lock()
websocket_clients = set()


async def sensor_websocket_handler(websocket):
    """
    Handle incoming WebSocket connections and send sensor data to clients
    Args:
        websocket (websockets.WebSocketServerProtocol): The WebSocket connection
    Returns:
        None
    """
    websocket_clients.add(websocket)
    print(f"Client connected: {websocket.remote_address}")
    try:
        while True:
            await asyncio.sleep(1)
            with sensor_data_lock:
                # Filter out disabled sensors and empty values
                filtered_data = {}
                for name, data in sensor_data.items():
                    if data["enabled"] == True and data["value"] != "":
                        filtered_data[name] = data["value"]
                if not filtered_data:
                    continue
                # Send the filtered data to the client
                message = json.dumps(filtered_data)
                await websocket.send(message)

    except websockets.exceptions.ConnectionClosed:
        print(f"Client disconnected: {websocket.remote_address}")
        pass

    finally:
        websocket_clients.remove(websocket)


async def start_server_async(host="localhost", port=6789):
    """
    Start the WebSocket server to handle incoming connections
    Args:
        host (str): The host address for the WebSocket server
        port (int): The port number for the WebSocket server
    Returns:
        None
    """
    async with websockets.serve(sensor_websocket_handler, host, port):
        print(f"WebSocket server started on ws://{host}:{port}")
        await asyncio.Future()


def start_websocket_server(host="localhost", port=6789):
    """
    Start the WebSocket server in a separate thread
    Args:
        host (str): The host address for the WebSocket server
        port (int): The port number for the WebSocket server
    Returns:
        None
    """
    def run():
        """
        Run the WebSocket server in a new event loop.
        Args:
            None
        Returns:
            None
        """
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(start_server_async(host, port))

        except Exception as e:
            print(f"WebSocket crashed: {e}")

    Thread(target=run, daemon=True).start()


def update_sensor_state(sensor_name, enabled, value=""):
    """
    Update the state of a sensor and its value
    Args:
        sensor_name (str): The name of the sensor
        enabled (bool): Whether the sensor is enabled or disabled
        value (str): The value of the sensor
    Returns:
        None
    """
    with sensor_data_lock:
        if enabled:
            sensor_data[sensor_name] = {
                "enabled": True,
                "value": value
            }
        else:
            if sensor_name in sensor_data:
                del sensor_data[sensor_name]
