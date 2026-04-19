from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional

class MessageType(Enum):
    TEXT = "text"
    IMAGE = "image"
    FILE = "file"

@dataclass
class MessageContext:
    platform: str
    sender_id: str
    session_id: str
    raw_event: Any = None
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class Message:
    content: str
    type: MessageType = MessageType.TEXT
    context: Optional[MessageContext] = None
    role: str = "user"  # "user" or "assistant"
