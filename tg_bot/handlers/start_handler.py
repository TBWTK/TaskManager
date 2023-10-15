from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.types import Message
from aiogram.fsm.state import default_state
from aiogram.fsm.context import FSMContext

from tg_bot.states.start_state import FSMFillFormName
from tg_bot.services.start_service import create_user


start_router = Router()


@start_router.message(Command("start"), StateFilter(default_state))
async def start_handler(msg: Message, state: FSMContext):
    if msg.chat.type == 'private':
        if await create_user(msg.from_user.id, msg.from_user.username):
            await msg.answer("Регистрируем ваш аккаунт в система бота")
            await msg.answer("Для того, чтобы узнать как работает этот бот"
                             "Введите команду /help")
        else:
            await msg.answer("Вы уже зарегистрированы в система бота")
