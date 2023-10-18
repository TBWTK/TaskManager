from aiogram import types, Router, Bot
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.state import default_state
from aiogram.fsm.context import FSMContext


from tg_bot.keyboards.simple_row_reply import make_row_keyboard, create_link
from tg_bot.keyboards.project_keyboard import inline_button_project_pr, choice_project
from tg_bot.states.project_state import FSMFillFormProject
from tg_bot.services.project_service import check_chat_id_from_project, create_project, create_text_task_responsible, \
    get_project_id_and_name, create_template_html
from tg_bot.services.base_service import get_all_project_user


project_router = Router()


@project_router.message(Command("project"), StateFilter(default_state))
async def project_handler(msg: Message, state: FSMContext):
    await msg.answer("Выберите какую команду вы хотите выполнить:",
                     reply_markup=make_row_keyboard(choice_project['creating_or_viewing']))
    await state.set_state(FSMFillFormProject.creating_or_viewing)


@project_router.message(StateFilter(FSMFillFormProject.creating_or_viewing))
async def choice_creating_or_viewing(msg: Message, state: FSMContext):
    await msg.answer("Проверяем чат:")
    if msg.text == 'Создать проект' and msg.chat.type != 'private':
        check_project = await check_chat_id_from_project(msg.chat.id)
        if check_project:
            await msg.answer("Введите название чата:", reply_markup=ReplyKeyboardRemove())
            await state.set_state(FSMFillFormProject.create_name_project)
        else:
            await msg.answer("Данный чат уже инициализирован)\n"
                             "Обратитесь к администратору, чтобы вам выдали статус "
                             "для получения возможности в постановке задач!", reply_markup=ReplyKeyboardRemove())
            await state.clear()
    elif msg.text == 'Мои проекты' and msg.chat.type == 'private':
        await state.set_state(FSMFillFormProject.viewing)
        await msg.answer("Выберите какую команду вы хотите выполнить:",
                         reply_markup=make_row_keyboard(choice_project['viewing']))
    elif msg.text == 'Создать приглашение' and msg.chat.type == 'private':
        await msg.answer("Выберите проект, после чего будет создана ссылка-приглашение",
                         reply_markup=ReplyKeyboardRemove())
        await state.clear()
    elif msg.chat.type != 'private':
        await msg.answer("Для просмотра перейдите в личные сообщения бота", reply_markup=ReplyKeyboardRemove())
        await state.clear()
    else:
        await msg.answer("Вы не можете создать проект в личных сообщениях\n"
                         "Добавьте бота в чат и инициализируйте его", reply_markup=ReplyKeyboardRemove())
        await state.clear()


# Создание проекта, добавление имени для проекта
@project_router.message(StateFilter(FSMFillFormProject.create_name_project))
async def process_name_sent(msg: Message, state: FSMContext):
    await state.update_data(name_project=msg.text)
    fill_data = await state.get_data()
    await create_project(msg.from_user.id, msg.chat.id, fill_data['name_project'])
    await state.clear()
    await msg.answer("Вы успешно создали проект!\n"
                     "Создаем ссылку!")
    project = await get_project_id_and_name(msg.chat.id)
    await msg.answer(f"Ссылка-приглашение в проект от @{msg.from_user.username}\n"
                     f"В проект {fill_data['name_project']}",
                     reply_markup=create_link(project['chat_id'], project['name'], 'responsible'))


# Выбор
@project_router.message(StateFilter(FSMFillFormProject.viewing))
async def choice_admin_or_responsible(msg: Message, state: FSMContext):
    if msg.text == 'Проекты, где я ответственный':
        await msg.answer("Выберите какую команду вы хотите выполнить:",
                         reply_markup=make_row_keyboard(choice_project['viewing_responsible']))
        await state.set_state(FSMFillFormProject.viewing_responsible)
    elif msg.text == 'Проекты, где я админ':
        await msg.answer("Выберите какую команду вы хотите выполнить:",
                         reply_markup=make_row_keyboard(choice_project['viewing_admin']))
        await state.set_state(FSMFillFormProject.viewing_admin)
    else:
        await msg.answer("Что то сломалось", reply_markup=ReplyKeyboardRemove())
        await state.clear()


# Команды для ответственного
@project_router.message(StateFilter(FSMFillFormProject.viewing_responsible))
async def choice_responsible(msg: Message, state: FSMContext):
    if msg.text == 'Просмотр задач':
        await msg.answer("Выберите проект", reply_markup=ReplyKeyboardRemove())
        await state.update_data(status='view')
        all_project = await get_all_project_user(msg.from_user.id, False)
        if all_project is not None:
            await msg.answer("Ваши проекты:",
                             reply_markup=inline_button_project_pr(all_project))
            await state.set_state(FSMFillFormProject.final_choice)


# Команды для админа
@project_router.message(StateFilter(FSMFillFormProject.viewing_admin))
async def choice_admin(msg: Message, state: FSMContext):
    if msg.text == 'Выгрузить отчет':
        await msg.answer("Выберите проект: после чего мы выгрузим по нему отчет",
                         reply_markup=ReplyKeyboardRemove())
        await state.update_data(status='report')
        all_project = await get_all_project_user(msg.from_user.id, True)
        if all_project is not None:
            await msg.answer("Ваши проекты:",
                             reply_markup=inline_button_project_pr(all_project))
            await state.set_state(FSMFillFormProject.final_choice)
    elif msg.text == 'Добавить админа':
        await msg.answer("Выберите проект, после чего пришлем вам ссылку-приглашения для администратора",
                         reply_markup=ReplyKeyboardRemove())
        await state.update_data(status='add_link')
        await state.update_data(type_status_user='admin')
        all_project = await get_all_project_user(msg.from_user.id, True)
        if all_project is not None:
            await msg.answer("Ваши проекты:",
                             reply_markup=inline_button_project_pr(all_project))
            await state.set_state(FSMFillFormProject.final_choice)
        else:
            await msg.answer("У вас нет проектов")
            await state.clear()
    elif msg.text == 'Добавить ответственного':
        await msg.answer("Выберите проект, после чего пришлем вам ссылку-приглашения для администратора",
                         reply_markup=ReplyKeyboardRemove())
        await state.update_data(status='add_link')
        await state.update_data(type_status_user='responsible')
        all_project = await get_all_project_user(msg.from_user.id, True)
        if all_project is not None:
            await msg.answer("Ваши проекты:",
                             reply_markup=inline_button_project_pr(all_project))
            await state.set_state(FSMFillFormProject.final_choice)
        else:
            await msg.answer("У вас нет проектов")
            await state.clear()
    else:
        await msg.answer("Что то сломалось", reply_markup=ReplyKeyboardRemove())
        await state.clear()


@project_router.callback_query(StateFilter(FSMFillFormProject.final_choice),
                               lambda c: c.data.startswith('ch_project_pr'))
async def status_choice(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    trash, project_chat_id = call.data.split(":")
    fill_data = await state.get_data()
    await bot.edit_message_text(text='Задание принято!',
                                chat_id=call.message.chat.id, message_id=call.message.message_id)
    await call.message.answer("Готовим данные...")
    await state.clear()
    project = await get_project_id_and_name(project_chat_id)
    if fill_data['status'] == 'report':
        await create_template_html(call.message.chat.id, project_chat_id, bot)
    elif fill_data['status'] == 'add_link':
        await call.message.answer(f"Ссылка-приглашение в проект от @{call.from_user.username}\n"
                                  f"В проект {project['name']}",
                                  reply_markup=create_link(project['chat_id'], project['name'],
                                                           fill_data['type_status_user']))
    elif fill_data['status'] == 'view':
        text = await create_text_task_responsible(call.from_user.id)
        if text == "":
            await call.message.answer("У вас нет активных задач!")

        else:
            await call.message.answer("Ваши задачи:\n\n"f"{text}")
    else:
        await call.message.answer("Что то сломалось")
    await state.clear()
