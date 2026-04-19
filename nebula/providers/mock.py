from ..core.message import Message, MessageType
from ..core.provider import BaseProvider


class MockProvider(BaseProvider):
    def __init__(self):
        super().__init__("mock")

    async def chat(self, messages: list[Message], system_prompt: str | None = None) -> Message:
        latest = messages[-1].content if messages else ""
        prompt_hint = (
            "Mock provider active. Configure OpenAI, Gemini, Qwen, Zhipu, or Claude "
            "credentials for live model replies."
        )
        response = (
            f"{prompt_hint}\n\n"
            f"You said: {latest}\n\n"
            "Available built-in commands:\n"
            "- /help\n"
            "- /echo <text>\n"
            "- /persona <style>\n"
            "- /persona clear"
        )
        return Message(content=response, role="assistant", type=MessageType.TEXT)
