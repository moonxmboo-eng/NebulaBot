from openai import AsyncOpenAI

from ..core.message import Message, MessageType
from ..core.provider import BaseProvider


class OpenAICompatibleProvider(BaseProvider):
    def __init__(
        self,
        name: str,
        api_key: str | None,
        model: str,
        base_url: str | None = None,
    ):
        super().__init__(name)
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url) if api_key else None

    def is_configured(self) -> bool:
        return bool(self.api_key)

    async def chat(self, messages: list[Message], system_prompt: str | None = None) -> Message:
        if not self.client:
            return Message(
                content=f"{self.name} API key not set.",
                role="assistant",
                type=MessageType.TEXT,
            )

        payload = []
        if system_prompt:
            payload.append({"role": "system", "content": system_prompt})
        for message in messages:
            payload.append({"role": message.role, "content": message.content})

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=payload,
            )
            return Message(
                content=response.choices[0].message.content or "",
                role="assistant",
                type=MessageType.TEXT,
            )
        except Exception as exc:
            return Message(
                content=f"Error from {self.name}: {exc}",
                role="assistant",
                type=MessageType.TEXT,
            )

