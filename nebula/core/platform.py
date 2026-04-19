from abc import ABC, abstractmethod
from typing import Awaitable, Callable, Optional

from .message import Message


class BasePlatform(ABC):
    def __init__(self, name: str):
        self.name = name
        self.on_message_callback: Optional[Callable[[Message], Awaitable[Message]]] = None

    def set_callback(self, callback: Callable[[Message], Awaitable[Message]]) -> None:
        self.on_message_callback = callback

    @abstractmethod
    async def run(self) -> None:
        """Start the platform listener"""
        raise NotImplementedError

    @abstractmethod
    async def send(self, message: Message) -> None:
        """Send a message back to the platform"""
        raise NotImplementedError
