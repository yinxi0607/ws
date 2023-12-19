import uuid
from fastapi import FastAPI, WebSocket
from starlette.websockets import WebSocketDisconnect

app = FastAPI()

# 还有问题

class SessionManager:
    def __init__(self):
        self.sessions = {}

    def generate_session_id(self, user_id):
        # 在实际应用中，你可能需要使用更复杂的算法生成 session id
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = user_id
        return session_id

    def get_user_id_by_session_id(self, session_id):
        return self.sessions.get(session_id)

    def remove_session(self, session_id):
        if session_id in self.sessions:
            del self.sessions[session_id]


session_manager = SessionManager()


# 获取 session 的 HTTP 服务
@app.post("/get_session")
async def post_session():
    user_id = "your_user_id"
    session_id = session_manager.generate_session_id(user_id)
    return {"session_id": session_id}


# WebSocket 服务
class WebSocketManager:
    def __init__(self):
        self.connections = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.connections[session_id] = websocket

    def disconnect(self, session_id: str):
        if session_id in self.connections:
            del self.connections[session_id]

    async def send_message(self, session_id: str, message: str):
        if session_id in self.connections:
            websocket = self.connections[session_id]
            await websocket.send_text(message)


websocket_manager = WebSocketManager()


@app.websocket("/ws/{session_id}")
async def websocket_endpoint(
        websocket: WebSocket,
        session_id: str,
):
    await websocket_manager.connect(websocket, session_id)
    try:
        while True:
            data = await websocket.receive_text()
            print(f"Received message from session {session_id}: {data}")
    except WebSocketDisconnect:
        websocket_manager.disconnect(session_id)


# 启动 FastAPI 服务
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
