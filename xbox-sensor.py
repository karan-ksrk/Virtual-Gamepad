import websocket
import json
import vgamepad as vg
import queue
import threading
import keyboard
from functools import lru_cache
import time


gamepad = vg.VX360Gamepad()
gamepad_x = 0
gamepad_y = 0

# Message queue for incoming WebSocket messages
message_queue = queue.Queue()
touch_message_queue = queue.Queue()


@lru_cache(maxsize=None)
def control_gamepad(x, y, z):
    x, y, z = (x / 10, y / 10, z / 10)
    x = max(x + 0.12, -0.99)
    # print to two decimal places
    # print(f"x = {x:.2f}, y = {y:.2f}, z={z:.2f}")
    # if y < -0.20:
    # gamepad.left_trigger_float(value_float=(1 - y) / 2)
    # else:
    #     gamepad.right_trigger_float(value_float=y)
    gamepad.left_joystick_float(x_value_float=x, y_value_float=0)
    # gamepad.right_trigger_float(value_float=0)
    gamepad.update()
    # gamepad.left_trigger_float(value_float=0)


@lru_cache(maxsize=None)
def touch_control_keyboard(x, y, action):
    press_s = (action in {"ACTION_DOWN", "ACTION_MOVE"}) and y < 250
    press_w = (action in {"ACTION_DOWN", "ACTION_MOVE"}) and y > 2000

    if press_s:
        keyboard.press("s")
    else:
        keyboard.release("s")

    if press_w:
        keyboard.press("w")
    else:
        keyboard.release("w")

    # print("x = ", x, "y = ", y, "action = ", action)


class Sensor:
    def __init__(self, address, sensor_type):
        self.address = address
        self.sensor_type = sensor_type

    def on_open(self, ws):
        print(f"Connected to : {self.address}")

    def on_message(self, ws, message):
        values = json.loads(message)["values"]
        z = values[0]
        x = values[1]
        y = values[2]
        # print(f"x = {x:.2f}, y = {y:.2f}, z={z:.2f}")
        message_queue.put((x, y, z))

    def on_error(self, ws, error):
        print("Error occurred")
        print(error)

    def on_close(self, ws, close_code, reason):
        print("Connection closed")
        print("Close code:", close_code)
        print("Reason:", reason)

    def make_websocket_connection(self):
        ws = websocket.WebSocketApp(
            f"ws://{self.address}/sensor/connect?type={self.sensor_type}",
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
        )
        ws.run_forever()

    def connect(self):
        thread = threading.Thread(target=self.make_websocket_connection)
        thread.start()


class TouchSensor:
    def __init__(self, address, sensor_type):
        self.address = address
        self.sensor_type = sensor_type

    def on_open(self, ws):
        print(f"Connected to : {self.address}")

    def on_message(self, ws, message):
        data = json.loads(message)

        x, y = data["x"], data["y"]
        action = data["action"]
        touch_message_queue.put((x, y, action))

    def on_error(self, ws, error):
        print("Error occurred")
        print(error)

    def on_close(self, ws, close_code, reason):
        print("Connection closed")
        print("Close code:", close_code)
        print("Reason:", reason)

    def make_websocket_connection(self):
        ws = websocket.WebSocketApp(
            f"ws://{self.address}/{self.sensor_type}",
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
        )
        ws.run_forever()

    def connect(self):
        thread = threading.Thread(target=self.make_websocket_connection)
        thread.start()


# Function to process messages from the queue
def process_messages():
    while True:
        try:
            x, y, z = message_queue.get_nowait()
            control_gamepad(x, y, z)
        except queue.Empty:
            # No items in the queue, sleep briefly to avoid busy-wait
            time.sleep(0.01)


# Function to process touch messages from the queue
def process_touch_messages():
    while True:
        try:
            x, y, action = touch_message_queue.get_nowait()
            touch_control_keyboard(x, y, action)
        except queue.Empty:
            # No items in the queue, sleep briefly to avoid busy-wait
            time.sleep(0.01)


if __name__ == "__main__":
    sensor = Sensor(
        address="192.168.1.4:8080", sensor_type="android.sensor.accelerometer"
    )
    sensor.connect()
    touch_sensor = TouchSensor(address="192.168.1.4:8080", sensor_type="touchscreen")
    touch_sensor.connect()

    # Start the message processing thread
    message_thread = threading.Thread(target=process_messages)
    message_thread.start()

    # start the touchmessage processing thread
    touch_message_thread = threading.Thread(target=process_touch_messages)
    touch_message_thread.start()
