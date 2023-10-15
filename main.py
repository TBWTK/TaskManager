import asyncio
import logging
from tg_bot.bot import main

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
