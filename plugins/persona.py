from typing import Optional

from nebula.core.plugin import BasePlugin
from nebula.core.message import Message, MessageType


class PersonaPlugin(BasePlugin):
    def __init__(self, name: str):
        super().__init__(name)
        # Store persona per session_id (simplified)
        self.session_personas = {}

    async def handle_message(self, message: Message) -> Optional[Message]:
        session_id = message.context.session_id if message.context else "default"

        # Handle command
        if message.content.startswith("/persona "):
            persona = message.content[9:].strip()
            if persona.lower() in ['clear', 'none']:
                if session_id in self.session_personas:
                    del self.session_personas[session_id]
                return Message(content="Persona cleared.", role="assistant", type=MessageType.TEXT)
            
            self.session_personas[session_id] = persona
            return Message(
                content=f"Persona set to: {persona}",
                role="assistant",
                type=MessageType.TEXT
            )
            
        # If not a command, prepend the persona to the content if it exists
        if session_id in self.session_personas:
            persona = self.session_personas[session_id]
            # In a real app, this should be an actual system prompt.
            # Here we just inject it into the user's message as a quick hack
            # to let the LLM know about the persona.
            original_content = message.content
            message.content = (
                f"System Instruction: You must act as {persona}. "
                f"User says: {original_content}"
            )

        # Return None to let the message continue to the provider
        return None
