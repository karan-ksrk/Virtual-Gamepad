import websocket
import json
import vgamepad as vg
import queue
import threading

gamepad = vg.VX360Gamepad()
gamepad_x = 0
gamepad_y = 0

# Message queue for incoming WebSocket messages
message_queue = queue.Queue()
touch_message_queue = queue.Queue()

# Calibration values
X_CALIBRATION = 0.12
Y_THRESHOLD_LOW = 250
Y_THRESHOLD_HIGH = 2000


def control_gamepad(x, y, z):
    x /= 10
    y /= 10
    x = max(x + X_CALIBRATION, -0.99)

    gamepad.left_joystick_float(x_value_float=x, y_value_float=0)
    gamepad.update()


def touch_control_keyboard(x, y, action):
    if action in ["ACTION_DOWN", "ACTION_MOVE"]:
        if Y_THRESHOLD_LOW <= y <= Y_THRESHOLD_HIGH:
            pass
        elif y < Y_THRESHOLD_LOW:
            gamepad.left_trigger_float(value_float=1)
        elif y > Y_THRESHOLD_HIGH:
            gamepad.right_trigger_float(value_float=1)
    elif action == "ACTION_UP":
        gamepad.left_trigger_float(value_float=0)
        gamepad.right_trigger_float(value_float=0)


class Sensor:
    def __init__(self, address, sensor_type):
        self.address = address
        self.sensor_type = sensor_type

    def on_open(self, ws):
        print(f"Connected to: {self.address}")

    def on_message(self, ws, message):
        values = json.loads(message)["values"]
        x, y, z = values[1], values[2], values[0]
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
        print(f"Connected to: {self.address}")

    def on_message(self, ws, message):
        data = json.loads(message)
        x, y, action = data["x"], data["y"], data["action"]
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
        x, y, z = message_queue.get()
        control_gamepad(x, y, z)


# Function to process touch messages from the queue
def process_touch_messages():
    while True:
        x, y, action = touch_message_queue.get()
        touch_control_keyboard(x, y, action)


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
