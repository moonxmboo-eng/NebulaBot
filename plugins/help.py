from nebula.core.message import Message, MessageType
from nebula.core.plugin import BasePlugin


class HelpPlugin(BasePlugin):
    async def handle_message(self, message: Message) -> Message | None:
        if message.content.strip() != "/help":
            return None

        return Message(
            content=(
                "NebulaBot built-in commands:\n"
                "- /help: show command help\n"
                "- /echo <text>: reply with the same text\n"
                "- /persona <style>: set a session persona\n"
                "- /persona clear: clear the persona\n\n"
                "If no provider API key is configured, NebulaBot runs in mock mode."
            ),
            role="assistant",
            type=MessageType.TEXT,
        )

