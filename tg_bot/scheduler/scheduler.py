from datetime import datetime, timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from .notification import send_message_question_implementation, send_message_event
from aiogram import Bot
from tg_bot.services.base_service import get_task_per_day, get_task_next_day, get_task_overdue, get_event_data, \
    calculate_time_hour_reminder_timedelta, preparation_text_notification
from ..services.notification_services import update_overdue


async def send_task_notifications_per_day(bot: Bot, apscheduler: AsyncIOScheduler):
    event_per_day = await get_task_per_day()
    for event in event_per_day:
        event_dict = await get_event_data(event)
        prepare_event = preparation_text_notification(event_dict, "check_ex")
        seconds = await calculate_time_hour_reminder_timedelta(event.time_event)

        if event_dict['is_task']:
            apscheduler.add_job(send_message_question_implementation, trigger='date',
                                run_date=datetime.now() + timedelta(seconds=seconds),
                                kwargs={'bot': bot,
                                        'chat_id': prepare_event['chat_id'],
                                        'text': prepare_event['text'],
                                        'event_id': event.id})
        else:
            apscheduler.add_job(send_message_event, trigger='date',
                                run_date=datetime.now() + timedelta(seconds=seconds),
                                kwargs={'bot': bot,
                                        'chat_id': prepare_event['chat_id'],
                                        'text': prepare_event['text'],
                                        'event_id': event.id})


async def send_task_notifications_next_day(bot: Bot, apscheduler: AsyncIOScheduler):
    event_next_day = await get_task_next_day()
    for event in event_next_day:
        event_dict = await get_event_data(event)
        prepare_event = preparation_text_notification(event_dict, "check_ex")
        seconds = await calculate_time_hour_reminder_timedelta(event.time_event)

        apscheduler.add_job(send_message_question_implementation, trigger='date',
                            run_date=datetime.now() + timedelta(seconds=seconds),
                            kwargs={'bot': bot,
                                    'chat_id': prepare_event['chat_id'],
                                    'text': prepare_event['text'],
                                    'event_id': event.id})


async def check_task_overdue(bot: Bot, apscheduler: AsyncIOScheduler):
    await update_overdue()


async def send_task_notifications_overdue(bot: Bot, apscheduler: AsyncIOScheduler):
    event_overdue = await get_task_overdue()
    for event in event_overdue:
        event_dict = await get_event_data(event)
        prepare_event = preparation_text_notification(event_dict, "overdue")
        seconds = await calculate_time_hour_reminder_timedelta(event.time_event)

        apscheduler.add_job(send_message_question_implementation, trigger='date',
                            run_date=datetime.now() + timedelta(seconds=seconds),
                            kwargs={'bot': bot,
                                    'chat_id': prepare_event['chat_id'],
                                    'text': f"{prepare_event['text']}\n\n<b>ЗАДАЧА ПРОСРОЧЕНА!</b>",
                                    'event_id': event.id})
