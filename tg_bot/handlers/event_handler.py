from datetime import date, datetime, timedelta

from aiogram import types, Router, Bot, F
from aiogram.filters import Command, StateFilter
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from aiogram.fsm.state import default_state
from aiogram.fsm.context import FSMContext
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from tg_bot.states.event_state import FSMFillFormEvent
from tg_bot.filters.filters import TimeFormatFilter
from tg_bot.keyboards.simple_row_reply import make_row_keyboard
from tg_bot.keyboards.event_keyboard import choice_event, inline_button_project_ev, inline_button_responsible_ev
from tg_bot.services.base_service import get_all_project_user, get_event_data, \
    preparation_text_notification, calculate_time_hour_reminder_timedelta
from tg_bot.services.event_service import get_all_responsible, save_event, process_input_time
from tg_bot.scheduler.notification import send_message_question_implementation, send_message_event
from tg_bot.keyboards.calendar_keyboard import SimpleCalendar

event_router = Router()

search_callback_calendar = "event"


@event_router.message(Command("event"), StateFilter(default_state))
async def event_handler(msg: Message, state: FSMContext):
    if msg.chat.type == 'private':
        await msg.answer("Вы открыли модуль создания событий\n"
                         "В этом модуле вы можете создавать мероприятия или задачи:\n"
                         "<b>Мероприятие</b> - для всех участников проекта\n"
                         "<b>Задача</b> - назначается ответственный\n"
                         )
        await msg.answer("Выберите какую команду вы хотите выполнить:",
                         reply_markup=make_row_keyboard(choice_event['event_task']))
        await state.set_state(FSMFillFormEvent.event_or_task)
    else:
        await msg.answer("Команда выполняется в личных сообщениях")


@event_router.message(StateFilter(FSMFillFormEvent.event_or_task))
async def choice_event_or_task(msg: Message, state: FSMContext):
    await msg.answer("Отлично!", reply_markup=ReplyKeyboardRemove())
    await state.update_data(producer=msg.from_user.id)
    if msg.text == 'Закрыть':
        await msg.answer("Закрываем модуль событий", reply_markup=ReplyKeyboardRemove())
        await state.clear()
    else:
        if msg.text == 'Создать мероприятие':
            await state.update_data(event='event')
        if msg.text == 'Создать задачу':
            await state.update_data(event='task')
        all_project = await get_all_project_user(msg.from_user.id, True)
        if all_project is not None:
            await msg.answer("Для продолжения выберите проект, для которого вы хотите создать событие\n\n"
                             "Ваши проекты:",
                             reply_markup=inline_button_project_ev(all_project))
            await state.set_state(FSMFillFormEvent.project)
        else:
            await msg.answer("У вас нет проектов")
            await state.clear()


@event_router.callback_query(StateFilter(FSMFillFormEvent.project),
                             lambda c: c.data.startswith('ch_project_ev'))
async def choice_project(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    trash, project_chat_id = call.data.split(":")
    fill_data = await state.get_data()
    await state.update_data(project=int(project_chat_id))
    await bot.edit_message_text(text='Идем дальше!',
                                chat_id=call.message.chat.id, message_id=call.message.message_id)
    if fill_data['event'] == 'task':
        all_responsible = await get_all_responsible(project_chat_id)
        if all_responsible is not None:
            await call.message.answer("Выберите ответственного, который будет выполнять задание\n\n"
                                      "Ваши исполнители:",
                                      reply_markup=inline_button_responsible_ev(all_responsible))
            await state.set_state(FSMFillFormEvent.responsible)
        else:
            await call.message.answer("У вас нет ни одного ответственного")
    if fill_data['event'] == 'event':
        await call.message.answer("Введите время:\n"
                                  "Формат времени ЧЧ:ММ")
        await state.set_state(FSMFillFormEvent.time)


@event_router.callback_query(StateFilter(FSMFillFormEvent.responsible),
                             lambda c: c.data.startswith('resp'))
async def choice_responsible(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    trash, responsible = call.data.split(":")
    await state.update_data(responsible=int(responsible))

    await bot.edit_message_text(text='Идем дальше!',
                                chat_id=call.message.chat.id, message_id=call.message.message_id)
    await call.message.answer("Введите время:\n"
                              "Формат времени ЧЧ:ММ")
    await state.set_state(FSMFillFormEvent.time)


@event_router.message(StateFilter(FSMFillFormEvent.time), TimeFormatFilter())
async def process_age_sent(msg: Message, state: FSMContext):
    await state.update_data(time=msg.text)
    await msg.answer("Спасибо, теперь введите дату:",
                     reply_markup=await SimpleCalendar().start_calendar(search_callback_calendar))
    await state.set_state(FSMFillFormEvent.date)


@event_router.message(StateFilter(FSMFillFormEvent.time))
async def warning_not_age(message: Message):
    await message.answer(
        text='Введите корректное время в формате ЧЧ:ММ\n\n'
             'Попробуйте еще раз\n\n'
    )


@event_router.callback_query(F.data.startswith(f'simple_calendar{search_callback_calendar}'))
async def process_simple_calendar(call: CallbackQuery, state: FSMContext):
    selected, date_choice = await SimpleCalendar().process_selection(call, search_callback_calendar)
    if selected:
        await call.message.answer("Отлично\nТеперь введите описание:")
        await state.update_data(date=date_choice)
        await state.set_state(FSMFillFormEvent.description)


@event_router.message(StateFilter(FSMFillFormEvent.date))
async def warning_not_age(message: Message):
    await message.answer(
        text='Введите корректное дату в формате дд.мм\n\n'
             'Попробуйте еще раз\n\n'
    )


@event_router.message(StateFilter(FSMFillFormEvent.description))
async def process_age_sent(msg: Message, state: FSMContext):
    await state.update_data(description=msg.text)
    fill_data = await state.get_data()
    if fill_data['event'] == 'task':
        await msg.answer(text='Выберите способ оповещения\n'
                              '<b>Только исполнителю</b> - '
                              'уведомление о задаче и о выполнении придет только исполнителю\n'
                              '<b>В чат проекта</b> - уведомление о задаче и о выполнении придет в чат проекта\n\n'
                              '<i>Уведомления о выполнении, валидации и переносе срока будет '
                              'приходить только продюсеру и исполнителю задачи</i>')
        await msg.answer("Выберите какую команду вы хотите выполнить:",
                         reply_markup=make_row_keyboard(choice_event['type_notif']))
        await state.set_state(FSMFillFormEvent.notification)


@event_router.message(StateFilter(FSMFillFormEvent.notification))
async def choice_event_or_task(msg: Message, bot: Bot, state: FSMContext, apscheduler: AsyncIOScheduler):
    fill_data = await state.get_data()
    if fill_data['event'] == 'event':
        await state.update_data(description=msg.text)
    await msg.answer("Создаем событие...", reply_markup=ReplyKeyboardRemove())

    if fill_data['event'] == 'task':
        await state.update_data(producer=msg.from_user.id)
        if msg.text == 'Только исполнителю':
            await state.update_data(notification=True)
        if msg.text == 'В чат проекта':
            await state.update_data(notification=False)

    fill_data = await state.get_data()
    await state.clear()
    await msg.answer(f"Событие создано!")
    event = await save_event(fill_data)
    event_dict = await get_event_data(event)
    print(event_dict)
    prepare_event = preparation_text_notification(event_dict, "new")

    await bot.send_message(prepare_event['chat_id'], prepare_event['text'])
    await bot.send_message(msg.from_user.id, prepare_event['text'])

    if fill_data['date'].date() == date.today():
        if fill_data['event'] == 'event':
            prepare_event = preparation_text_notification(event_dict, "event")
            seconds = await calculate_time_hour_reminder_timedelta(process_input_time(fill_data['time']))
            apscheduler.add_job(send_message_event, trigger='date',
                                run_date=datetime.now() + timedelta(seconds=seconds),
                                kwargs={'bot': bot,
                                        'chat_id': prepare_event['chat_id'],
                                        'text': prepare_event['text'],
                                        'event_id': event.id})
        else:
            prepare_event = preparation_text_notification(event_dict, "check_ex")
            seconds = await calculate_time_hour_reminder_timedelta(process_input_time(fill_data['time']))
            apscheduler.add_job(send_message_question_implementation, trigger='date',
                                run_date=datetime.now() + timedelta(seconds=seconds),
                                kwargs={'bot': bot,
                                        'chat_id': prepare_event['chat_id'],
                                        'text': prepare_event['text'],
                                        'event_id': event.id})
