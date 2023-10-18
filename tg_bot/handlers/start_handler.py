from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.state import default_state
from aiogram.fsm.context import FSMContext

from tg_bot.states.start_state import FSMFillFormName
from tg_bot.services.start_service import create_user, check_user_from_project, add_user_name, update_status


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
        data = msg.text.split(' ')[1] if len(msg.text.split(' ')) > 1 else None
        if data is not None:
            project_chat_id, flag = data.split("_")
            if await check_user_from_project(msg.from_user.id, project_chat_id):
                await msg.answer("Вы добавлены в проект!\n"
                                 "<b>Для дальнейшего участия, вам необходимо ввести свои данные</b>")
                await msg.answer("Введите имя:")
                await state.update_data(project_chat_id=project_chat_id)
                await state.set_state(FSMFillFormName.first_name)
            elif await update_status(msg.from_user.id, project_chat_id, flag):
                await msg.answer("Обновляем ваш статус\n\nВведите имя:")
                await state.update_data(project_chat_id=project_chat_id)
                await state.set_state(FSMFillFormName.first_name)
            else:
                await msg.answer("Вы уже участвуете в проекте!")
    else:
        await msg.answer("Команда выполняется в личных сообщениях")


@start_router.message(StateFilter(FSMFillFormName.first_name), F.text.isalpha())
async def process_first_name_sent(msg: Message, state: FSMContext):
    await state.update_data(first_name=msg.text)
    await msg.answer("Теперь введите вашу фамилию")
    await state.set_state(FSMFillFormName.last_name)


@start_router.message(StateFilter(FSMFillFormName.first_name))
async def warning_not_first_name(message: Message):
    await message.answer(
        text='Введенные вами данные не являются именем\n'
             'Не используйте цифры, пробелы и точки!\n'
             'Введите фамилию заново:'
    )


@start_router.message(StateFilter(FSMFillFormName.last_name), F.text.isalpha())
async def process_last_name_sent(msg: Message, state: FSMContext):
    await state.update_data(last_name=msg.text)
    await state.set_state(FSMFillFormName.last_name)
    fill_data = await state.get_data()
    await add_user_name(msg.from_user.id, fill_data['project_chat_id'],
                        fill_data['first_name'], fill_data['last_name'])
    await state.clear()
    await msg.answer(f"Вы зарегистрированы в проекте\n"
                     f"Ваше имя в проекте: {fill_data['first_name']}\n"
                     f"Ваша фамилия в проекте: {fill_data['last_name']}")
    await msg.answer("Ожидайте задач или создавайте свои проекты!")


@start_router.message(StateFilter(FSMFillFormName.last_name))
async def warning_not_last_name(message: Message):
    await message.answer(
        text='С именем справились, с фамилией такие же условия\n'
             'Не используйте цифры, пробелы и другие символы!\n'
             'Введите фамилию заново:'
    )
