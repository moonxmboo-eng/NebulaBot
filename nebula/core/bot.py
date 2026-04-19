import asyncio
import importlib
import inspect
import os
from typing import List, Dict, Type
from .message import Message
from .plugin import BasePlugin
from .platform import BasePlatform
from .provider import BaseProvider

class NebulaBot:
    def __init__(self):
        self.plugins: List[BasePlugin] = []
        self.platforms: Dict[str, BasePlatform] = {}
        self.providers: Dict[str, BaseProvider] = {}
        self.default_provider: str = ""

    def add_platform(self, platform: BasePlatform):
        platform.set_callback(self.on_message)
        self.platforms[platform.name] = platform

    def add_provider(self, provider: BaseProvider, is_default: bool = False):
        self.providers[provider.name] = provider
        if is_default or not self.default_provider:
            self.default_provider = provider.name

    def load_plugins(self, directory: str):
        if not os.path.exists(directory):
            return

        for filename in os.listdir(directory):
            if filename.endswith(".py") and not filename.startswith("__"):
                module_name = f"plugins.{filename[:-3]}"
                module = importlib.import_module(module_name)
                for name, obj in inspect.getmembers(module):
                    if (
                        inspect.isclass(obj) 
                        and issubclass(obj, BasePlugin) 
                        and obj != BasePlugin
                    ):
                        self.plugins.append(obj(name=filename[:-3]))

    async def on_message(self, message: Message):
        # 1. Process plugins
        for plugin in self.plugins:
            response = await plugin.handle_message(message)
            if response:
                await self.send_response(message, response)
                return

        # 2. If no plugin handled it, use default LLM provider
        if self.default_provider:
            provider = self.providers[self.default_provider]
            response = await provider.chat([message])
            await self.send_response(message, response)

    async def send_response(self, original_message: Message, response: Message):
        if original_message.context and original_message.context.platform in self.platforms:
            platform = self.platforms[original_message.context.platform]
            await platform.send(response)

    async def run(self):
        tasks = [platform.run() for platform in self.platforms.values()]
        await asyncio.gather(*tasks)
