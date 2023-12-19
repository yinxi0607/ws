import requests
from websocket import WebSocketApp
import json


def get_session():
    url = "http://localhost:5022/get_session"  # Replace with your server's address
    headers = {"Content-Type": "application/json"}
    data = {"user_id": 123}  # Replace with your user ID or any relevant data

    response = requests.post(url, headers=headers, json=data)
    session_id = response.json()["session_id"]
    return session_id


def on_message(ws, message):
    print(f"Received message: {message}")


def on_error(ws, error):
    print(f"Error: {error}")


def on_close(ws, close_status_code, close_msg):
    print(f"Closed with status code {close_status_code}: {close_msg}")


def on_open(ws):
    message = "hello world"
    ws.send(message)
    print(f"Sent message: {message}")


if __name__ == "__main__":
    # session_id = get_session()
    session_id = 'user_123_session'
    ws_url = f"ws://localhost:5022/socket.io/?EIO=4&transport=websocket&sid={session_id}"

    ws = WebSocketApp(
        ws_url,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
    )
    ws.on_open = on_open

    ws.run_forever()
