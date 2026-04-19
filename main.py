import asyncio
import os

from dotenv import load_dotenv

from nebula.core.bot import NebulaBot
from nebula.core.config import AppConfig
from nebula.platforms.console import ConsolePlatform
from nebula.platforms.web import WebPlatform
from nebula.providers.anthropic import AnthropicProvider
from nebula.providers.gemini import GeminiProvider
from nebula.providers.mock import MockProvider
from nebula.providers.openai_compatible import OpenAICompatibleProvider
from nebula.providers.openai import OpenAIProvider


async def main() -> None:
    load_dotenv()
    config = AppConfig.from_env()

    bot = NebulaBot(config=config)
    bot.add_provider(MockProvider(), is_default=config.default_provider == "mock")
    bot.add_provider(OpenAIProvider(model=config.openai_model), is_default=config.default_provider == "openai")
    bot.add_provider(GeminiProvider(model=config.gemini_model), is_default=config.default_provider == "gemini")
    bot.add_provider(
        OpenAICompatibleProvider(
            name="qwen",
            api_key=os.getenv("QWEN_API_KEY") or os.getenv("DASHSCOPE_API_KEY"),
            model=config.qwen_model,
            base_url=config.qwen_base_url,
        ),
        is_default=config.default_provider == "qwen",
    )
    bot.add_provider(
        OpenAICompatibleProvider(
            name="zhipu",
            api_key=os.getenv("ZHIPU_API_KEY"),
            model=config.zhipu_model,
            base_url=config.zhipu_base_url,
        ),
        is_default=config.default_provider == "zhipu",
    )
    bot.add_provider(
        AnthropicProvider(
            api_key=os.getenv("CLAUDE_API_KEY") or os.getenv("ANTHROPIC_API_KEY"),
            model=config.claude_model,
            base_url=config.claude_base_url,
            api_style=config.claude_api_style,
        ),
        is_default=config.default_provider in {"claude", "anthropic"},
    )

    web_platform = WebPlatform(config=config)
    bot.add_platform(web_platform)

    if config.enable_console:
        bot.add_platform(ConsolePlatform())

    bot.load_plugins("plugins")

    print(f"NebulaBot starting on http://{config.host}:{config.port}")
    print(f"Active default provider: {bot.get_active_provider_name()}")
    await bot.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nNebulaBot stopped.")
