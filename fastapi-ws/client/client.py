import time
import requests
import websockets
import json
import asyncio


async def get_session_id(user_id):
    response = requests.post(f"http://127.0.0.1:8000/get_session")
    data = response.json()
    session_id = data["session_id"]
    print(f"Received session_id: {session_id}")
    return session_id


async def send_message(session_id, message):
    async with websockets.connect(f"ws://127.0.0.1:8000/ws/{session_id}") as ws:
        while True:
            await ws.send(json.dumps({"message": message}))
            print(f"Message sent to server: {message}")
            time.sleep(1)


async def main():
    user_id = "your_user_id"  # 替换为实际的用户ID
    message = "Hello, server!"  # 替换为实际要发送的消息

    session_id = await get_session_id(user_id)
    await send_message(session_id, message)


if __name__ == "__main__":
    asyncio.run(main())
