from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException,APIRouter
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List
import json
from .schemas import NotificationCount, WSMessage
from naukry.utils.auth import AsyncJWTAuth as auth
from user.models import *
import jwt
from django.conf import settings

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)

    def disconnect(self, websocket: WebSocket, user_id: int):
        if user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

    async def broadcast_to_user(self, message: dict, user_id: int):
        print("SUCESSSSSSS.....")
        if user_id in self.active_connections:
            disconnected = []
            for connection in self.active_connections[user_id]:
                try:
                    print("SUCESSSSSSS.....", connection)
                    await connection.send_json(message)
                except WebSocketDisconnect:
                    disconnected.append(connection)
            for conn in disconnected:
                self.active_connections[user_id].remove(conn)

manager = ConnectionManager()

async def authenticate_user(token):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        user_id = payload.get('user_id')
        if user_id and await UserProfile.objects.filter(id=user_id).aexists():
            user = await UserProfile.objects.aget(id=user_id)
            return user
        return None
    except jwt.ExpiredSignatureError:
        return None
    except Exception as e:
        return None

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    try:
        await websocket.accept()
        token = websocket.headers.get("Authorization")
        if not token:
            print("No token in headers")
            await websocket.close(code=4001, reason="No token provided in headers")
            return
        try:
            token = token.replace("Bearer ", "").strip()
            user = await authenticate_user(token)
            if not user:
                print("No user found")
                await websocket.close(code=4002, reason="Invalid user ID")
                return
            await manager.connect(websocket, user.id)
            try:
                while True:
                    await websocket.receive_text()
            except WebSocketDisconnect:
                manager.disconnect(websocket, user.id)
        except Exception as e:
            print(e)
            await websocket.close(code=4003, reason=str(e))
    except WebSocketDisconnect:
        if 'user_id' in locals():
            manager.disconnect(websocket, user.id)