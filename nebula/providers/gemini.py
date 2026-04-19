import os
import google.generativeai as genai
from ..core.provider import BaseProvider
from ..core.message import Message, MessageType

class GeminiProvider(BaseProvider):
    def __init__(self, api_key: str = None, model: str = "gemini-1.5-flash"):
        super().__init__("gemini")
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)
        self.model_name = model

    async def chat(self, messages: list[Message]) -> Message:
        if not self.api_key:
            return Message(content="Gemini API Key not set.", role="assistant")
            
        model = genai.GenerativeModel(self.model_name)
        # Simplified history handling
        chat = model.start_chat(history=[])
        try:
            # We just send the last message for now as a simple example
            response = await model.generate_content_async(messages[-1].content)
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
