from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def inline_button_project_ev(items) -> InlineKeyboardMarkup:
    inline_keyboard = [InlineKeyboardButton(text=item.project.name,
                                            callback_data=f'ch_project_ev:{item.project.chat_id}') for item in items]
    return InlineKeyboardMarkup(inline_keyboard=[inline_keyboard])


def inline_button_responsible_ev(items) -> InlineKeyboardMarkup:
    inline_keyboard = [InlineKeyboardButton(text=f'{item.last_name} {item.first_name}',
                                            callback_data=f'resp:{item.player.user_id}')
                       for item in items]
    return InlineKeyboardMarkup(inline_keyboard=[inline_keyboard])


choice_event = {
    'event_task': ['Создать мероприятие', 'Создать задачу', 'Закрыть'],
    'type_notif': ['Только исполнителю', 'В чат проекта']

}


project_chat_id = {

}
