from typing import List, Dict, Any, Optional
from fastapi import WebSocket
import json


class ConnectionManager:
    def __init__(self):
        # Global connections (legacy)
        self.active_connections: List[WebSocket] = []
        # Per-mission connections: mission_id -> [WebSocket, ...]
        self._mission_connections: Dict[int, List[WebSocket]] = {}

    # ── Global (legacy) ───────────────────────────────────────────────────────
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: Dict[str, Any]):
        for connection in list(self.active_connections):
            try:
                await connection.send_json(message)
            except Exception:
                pass

    # ── Per-mission (new) ─────────────────────────────────────────────────────
    async def connect_mission(self, mission_id: int, websocket: WebSocket):
        await websocket.accept()
        if mission_id not in self._mission_connections:
            self._mission_connections[mission_id] = []
        self._mission_connections[mission_id].append(websocket)

    def disconnect_mission(self, mission_id: int, websocket: WebSocket):
        if mission_id in self._mission_connections:
            conns = self._mission_connections[mission_id]
            if websocket in conns:
                conns.remove(websocket)
            if not conns:
                del self._mission_connections[mission_id]

    async def broadcast_to(self, mission_id: int, message: Dict[str, Any]):
        """Push a message to all subscribers of a specific mission."""
        # Also fan-out to global connections (e.g. legacy TaskCenter)
        for connection in list(self.active_connections):
            try:
                await connection.send_json(message)
            except Exception:
                pass
        # Per-mission subscribers
        for connection in list(self._mission_connections.get(mission_id, [])):
            try:
                await connection.send_json(message)
            except Exception:
                pass


manager = ConnectionManager()
