from tg_bot.models.models import Participants, Event, ParticipantsEvent
from datetime import datetime, timedelta, date
import pytz


def process_input_time(time_str: str):
    datetime_obj = datetime.strptime(time_str, '%H:%M')
    return datetime_obj.time()


async def get_all_project_user(user_id, flag: bool):
    if flag:
        check = await Participants.filter(player=user_id, is_admin=True).prefetch_related('project').all()
        if check is not None:
            return check
        else:
            return None
    else:
        check = await Participants.filter(player=user_id, is_responsible=True).prefetch_related('project').all()
        if check is not None:
            return check
        else:
            return None


async def get_task_per_day() -> list[Event]:
    check = await Event.filter(date_event=date.today(), is_active=True).all()
    if check is not None:
        return check


async def get_task_next_day() -> list[Event]:
    check = await Event.filter(date_event=date.today() + timedelta(days=1), is_active=True).all()
    if check is not None:
        return check


async def get_task_overdue() -> list[Event]:
    check = await Event.filter(is_overdue=True).all()
    if check is not None:
        return check


async def calculate_time_hour_reminder_timedelta(item_time):

    moscow_tz = pytz.timezone("Europe/Moscow")
    current_time = datetime.now(moscow_tz).time()
    task_time = item_time

    current_timedelta = timedelta(hours=current_time.hour, minutes=current_time.minute, seconds=current_time.second)
    task_timedelta = timedelta(hours=task_time.hour, minutes=task_time.minute, seconds=task_time.second)
    hour_reminder_timedelta = task_timedelta - current_timedelta - timedelta(hours=1)
    print(current_timedelta, task_timedelta, hour_reminder_timedelta.total_seconds())
    hour_reminder_start_task = hour_reminder_timedelta.total_seconds()
    if hour_reminder_start_task < 0:
        hour_reminder_start_task = 200
    return hour_reminder_start_task


async def get_event(event_id: int) -> Event:
    return await Event.filter(id=event_id).first()


async def get_event_data(event: Event) -> dict:
    if event.is_task:
        # Получаем объект ParticipantsEvent, связанный с данным событием
        participants_event = await ParticipantsEvent.filter(event=event).first()

        # Получаем связанные объекты
        producer = await participants_event.producer
        responsible = await participants_event.responsible
        project = await participants_event.project

        # Получаем связанные объекты User
        producer_user = await producer.player
        responsible_user = await responsible.player

        # Формируем и возвращаем словарь с данными
        event_data = {
            "is_task": event.is_task,
            "producer_user_id": producer_user.user_id,
            "producer_username": producer_user.username,
            "responsible_user_id": responsible_user.user_id,
            "responsible_username": responsible_user.username,
            "event_date": event.date_event,
            "event_time": event.time_event,
            "event_description": event.description,
            "event_is_private_notification": event.is_private_notification,
            "project_chat_id": project.chat_id,
            "project_name": project.name,
        }
        return event_data
    else:
        # Получаем объект ParticipantsEvent, связанный с данным событием
        participants_event = await ParticipantsEvent.filter(event=event).first()

        # Получаем связанные объекты
        producer = await participants_event.producer
        project = await participants_event.project

        # Получаем связанные объекты User
        producer_user = await producer.player

        # Формируем и возвращаем словарь с данными
        event_data = {
            "is_task": event.is_task,
            "producer_user_id": producer_user.user_id,
            "producer_username": producer_user.username,
            "event_date": event.date_event,
            "event_time": event.time_event,
            "event_description": event.description,
            "event_is_private_notification": event.is_private_notification,
            "project_chat_id": project.chat_id,
            "project_name": project.name,
        }
        return event_data


def preparation_text_notification(event: dict, flag: str) -> dict:
    data = {'chat_id': int, 'text': ""}

    if flag == "new":
        data['text'] += '<b><i>НОВОЕ СОБЫТИЕ</i></b>\n'
    if flag == "check_ex" or flag == "event":
        data['text'] += '<b><i>НАПОМИНАНИЕ</i></b>\n'
    if flag == "new_deadline_req":
        data['text'] += '<b><i>ЗАПРОС НА ПЕРЕНОС СРОКА</i></b>\n'
    if flag == "new_deadline":
        data['text'] += '<b><i>НАЗНАЧИТЬ НОВЫЙ СРОК</i></b>\n'
    if flag == "change":
        data['text'] += '<b><i>ОБНОВЛЕНИЕ КРАЙНЕГО СРОКА</i></b>\n'
    if flag == "validation":
        data['text'] += '<b><i>ВАЛИДАЦИЯ</i></b>\n'
    if flag == "completed":
        data['text'] += '<b><i>ВЫПОЛНЕНО</i></b>\n'

    if event['is_task']:
        data['text'] += '\n<b>ЗАДАЧА</b>\n'
    else:
        data['text'] += '\n<b>МЕРОПРИЯТИЕ</b>\n'
    data['text'] += f'<b>Проект</b>: <i>{event["project_name"]}</i>\n'
    data['text'] += f'<b>Продюсер</b>: @{event["producer_username"]}\n'
    if event['is_task']:
        data['text'] += f'<b>Исполнитель</b>: @{event["responsible_username"]}\n'

    data['text'] += f'<b>Дата</b>: {event["event_date"].strftime("%d.%m.%y")}\n'
    data['text'] += f'Время: {event["event_time"].strftime("%H:%M")}\n'
    data['text'] += f'<b>Описание</b>: {event["event_description"]}\n'

    if event['event_is_private_notification']:
        data['chat_id'] = event['responsible_user_id']
    else:
        data['chat_id'] = event['project_chat_id']

    if flag == "check_ex":
        if not event["is_task"]:
            data['chat_id'] = event['project_chat_id']
        else:
            data['chat_id'] = event['responsible_user_id']
    if flag == "new_deadline" or flag == 'new_deadline_req':
        data['chat_id'] = event['producer_user_id']
    if flag == "validation":
        data['chat_id'] = event['producer_user_id']
    return data
