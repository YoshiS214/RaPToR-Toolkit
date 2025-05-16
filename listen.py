# listen.py
import asyncio
import websockets
import json


async def listen_to_sensors(uri="ws://localhost:6789"):
    """
    Listen to sensor updates from a WebSocket server
    Args:
        uri (str): The WebSocket server URI
    Returns:
        None
    """
    try:
        async with websockets.connect(uri) as websocket:
            print(f"Connected to {uri}")
            while True:
                message = await websocket.recv()
                try:
                    data = json.loads(message)
                    print("Sensor Update:", json.dumps(data, indent=2))
                except json.JSONDecodeError:
                    print("Received non-JSON message:", message)
    except Exception as e:
        print(f"Connection error: {e}")

if __name__ == "__main__":
    # This will start the webSocket listener and keep displaying sensor updates
    asyncio.run(listen_to_sensors())
