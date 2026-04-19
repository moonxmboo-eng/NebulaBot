from abc import ABC, abstractmethod
from typing import Optional
from .message import Message

class BasePlugin(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    async def handle_message(self, message: Message) -> Optional[Message]:
        """Handle incoming message. Return a response Message or None to continue chain."""
        pass
