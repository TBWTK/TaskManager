from tg_bot.models.models import Event
from .base_service import process_input_time
from datetime import date


async def update_overdue():
    events = await Event.filter(is_active=True).all()
    today = date.today()
    for event in events:
        if event.date_event < today and event.is_active == True:
            event.is_active = False
            event.is_overdue = True
            await event.save()


async def update_event(event_id: int):
    event = await Event.get(id=event_id)
    event.is_active = False
    event.is_completed = True
    await event.save()


async def update_completed(event_id: int):
    event = await Event.get(id=event_id)
    event.is_active = False
    event.is_overdue = False
    event.is_completed = True
    await event.save()


async def change_deadline(event_id: int, new_date, new_time):
    updated, created = await Event.update_or_create(
        id=event_id,
        defaults={"is_changed": True,
                  "is_active:": True,
                  "is_validation": False,
                  'date_event': new_date,
                  'time_event': process_input_time(new_time)
                  }
    )
    if not created:
        await updated.save()
    """
    event = await Event.get(id=event_id)
    event.is_changed = True
    event.date_event = process_input_date(new_date)
    event.time_event = process_input_time(new_time)
    await event.save()
"""
