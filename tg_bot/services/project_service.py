import datetime
from tortoise.exceptions import DoesNotExist
from jinja2 import Environment, FileSystemLoader
import os
import pdfkit

from aiogram.types import FSInputFile
from aiogram import Bot

from tg_bot.models.models import User, Project, Participants, ParticipantsEvent
from tg_bot.services.base_service import get_event_data, preparation_text_notification

base_name_path = os.path.basename(__file__)
base_dir = os.path.abspath(__file__).replace(base_name_path, '')


async def check_chat_id_from_project(chat_id: int):
    check_project = await Project.get_or_none(chat_id=chat_id)
    if check_project is None:
        return True
    else:
        return False


async def create_project(id_user: int, chat_id: int, name_project: str):
    user, _ = await User.get_or_create(user_id=id_user)
    project = Project(chat_id=chat_id, name=name_project)
    await project.save()
    admin_project = Participants(player=user, project=project, is_admin=True)
    await admin_project.save()


async def get_project_id_and_name(chat_id: int):
    project = await Project.filter(chat_id=chat_id).first()
    project_dict = {'chat_id': project.chat_id,
                    'name': project.name}
    return project_dict


async def get_task_responsible(responsible_id: int):
    participants_events = await ParticipantsEvent.filter(
        responsible_id=responsible_id,
        event__is_task=True,
        event__is_active=True
    ).exclude(
        event__is_overdue=True
    ).prefetch_related('event').all()

    events = [participant_event.event for participant_event in participants_events]

    print(len(events))

    return events


async def create_text_task_responsible(responsible_id: int) -> str:
    pre_text = ""
    events = await get_task_responsible(responsible_id)
    for event in events:
        event_dict = await get_event_data(event)
        print(event_dict)
        check_dict = preparation_text_notification(event_dict, "none")
        pre_text += check_dict['text']
    return pre_text


async def get_events_and_generate_report(project_chat_id: int):
    try:
        project = await Project.get(chat_id=project_chat_id)
    except DoesNotExist:
        print(f"Проект с chat_id {project_chat_id} не найден.")
        return None

    reports = {
        "project_name": project.name,
        "is_completed": 0,
        "is_active": 0,
        "is_overdue": 0,
        "all": 0,
        "events": 0,
        "upcoming_events": []
    }

    participants_events = await ParticipantsEvent.filter(project=project).prefetch_related("event")

    for pe in participants_events:
        event = pe.event
        if event.is_task:
            if event.is_completed:
                reports["is_completed"] += 1
            if event.is_active:
                reports["is_active"] += 1
            if event.is_overdue:
                reports["is_overdue"] += 1
            reports["all"] += 1
        else:
            reports["events"] += 1
            if event.date_event >= datetime.date.today():
                reports['upcoming_events'].append(
                    dict(disc_event=event.description,
                         date_event=event.date_event.strftime("%d.%m.%y"),
                         time_event=event.time_event.strftime("%H:%M")))

    participants = await Participants.filter(project=project).prefetch_related("player")
    project_admins = [{"name": f"{participant.last_name} {participant.first_name}"}
                      for participant in participants if participant.is_admin]
    project_responsible = [{"name": f"{participant.last_name} {participant.first_name}"}
                           for participant in participants if participant.is_responsible]

    reports["admin"] = project_admins
    reports["responsible"] = project_responsible
    reports["all_admin"] = len(reports["admin"])
    reports["all_responsible"] = len(reports["responsible"])

    # Получение участников проекта
    participants = await Participants.filter(project=project, is_responsible=True).prefetch_related("player")

    # Создание словаря с задачами для каждого участника
    task_players = {}
    for participant in participants:
        name = f"{participant.last_name} {participant.first_name}"
        task_players[name] = {
            "is_completed": 0,
            "is_active": 0,
            "is_overdue": 0,
            "all": 0
        }
        # Обновление задач для каждого участника
        participant_events = await ParticipantsEvent.filter(producer=participant).prefetch_related("event")
        for pe in participant_events:
            event = pe.event
            if event.is_task:
                if event.is_completed:
                    task_players[name]["is_completed"] += 1
                if event.is_active:
                    task_players[name]["is_active"] += 1
                if event.is_overdue:
                    task_players[name]["is_overdue"] += 1
                task_players[name]["all"] += 1
    # Добавление списка участников с задачами в словарь reports_task
    reports["task_player"] = task_players

    print(reports)
    return reports


async def send_or_delete_report(bot: Bot, chat_id):
    with open(base_dir + "test.html", "r") as f:
        html_data = f.read()
    pdfkit.from_string(html_data, base_dir + "out.pdf")

    # Отправка PDF-файла
    doc = FSInputFile(path=base_dir + "out.pdf")
    await bot.send_document(chat_id=chat_id, document=doc, caption='Ваш отчет!')

    os.remove(base_dir + "out.pdf")
    os.remove(base_dir + "test.html")


async def create_template_html(chat_id: int, project_chat_id: int, bot: Bot):
    env = Environment(loader=FileSystemLoader(base_dir))
    template = env.get_template('example.html')
    sample = await get_events_and_generate_report(project_chat_id)
    html_content = template.render(items=sample)
    with open(base_dir + 'test.html', 'w', encoding='utf-8') as html_file:
        html_file.write(html_content)
    await send_or_delete_report(bot, chat_id)
