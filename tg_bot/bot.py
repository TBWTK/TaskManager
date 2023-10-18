from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from .config.config import BOT_TOKEN
from .models.router import init_database

from .handlers.start_handler import start_router
from .handlers.project_handler import project_router
from .handlers.event_handler import event_router
from .handlers.notification_handler import notif_router
from .handlers.helper_handler import helper_router
from .middlewares.scheduler_middleware import SchedulerMiddleware

from .scheduler.scheduler import \
    send_task_notifications_per_day, \
    send_task_notifications_next_day,\
    send_task_notifications_overdue, \
    check_task_overdue


main_menu_commands = [
    BotCommand(command='/start', description='Начать'),
    BotCommand(command='/project', description='Проекты'),
    BotCommand(command='/event', description='Создать событие'),
    BotCommand(command='/help', description='Узнать как работает бот'),
    BotCommand(command='/cancel', description='Если, что-то сломалось'),
]


async def main():
    await init_database()

    bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(start_router)
    dp.include_router(project_router)
    dp.include_router(event_router)
    dp.include_router(notif_router)
    dp.include_router(helper_router)

    scheduler = AsyncIOScheduler(timezone='Europe/Moscow')
    scheduler.add_job(check_task_overdue,
                      'cron', hour=10, minute=19, kwargs={'bot': bot, 'apscheduler': scheduler})
    scheduler.add_job(send_task_notifications_per_day,
                      'cron', hour=10, minute=20, kwargs={'bot': bot, 'apscheduler': scheduler})
    scheduler.add_job(send_task_notifications_next_day,
                      'cron', hour=10, minute=21, kwargs={'bot': bot, 'apscheduler': scheduler})
    scheduler.add_job(send_task_notifications_overdue,
                      'cron', hour=10, minute=22, kwargs={'bot': bot, 'apscheduler': scheduler})
    scheduler.start()

    dp.update.middleware.register(SchedulerMiddleware(scheduler))

    await bot.delete_webhook(drop_pending_updates=True)
    await bot.set_my_commands(main_menu_commands)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
