from tortoise.models import Model
from tortoise import fields


class User(Model):
    user_id = fields.BigIntField(pk=True)

    username = fields.CharField(max_length=255, null=True)

    def __str__(self):
        return f"{self.username}"
