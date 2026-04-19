import os
from openai import AsyncOpenAI
from ..core.provider import BaseProvider
from ..core.message import Message, MessageType

class OpenAIProvider(BaseProvider):
    def __init__(self, api_key: str = None, model: str = "gpt-3.5-turbo"):
        super().__init__("openai")
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.client = AsyncOpenAI(api_key=self.api_key)

    async def chat(self, messages: list[Message]) -> Message:
        openai_messages = []
        for msg in messages:
            openai_messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=openai_messages
            )
            return Message(
                content=response.choices[0].message.content,
                role="assistant",
                type=MessageType.TEXT
            )
        except Exception as e:
            return Message(
                content=f"Error from OpenAI: {str(e)}",
                role="assistant",
                type=MessageType.TEXT
            )
