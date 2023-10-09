import websocket
import json


speed = 1.3

old_x = 0
old_y = 0


def on_message(ws, message):
    global old_x
    global old_y

    data = json.loads(message)

    new_x, new_y = data["x"], data["y"]
    action = data["action"]
    print("new_x = ", new_x, "new_y = ", new_y, "action = ", action)


def on_error(ws, error):
    print(error)


def on_close(ws, close_code, reason):
    print("connection close : ", reason)


def on_open(ws):
    print("connected")


def connect(url):
    ws = websocket.WebSocketApp(
        url,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
    )

    ws.run_forever()


connect("ws://192.168.1.4:8080/touchscreen")
