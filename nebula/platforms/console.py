import asyncio
import sys
from ..core.platform import BasePlatform
from ..core.message import Message, MessageContext, MessageType

class ConsolePlatform(BasePlatform):
    def __init__(self):
        super().__init__("console")

    async def run(self):
        print("--- Console Platform Started (type 'exit' to quit) ---")
        loop = asyncio.get_event_loop()
        while True:
            # Non-blocking input is tricky in terminal, using run_in_executor
            user_input = await loop.run_in_executor(None, sys.stdin.readline)
            user_input = user_input.strip()
            
            if user_input.lower() == 'exit':
                break
            
            if not user_input:
                continue

            msg = Message(
                content=user_input,
                type=MessageType.TEXT,
                context=MessageContext(
                    platform="console",
                    sender_id="user",
                    session_id="console_session"
                )
            )
            
            if self.on_message_callback:
                await self.on_message_callback(msg)

    async def send(self, message: Message):
        print(f"\n[Bot]: {message.content}\n")
