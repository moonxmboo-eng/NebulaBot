import asyncio
import importlib
import inspect

from .config import AppConfig
from .message import Message
from .plugin import BasePlugin
from .platform import BasePlatform
from .provider import BaseProvider
from .store import ChatStore


class NebulaBot:
    def __init__(self, config: AppConfig):
        self.config = config
        self.store = ChatStore(config.database_path)
        self.plugins: list[BasePlugin] = []
        self.platforms: dict[str, BasePlatform] = {}
        self.providers: dict[str, BaseProvider] = {}
        self.default_provider = config.default_provider

    def add_platform(self, platform: BasePlatform) -> None:
        platform.set_callback(self.process_message)
        self.platforms[platform.name] = platform
        if hasattr(platform, "bind_bot"):
            platform.bind_bot(self)

    def add_provider(self, provider: BaseProvider, is_default: bool = False) -> None:
        self.providers[provider.name] = provider
        if is_default or not self.default_provider:
            self.default_provider = provider.name

    def get_active_provider_name(self) -> str:
        preferred = self.providers.get(self.default_provider)
        if preferred and preferred.is_configured():
            return preferred.name

        for provider in self.providers.values():
            if provider.is_configured():
                return provider.name

        return "mock"

    def load_plugins(self, directory: str) -> None:
        import os

        if not os.path.exists(directory):
            return

        for filename in sorted(os.listdir(directory)):
            if filename.endswith(".py") and not filename.startswith("__"):
                module_name = f"plugins.{filename[:-3]}"
                module = importlib.import_module(module_name)
                for _, obj in inspect.getmembers(module):
                    if (
                        inspect.isclass(obj)
                        and issubclass(obj, BasePlugin)
                        and obj != BasePlugin
                    ):
                        self.plugins.append(obj(name=filename[:-3]))

    def _resolve_provider(self) -> BaseProvider:
        preferred = self.providers.get(self.default_provider)
        if preferred and preferred.is_configured():
            return preferred

        for provider in self.providers.values():
            if provider.is_configured():
                return provider

        return self.providers["mock"]

    async def process_message(self, message: Message) -> Message:
        platform_name = message.context.platform if message.context else "unknown"
        session_id = message.context.session_id if message.context else "default"
        original_content = message.content

        self.store.ensure_session(
            session_id=session_id,
            platform=platform_name,
            title=self._make_session_title(original_content),
        )

        for plugin in self.plugins:
            response = await plugin.handle_message(message)
            if response:
                response.context = message.context
                self.store.add_message(session_id, "user", original_content)
                self.store.add_message(session_id, "assistant", response.content, provider=plugin.name)
                return response

        provider = self._resolve_provider()
        history = self.store.get_recent_messages(session_id=session_id, limit=20)
        response = await provider.chat(
            [*history, message],
            system_prompt=self.config.system_prompt,
        )
        response.context = message.context
        self.store.add_message(session_id, "user", original_content)
        self.store.add_message(session_id, "assistant", response.content, provider=provider.name)
        return response

    def list_sessions(self) -> list[dict]:
        return self.store.list_sessions()

    def get_session_messages(self, session_id: str) -> list[dict]:
        return self.store.get_session_messages(session_id)

    def _make_session_title(self, content: str) -> str:
        compact = " ".join(content.strip().split())
        if not compact:
            return "New Session"
        if compact.startswith("/"):
            return "New Session"
        return compact[:48]

    async def run(self) -> None:
        tasks = [platform.run() for platform in self.platforms.values()]
        await asyncio.gather(*tasks)
