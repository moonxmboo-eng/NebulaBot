from abc import ABC, abstractmethod
from typing import List
from .message import Message

class BaseProvider(ABC):
    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    async def chat(self, messages: List[Message]) -> Message:
        """Process chat messages and return a response"""
        pass
