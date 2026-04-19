import os

import google.generativeai as genai

from ..core.message import Message, MessageType
from ..core.provider import BaseProvider


class GeminiProvider(BaseProvider):
    def __init__(self, api_key: str = None, model: str = "gemini-1.5-flash"):
        super().__init__("gemini")
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)
        self.model_name = model

    def is_configured(self) -> bool:
        return bool(self.api_key)

    async def chat(self, messages: list[Message], system_prompt: str | None = None) -> Message:
        if not self.api_key:
            return Message(content="Gemini API Key not set.", role="assistant")

        model = genai.GenerativeModel(self.model_name)
        try:
            prompt_lines: list[str] = []
            if system_prompt:
                prompt_lines.append(f"System: {system_prompt}")
            for item in messages[-20:]:
                prompt_lines.append(f"{item.role.title()}: {item.content}")
            prompt_lines.append("Assistant:")
            response = await model.generate_content_async("\n\n".join(prompt_lines))
            return Message(
                content=response.text,
                role="assistant",
                type=MessageType.TEXT
            )
        except Exception as e:
            return Message(
                content=f"Error from Gemini: {str(e)}",
                role="assistant",
                type=MessageType.TEXT
            )
