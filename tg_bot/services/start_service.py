from tg_bot.models.models import User


async def create_user(id_user: int, username: str):
    user = await User.get_or_none(user_id=id_user)
    if user is None:
        user = User(user_id=id_user, username=username)
        await user.save()
        return True
    else:
        return False
