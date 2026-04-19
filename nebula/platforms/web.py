import asyncio
from typing import List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn
import os

from ..core.platform import BasePlatform
from ..core.message import Message, MessageContext, MessageType

class WebPlatform(BasePlatform):
    def __init__(self, port: int = 8000):
        super().__init__("web")
        self.port = port
        self.app = FastAPI(title="NebulaBot Web UI")
        self.active_connections: List[WebSocket] = []
        self._setup_routes()

    def _setup_routes(self):
        ui_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ui")
        
        # Serve static files for CSS/JS
        self.app.mount("/static", StaticFiles(directory=ui_path), name="static")

        @self.app.get("/")
        async def get_index():
            return FileResponse(os.path.join(ui_path, "index.html"))

        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            await websocket.accept()
            self.active_connections.append(websocket)
            try:
                while True:
                    data = await websocket.receive_text()
                    msg = Message(
                        content=data,
                        type=MessageType.TEXT,
                        context=MessageContext(
                            platform="web",
                            sender_id="web_user",
                            session_id="web_session",
                            raw_event=websocket
                        )
                    )
                    if self.on_message_callback:
                        await self.on_message_callback(msg)
            except WebSocketDisconnect:
                self.active_connections.remove(websocket)
            except Exception as e:
                print(f"WebSocket Error: {e}")
                if websocket in self.active_connections:
                    self.active_connections.remove(websocket)

    async def run(self):
        print(f"--- Web Platform starting at http://localhost:{self.port} ---")
        config = uvicorn.Config(self.app, host="0.0.0.0", port=self.port, log_level="info")
        server = uvicorn.Server(config)
        await server.serve()

    async def send(self, message: Message):
        # We need to find the websocket to send the response back
        # In a real app, you map session_id to websockets.
        # For simplicity, we broadcast to all or find from context
        
        target_ws = None
        if message.context and message.context.raw_event:
            target_ws = message.context.raw_event
            
        if target_ws and target_ws in self.active_connections:
            await target_ws.send_text(message.content)
        else:
            # Broadcast if we can't find specific target
            for ws in self.active_connections:
                try:
                    await ws.send_text(message.content)
                except Exception:
                    pass
