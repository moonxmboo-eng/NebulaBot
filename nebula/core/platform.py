from abc import ABC, abstractmethod
from typing import Callable, Awaitable
from .message import Message

class BasePlatform(ABC):
    def __init__(self, name: str):
        self.name = name
        self.on_message_callback: Optional[Callable[[Message], Awaitable[None]]] = None

    def set_callback(self, callback: Callable[[Message], Awaitable[None]]):
        self.on_message_callback = callback

    @abstractmethod
    async def run(self):
        """Start the platform listener"""
        pass

    @abstractmethod
    async def send(self, message: Message):
        """Send a message back to the platform"""
        pass
