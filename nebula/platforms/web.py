from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
import uvicorn

from ..core.config import AppConfig
from ..core.message import Message, MessageContext, MessageType
from ..core.platform import BasePlatform


class ChatRequest(BaseModel):
    session_id: str = Field(..., min_length=1)
    content: str = Field(..., min_length=1)


class SessionCreateResponse(BaseModel):
    session_id: str


class WebPlatform(BasePlatform):
    def __init__(self, config: AppConfig):
        super().__init__("web")
        self.config = config
        self.bot = None
        self.ui_path = Path(__file__).resolve().parent.parent / "ui"
        self.app = FastAPI(title="NebulaBot")
        self.app.mount("/static", StaticFiles(directory=self.ui_path), name="static")
        self._setup_routes()

    def bind_bot(self, bot) -> None:
        self.bot = bot

    def _setup_routes(self) -> None:
        @self.app.get("/")
        async def index() -> FileResponse:
            return FileResponse(self.ui_path / "index.html")

        @self.app.get("/api/health")
        async def health() -> dict:
            provider = self.bot.get_active_provider_name() if self.bot else "unknown"
            return {
                "status": "ok",
                "provider": provider,
                "sessions": len(self.bot.list_sessions()) if self.bot else 0,
            }

        @self.app.get("/api/providers")
        async def providers() -> dict:
            if not self.bot:
                return {"default": "unknown", "providers": []}
            return {
                "default": self.bot.get_active_provider_name(),
                "providers": [
                    {"name": provider.name, "configured": provider.is_configured()}
                    for provider in self.bot.providers.values()
                ],
            }

        @self.app.post("/api/sessions", response_model=SessionCreateResponse)
        async def create_session() -> SessionCreateResponse:
            session_id = f"web-{uuid4().hex[:12]}"
            self.bot.store.ensure_session(session_id=session_id, platform="web", title="New Session")
            return SessionCreateResponse(session_id=session_id)

        @self.app.get("/api/sessions")
        async def list_sessions() -> list[dict]:
            return self.bot.list_sessions() if self.bot else []

        @self.app.get("/api/sessions/{session_id}/messages")
        async def session_messages(session_id: str) -> list[dict]:
            return self.bot.get_session_messages(session_id) if self.bot else []

        @self.app.post("/api/chat")
        async def chat(payload: ChatRequest) -> dict:
            if not self.bot or not self.on_message_callback:
                return {"reply": "NebulaBot is not ready.", "provider": "unavailable"}

            message = Message(
                content=payload.content,
                type=MessageType.TEXT,
                context=MessageContext(
                    platform="web",
                    sender_id="web-user",
                    session_id=payload.session_id,
                ),
            )
            response = await self.on_message_callback(message)
            return {
                "reply": response.content,
                "provider": self.bot.get_active_provider_name(),
                "session_id": payload.session_id,
            }

    async def run(self) -> None:
        config = uvicorn.Config(
            self.app,
            host=self.config.host,
            port=self.config.port,
            log_level="info",
        )
        server = uvicorn.Server(config)
        await server.serve()

    async def send(self, message: Message) -> None:
        return None
