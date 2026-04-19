import asyncio
import os
from dotenv import load_dotenv
from nebula.core.bot import NebulaBot
from nebula.platforms.console import ConsolePlatform
from nebula.providers.openai import OpenAIProvider
from nebula.providers.gemini import GeminiProvider

async def main():
    load_dotenv()
    
    bot = NebulaBot()
    
    # 1. Add Platforms
    bot.add_platform(ConsolePlatform())
    
    # 2. Add Providers
    # bot.add_provider(OpenAIProvider(), is_default=True)
    # Using Gemini as default since I can test it more easily or just add both
    bot.add_provider(GeminiProvider(), is_default=True)
    
    # 3. Load Plugins
    bot.load_plugins("plugins")
    
    print("NebulaBot is running...")
    await bot.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBot stopped.")
