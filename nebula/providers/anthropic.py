import os

from anthropic import AsyncAnthropic
from openai import AsyncOpenAI

from ..core.message import Message, MessageType
from ..core.provider import BaseProvider


class AnthropicProvider(BaseProvider):
    def __init__(
        self,
        api_key: str | None = None,
        model: str = "claude-sonnet-4-20250514",
        base_url: str | None = None,
        api_style: str = "anthropic",
    ):
        super().__init__("claude")
        self.api_key = api_key or os.getenv("CLAUDE_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
        self.model = model
        self.base_url = base_url or None
        self.api_style = api_style
        self.anthropic_client = None
        self.openai_client = None
        if self.api_key:
            if self.api_style == "openai":
                self.openai_client = AsyncOpenAI(
                    api_key=self.api_key,
                    base_url=self.base_url or "https://api.anthropic.com/v1/",
                )
            else:
                kwargs = {"api_key": self.api_key}
                if self.base_url:
                    kwargs["base_url"] = self.base_url
                self.anthropic_client = AsyncAnthropic(**kwargs)

    def is_configured(self) -> bool:
        return bool(self.api_key)

    async def chat(self, messages: list[Message], system_prompt: str | None = None) -> Message:
        if not self.api_key:
            return Message(
                content="Anthropic API key not set.",
                role="assistant",
                type=MessageType.TEXT,
            )

        payload = [
            {"role": message.role, "content": message.content}
            for message in messages
            if message.role in {"user", "assistant"}
        ]

        if not payload:
            payload = [{"role": "user", "content": "Hello"}]

        try:
            if self.api_style == "openai":
                openai_payload = []
                if system_prompt:
                    openai_payload.append({"role": "system", "content": system_prompt})
                openai_payload.extend(payload)
                response = await self.openai_client.chat.completions.create(
                    model=self.model,
                    messages=openai_payload,
                )
                text = response.choices[0].message.content or ""
            else:
                response = await self.anthropic_client.messages.create(
                    model=self.model,
                    max_tokens=1024,
                    system=system_prompt or "",
                    messages=payload,
                )
                blocks = [block.text for block in response.content if getattr(block, "text", None)]
                text = "\n".join(blocks).strip()
            return Message(
                content=text or "(empty Claude response)",
                role="assistant",
                type=MessageType.TEXT,
            )
        except Exception as exc:
            return Message(
                content=f"Error from Claude: {exc}",
                role="assistant",
                type=MessageType.TEXT,
            )
