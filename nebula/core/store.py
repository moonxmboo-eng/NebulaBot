from __future__ import annotations

from datetime import datetime
from pathlib import Path
import sqlite3
from threading import Lock

from .message import Message, MessageContext, MessageType


class ChatStore:
    def __init__(self, database_path: str):
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(self.database_path, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        self.lock = Lock()
        self._init_schema()

    def _init_schema(self) -> None:
        with self.lock:
            self.connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    platform TEXT NOT NULL,
                    title TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    provider TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(session_id) REFERENCES sessions(session_id)
                );
                """
            )
            self.connection.commit()

    def ensure_session(self, session_id: str, platform: str, title: str | None = None) -> None:
        now = datetime.utcnow().isoformat()
        session_title = title or f"{platform}:{session_id}"
        with self.lock:
            self.connection.execute(
                """
                INSERT INTO sessions (session_id, platform, title, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(session_id) DO UPDATE SET
                    platform = excluded.platform,
                    updated_at = excluded.updated_at,
                    title = CASE
                        WHEN sessions.title IS NULL
                            OR sessions.title = ''
                            OR sessions.title = 'New Session'
                        THEN excluded.title
                        ELSE sessions.title
                    END
                """,
                (session_id, platform, session_title, now, now),
            )
            self.connection.commit()

    def touch_session(self, session_id: str) -> None:
        with self.lock:
            self.connection.execute(
                "UPDATE sessions SET updated_at = ? WHERE session_id = ?",
                (datetime.utcnow().isoformat(), session_id),
            )
            self.connection.commit()

    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        provider: str | None = None,
    ) -> None:
        now = datetime.utcnow().isoformat()
        with self.lock:
            self.connection.execute(
                """
                INSERT INTO messages (session_id, role, content, provider, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (session_id, role, content, provider, now),
            )
            self.connection.execute(
                "UPDATE sessions SET updated_at = ? WHERE session_id = ?",
                (now, session_id),
            )
            self.connection.commit()

    def get_recent_messages(self, session_id: str, limit: int = 20) -> list[Message]:
        with self.lock:
            rows = self.connection.execute(
                """
                SELECT role, content, created_at
                FROM messages
                WHERE session_id = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (session_id, limit),
            ).fetchall()

        messages: list[Message] = []
        for row in reversed(rows):
            messages.append(
                Message(
                    content=row["content"],
                    role=row["role"],
                    type=MessageType.TEXT,
                    context=MessageContext(
                        platform="history",
                        sender_id=row["role"],
                        session_id=session_id,
                        raw_event=None,
                    ),
                )
            )
        return messages

    def list_sessions(self, limit: int = 50) -> list[dict]:
        with self.lock:
            rows = self.connection.execute(
                """
                SELECT
                    s.session_id,
                    s.platform,
                    s.title,
                    s.created_at,
                    s.updated_at,
                    COUNT(m.id) AS message_count
                FROM sessions s
                LEFT JOIN messages m ON m.session_id = s.session_id
                GROUP BY s.session_id
                ORDER BY s.updated_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [dict(row) for row in rows]

    def get_session_messages(self, session_id: str, limit: int = 100) -> list[dict]:
        with self.lock:
            rows = self.connection.execute(
                """
                SELECT role, content, provider, created_at
                FROM messages
                WHERE session_id = ?
                ORDER BY id ASC
                LIMIT ?
                """,
                (session_id, limit),
            ).fetchall()
        return [dict(row) for row in rows]
