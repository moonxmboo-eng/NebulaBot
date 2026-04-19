# NebulaBot

NebulaBot is an AstrBot-style chatbot infrastructure MVP: a single-repo project with Web Chat, REST API, provider abstraction, plugin commands, and SQLite session memory.

## What It Includes

- Web chat UI with session sidebar and persistent conversation history
- REST API for health, sessions, messages, and chat
- Provider routing for `OpenAI`, `Gemini`, `Qwen / 百炼`, `智谱 GLM`, `Claude`, and a built-in `mock` provider
- Plugin system with built-in `/help`, `/echo`, and `/persona` commands
- SQLite-backed session/message storage for replayable conversations
- Optional console platform for local terminal chat

## Quick Start

1. Create a virtual environment and install dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Copy the environment template:

```bash
cp .env.example .env
```

3. Start NebulaBot:

```bash
python main.py
```

4. Open `http://localhost:8000`

## Environment

Default mode is `mock`, so the project works even without an API key.

```env
NEBULA_PROVIDER=mock
OPENAI_API_KEY=
GEMINI_API_KEY=
```

To use a live provider:

```env
NEBULA_PROVIDER=openai
OPENAI_API_KEY=your_key
OPENAI_MODEL=gpt-4.1-mini
```

or

```env
NEBULA_PROVIDER=gemini
GEMINI_API_KEY=your_key
GEMINI_MODEL=gemini-1.5-flash
```

or

```env
NEBULA_PROVIDER=qwen
QWEN_API_KEY=your_key
QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
QWEN_MODEL=qwen-plus
```

or

```env
NEBULA_PROVIDER=zhipu
ZHIPU_API_KEY=your_key
ZHIPU_BASE_URL=https://open.bigmodel.cn/api/paas/v4
ZHIPU_MODEL=glm-5.1
```

or

```env
NEBULA_PROVIDER=claude
CLAUDE_API_KEY=your_key
CLAUDE_MODEL=claude-sonnet-4-20250514
CLAUDE_API_STYLE=anthropic
```

If you use a relay for Claude:

```env
NEBULA_PROVIDER=claude
CLAUDE_API_KEY=your_key
CLAUDE_MODEL=claude-sonnet-4-20250514
CLAUDE_API_STYLE=openai
CLAUDE_BASE_URL=https://your-relay.example/v1
```

## API

- `GET /api/health`
- `GET /api/providers`
- `POST /api/sessions`
- `GET /api/sessions`
- `GET /api/sessions/{session_id}/messages`
- `POST /api/chat`

Example:

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id":"web-demo","content":"hello"}'
```

## Plugins

Drop new Python modules into `plugins/` and subclass `BasePlugin`.

```python
from nebula.core.message import Message
from nebula.core.plugin import BasePlugin


class MyPlugin(BasePlugin):
    async def handle_message(self, message: Message) -> Message | None:
        if message.content == "/ping":
            return Message(content="pong", role="assistant")
        return None
```

## Notes

- This is deliberately smaller than AstrBot, but the architecture is aligned: pluggable providers, pluggable interaction surfaces, persistent sessions, and command-style extensions.
- The `mock` provider keeps the project demoable on a fresh machine.
