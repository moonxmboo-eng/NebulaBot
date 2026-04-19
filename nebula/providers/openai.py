import os

from .openai_compatible import OpenAICompatibleProvider


class OpenAIProvider(OpenAICompatibleProvider):
    def __init__(self, api_key: str = None, model: str = "gpt-4.1-mini"):
        super().__init__(
            name="openai",
            api_key=api_key or os.getenv("OPENAI_API_KEY"),
            model=model,
        )
