from abc import ABC, abstractmethod
from typing import List

from .message import Message


class BaseProvider(ABC):
    def __init__(self, name: str):
        self.name = name

    def is_configured(self) -> bool:
        return True

    @abstractmethod
    async def chat(self, messages: List[Message], system_prompt: str | None = None) -> Message:
        """Process chat messages and return a response"""
        raise NotImplementedError
