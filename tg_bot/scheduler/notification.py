from aiogram import Bot
from tg_bot.keyboards.notification_keyboards import question_implementation
from tg_bot.services.notification_services import update_event


async def send_message_question_implementation(bot: Bot, chat_id: int, text: str, event_id: int):
    await bot.send_message(chat_id, f'{text}\n\nЗадача выполнена?', reply_markup=question_implementation(event_id))


async def send_message_event(bot: Bot, chat_id: int, text: str, event_id: int):
    await bot.send_message(chat_id, f'{text}')
    await update_event(event_id)

