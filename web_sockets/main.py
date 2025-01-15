from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List
import json
from .schemas import NotificationCount, WSMessage
from naukry.utils.auth import AsyncJWTAuth as auth

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)

    def disconnect(self, websocket: WebSocket, user_id: int):
        if user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

    async def broadcast_to_user(self, message: dict, user_id: int):
        if user_id in self.active_connections:
            disconnected = []
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except WebSocketDisconnect:
                    disconnected.append(connection)
            for conn in disconnected:
                self.active_connections[user_id].remove(conn)

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    try:
        await websocket.accept()
        auth_data = await websocket.receive_json()
        token = auth_data.get("token")
        if not token:
            await websocket.close(code=4001, reason="No token provided")
            return
        try:
            payload = auth(token)
            user = payload.get("user_id")
            if not user:
                await websocket.close(code=4002, reason="Invalid user ID")
                return
            print(user)
            await manager.connect(websocket, user.id)
        except Exception as e:
            await websocket.close(code=4003, reason=str(e))
    except WebSocketDisconnect:
        if 'user_id' in locals():
            manager.disconnect(websocket, user.id)

@app.post("/update_counts")
async def update_counts(
    counts: NotificationCount,
    # auth: HTTPAuthorizationCredentials = Depends(security)
):
    payload = auth(token)
    user = payload.get("user_id")
    message = WSMessage(
        type="counts_update",
        data={
            "notification_count": counts.notification_count,
            "invitation_count": counts.invitation_count
        }
    )
    await manager.broadcast_to_user(message.dict(), user.id)
    print("Working...")