from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

from .config.config import BOT_TOKEN
from .models.router import init_database
from .handlers.start_handler import start_router


main_menu_commands = [
    BotCommand(command='/start', description='Начать')
]


async def main():
    await init_database()
    bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(start_router)

    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_my_commands(main_menu_commands)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
