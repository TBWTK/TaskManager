from tg_bot.models.models import Participants, Project, Event, ParticipantsEvent, User
from .base_service import process_input_time


async def get_all_responsible(project: int):
    check_player = await Participants.filter(project=project, is_responsible=True).prefetch_related('player').all()
    return check_player


async def save_event(event_dc: dict):
    if event_dc['event'] == 'task':
        event = Event(is_task=True, is_active=True,
                      is_private_notification=event_dc['notification'],
                      date_event=event_dc['date'],
                      time_event=process_input_time(event_dc['time']),
                      description=event_dc['description']
                      )
        await event.save()

        producer_user, _ = await User.get_or_create(user_id=event_dc['producer'])
        responsible_user, _ = await User.get_or_create(user_id=event_dc['responsible'])
        project, _ = await Project.get_or_create(chat_id=event_dc['project'])

        # Получаем или создаем объекты Participants для producer и responsible
        producer, _ = await Participants.get_or_create(player=producer_user, project=project)
        responsible, _ = await Participants.get_or_create(player=responsible_user, project=project)

        part_event = ParticipantsEvent(project=project, producer=producer, responsible=responsible, event=event)
        await part_event.save()
        return event
    if event_dc['event'] == 'event':
        event = Event(is_task=False, is_active=True,
                      is_private_notification=False,
                      date_event=event_dc['date'],
                      time_event=process_input_time(event_dc['time']),
                      description=event_dc['description']
                      )
        await event.save()

        producer_user, _ = await User.get_or_create(user_id=event_dc['producer'])
        project, _ = await Project.get_or_create(chat_id=event_dc['project'])
        producer, _ = await Participants.get_or_create(player=producer_user, project=project)

        part_event = ParticipantsEvent(project=project, producer=producer, event=event)
        await part_event.save()
        return event
