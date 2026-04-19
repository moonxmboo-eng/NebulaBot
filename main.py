import asyncio
import os
from dotenv import load_dotenv
from nebula.core.bot import NebulaBot
from nebula.platforms.web import WebPlatform
from nebula.providers.gemini import GeminiProvider

async def main():
    load_dotenv()
    
    bot = NebulaBot()
    
    # 1. Add Platforms
    web_platform = WebPlatform(port=8000)
    bot.add_platform(web_platform)
    
    # 2. Add Providers
    bot.add_provider(GeminiProvider(), is_default=True)
    
    # 3. Load Plugins
    bot.load_plugins("plugins")
    
    print("NebulaBot Web UI is starting...")
    await bot.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nBot stopped.")
