from tortoise.models import Model
from tortoise import fields


class User(Model):
    user_id = fields.BigIntField(pk=True)

    username = fields.CharField(max_length=255, null=True)

    def __str__(self):
        return f"{self.username}"


class Project(Model):
    chat_id = fields.BigIntField(pk=True)

    name = fields.CharField(max_length=50, null=True)

    def __str__(self):
        return self.name


class Participants(Model):
    id = fields.BigIntField(pk=True)

    project = fields.ForeignKeyField('models.Project', related_name='participants_project', null=True)
    player = fields.ForeignKeyField('models.User', related_name='participants_project_producer', null=True)
    is_admin = fields.BooleanField(null=True, default=False)
    is_responsible = fields.BooleanField(null=True, default=False)
    first_name = fields.CharField(max_length=50, null=True)
    last_name = fields.CharField(max_length=50, null=True)

    def __str__(self):
        return f"{self.player}_{self.project}"


class Event(Model):
    id = fields.BigIntField(pk=True)

    is_created = fields.BooleanField(default=True)  # В создании
    is_task = fields.BooleanField(default=True)  # Задача или событие
    is_active = fields.BooleanField(default=True)   # Активно
    is_overdue = fields.BooleanField(default=False)   # Просрочено
    is_completed = fields.BooleanField(default=False)   # Выполнено
    is_changed = fields.BooleanField(default=False)   # Изменена
    is_private_notification = fields.BooleanField(default=True)   # Приватный метод оповещения

    date_event = fields.DateField(null=True)   # Дата
    time_event = fields.TimeField(null=True)   # Время
    description = fields.CharField(max_length=2500, null=True)   # Описание

    def __str__(self):
        return f"{self.id}"


class ParticipantsEvent(Model):
    id = fields.BigIntField(pk=True)

    project = fields.ForeignKeyField('models.Project', related_name='participants_event_project', null=True)
    producer = fields.ForeignKeyField('models.Participants',
                                      related_name='participants_event_project_producer', null=True)
    responsible = fields.ForeignKeyField('models.Participants',
                                         related_name='participants_event_project_responsible', null=True)
    event = fields.ForeignKeyField('models.Event', related_name='project_event', null=True)

    def __str__(self):
        return f"{self.project}_{self.producer}_{self.responsible}"
