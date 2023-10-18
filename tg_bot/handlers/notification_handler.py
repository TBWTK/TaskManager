from datetime import date, timedelta, datetime

from aiogram import types, Router, Bot, F
from aiogram.filters import StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import default_state
from aiogram.fsm.context import FSMContext
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from tg_bot.filters.filters import TimeFormatFilter
from tg_bot.scheduler.notification import send_message_question_implementation
from tg_bot.services.base_service import get_event, get_event_data, preparation_text_notification, \
    calculate_time_hour_reminder_timedelta, process_input_time
from tg_bot.keyboards.notification_keyboards import request_postponement, \
    processing_postponement_request, event_validation
from tg_bot.services.notification_services import update_completed, change_deadline
from tg_bot.states.notification_state import FSMFillFormNotif
from tg_bot.keyboards.calendar_keyboard import SimpleCalendar

notif_router = Router()


search_callback_calendar = "notif"


# Валидация задачи КНОПКА ДА:ВЫПОЛНЕНО-НЕТ:НЕ ВЫПОЛНЕНО
@notif_router.callback_query(lambda c: c.data.startswith('event_done'), StateFilter(default_state))
async def notif_event_done(call: types.CallbackQuery, bot: Bot):
    trash, event_id = call.data.split(":")
    await bot.edit_message_text(text='Отлично, отправляем задачу на валидацию!',
                                chat_id=call.message.chat.id, message_id=call.message.message_id)
    event = await get_event(event_id)
    dict_event = await get_event_data(event)
    prepare = preparation_text_notification(dict_event, "validation")
    await bot.send_message(chat_id=prepare['chat_id'], text=prepare['text'], reply_markup=event_validation(event_id))


# Подтверждение выполнения задачи НЕ ОТПРАВЛЯЕМ КНОПКИ
@notif_router.callback_query(lambda c: c.data.startswith('event_completed'), StateFilter(default_state))
async def notif_event_validation(call: types.CallbackQuery, bot: Bot):
    trash, event_id = call.data.split(":")
    await bot.edit_message_text(text='Задача выполнена, готовим оповещение!',
                                chat_id=call.message.chat.id, message_id=call.message.message_id)
    await update_completed(event_id)
    event = await get_event(event_id)
    dict_event = await get_event_data(event)
    prepare = preparation_text_notification(dict_event, "completed")
    print(prepare)
    await bot.send_message(chat_id=call.message.chat.id, text=prepare['text'])
    await bot.send_message(chat_id=prepare['chat_id'], text=prepare['text'])


# Задача не выполнена, вопрос о запросе на перенос срока КНОПКИ-- ДА:ПЕРЕНСТИ-НЕТ:НЕ ПЕРЕНОСИМ
@notif_router.callback_query(lambda c: c.data.startswith('event_not_done'), StateFilter(default_state))
async def notif_event_not_done(call: types.CallbackQuery, bot: Bot):
    trash, event_id = call.data.split(":")
    await bot.edit_message_text(text='Задача не выполнена\n\n'
                                     'Запросить перенос срока?',
                                chat_id=call.message.chat.id,
                                message_id=call.message.message_id,
                                reply_markup=request_postponement(event_id))


# Вопрос о запросе на перенос срока отклонен НЕТ КНОПОК
@notif_router.callback_query(lambda c: c.data.startswith('event_not_change'), StateFilter(default_state))
async def notif_event_not_change(call: types.CallbackQuery, bot: Bot):
    await bot.edit_message_text(text='Не переносим срок задачи',
                                chat_id=call.message.chat.id,
                                message_id=call.message.message_id)


# Отправка запроса на перенос срока
@notif_router.callback_query(lambda c: c.data.startswith('event_req_new_deadline'), StateFilter(default_state))
async def notif_event_req_new_deadline(call: types.CallbackQuery, bot: Bot):
    trash, event_id = call.data.split(":")
    await bot.edit_message_text(text='Задача не выполнена\n\n',
                                chat_id=call.message.chat.id,
                                message_id=call.message.message_id)
    event = await get_event(event_id)
    dict_event = await get_event_data(event)
    prepare = preparation_text_notification(dict_event, "new_deadline_req")
    await bot.send_message(chat_id=prepare['chat_id'], text=prepare['text'],
                           reply_markup=processing_postponement_request(event_id))


# Отправка запроса на перенос срока
@notif_router.callback_query(lambda c: c.data.startswith('event_new_deadline'), StateFilter(default_state))
async def event_new_deadline(call: types.CallbackQuery, bot: Bot, state: FSMContext):
    trash, event_id = call.data.split(":")
    await bot.edit_message_text(text='Переносим срок задачи',
                                chat_id=call.message.chat.id,
                                message_id=call.message.message_id)
    await state.update_data(event_id=event_id)
    await call.message.answer("Введите время:\n"
                              "Формат времени ЧЧ:ММ")
    await state.set_state(FSMFillFormNotif.time)


@notif_router.message(StateFilter(FSMFillFormNotif.time), TimeFormatFilter())
async def process_age_sent(msg: Message, state: FSMContext):
    await state.update_data(time=msg.text)
    await msg.answer("Спасибо, теперь введите дату:",
                     reply_markup=await SimpleCalendar().start_calendar(search_callback_calendar))
    await state.set_state(FSMFillFormNotif.date)


@notif_router.message(StateFilter(FSMFillFormNotif.time))
async def warning_not_age(message: Message):
    await message.answer(
        text='Введите корректное время в формате ЧЧ:ММ\n\n'
             'Попробуйте еще раз\n\n'
    )


@notif_router.message(F.data.startswith(f'simple_calendar{search_callback_calendar}'))
async def process_age_sent(call: CallbackQuery, state: FSMContext, bot: Bot,
                           apscheduler: AsyncIOScheduler):
    selected, date_choice = await SimpleCalendar().process_selection(call, search_callback_calendar)
    if selected:
        await call.message.answer("Обновляем задачу...:")
        await state.update_data(date=date_choice)
        fill_data = await state.get_data()
        await state.clear()

        await change_deadline(fill_data['event_id'], fill_data['date'], fill_data['time'])

        event = await get_event(fill_data['event_id'])
        dict_event = await get_event_data(event)
        prepare = preparation_text_notification(dict_event, "change")

        await bot.send_message(prepare['chat_id'], prepare['text'])
        await bot.send_message(call.from_user.id, prepare['text'])

        if fill_data['date'].date() == date.today():
            prepare_event = preparation_text_notification(dict_event, "check_ex")
            seconds = await calculate_time_hour_reminder_timedelta(process_input_time(fill_data['time']))
            apscheduler.add_job(send_message_question_implementation, trigger='date',
                                run_date=datetime.now() + timedelta(seconds=seconds),
                                kwargs={'bot': bot,
                                        'chat_id': prepare_event['chat_id'],
                                        'text': prepare_event['text'],
                                        'event_id': event.id})


@notif_router.message(StateFilter(FSMFillFormNotif.date))
async def warning_not_age(message: Message):
    await message.answer(
        text='Введите корректное дату в формате дд.мм\n\n'
             'Попробуйте еще раз\n\n'
    )
