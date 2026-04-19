# NebulaBot 🌌

A modular, extensible AI chatbot framework inspired by AstrBot.

## Features
- **Platform Agnostic**: Easily plug in new IM platforms (Console included).
- **Provider Agnostic**: Support for OpenAI, Gemini, and more.
- **Plugin System**: Drop Python files into `plugins/` to extend functionality.
- **Async First**: Built on top of `asyncio` for high performance.

## Quick Start

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   *(Note: You can also use `uv` or `pip install .` if you have `pyproject.toml` setup)*

2. **Configure environment**:
   Copy `.env.example` to `.env` and add your API keys.

3. **Run**:
   ```bash
   python main.py
   ```

## Creating Plugins

Create a new file in `plugins/` that inherits from `BasePlugin`:

```python
from nebula.core.plugin import BasePlugin
from nebula.core.message import Message

class MyPlugin(BasePlugin):
    async def handle_message(self, message: Message):
        if "hello" in message.content.lower():
            return Message(content="Hi there!", role="assistant")
        return None
```

## License
MIT
