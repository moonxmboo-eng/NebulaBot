from nebula.core.plugin import BasePlugin
from nebula.core.message import Message, MessageType


class EchoPlugin(BasePlugin):
    async def handle_message(self, message: Message) -> Message | None:
        if message.content.startswith("/echo "):
            echo_text = message.content[6:]
            return Message(
                content=f"Echo: {echo_text}",
                role="assistant",
                type=MessageType.TEXT
            )
        return None
