from tg_bot.models.models import User, Participants, Project


async def create_user(id_user: int, username: str):
    user = await User.get_or_none(user_id=id_user)
    if user is None:
        user = User(user_id=id_user, username=username)
        await user.save()
        return True
    else:
        return False


async def check_user_from_project(id_user: int, project_chat_id: int):
    user, _ = await User.get_or_create(user_id=id_user)
    project, _ = await Project.get_or_create(chat_id=project_chat_id)
    check_player = await Participants.get_or_none(player=user, project=project)
    if check_player is None:
        check_player = Participants(player=user, project=project, is_responsible=True)
        await check_player.save()
        return True
    else:
        return False


async def update_status(id_user: int, project_chat_id: int, flag):
    user, _ = await User.get_or_create(user_id=id_user)
    project, _ = await Project.get_or_create(chat_id=project_chat_id)
    if flag == 'admin':
        part = await Participants.get_or_none(player=user, project=project)
        if part is not None:
            part.is_admin = True
            await part.save()
            return True
        return False
    else:
        part = await Participants.get_or_none(player=user, project=project)
        if part is not None:
            part.is_responsible = True
            await part.save()
            return True
        return False


async def add_user_name(id_user: int, project_chat_id: int, first_name: str, last_name: str):
    user, _ = await User.get_or_create(user_id=id_user)
    project, _ = await Project.get_or_create(chat_id=project_chat_id)
    updated, created = await Participants.update_or_create(
        player=user,
        project=project,
        defaults={"first_name": first_name,
                  "last_name": last_name}

    )
    if not created:
        await updated.save()
        return True
    else:
        return False
