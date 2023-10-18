from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def question_implementation(event_id: int) -> InlineKeyboardMarkup:
    inline_keyboard = [
        InlineKeyboardButton(text=f'Да', callback_data=f'event_done:{event_id}'),  # done
        InlineKeyboardButton(text=f'Нет', callback_data=f'event_not_done:{event_id}')  # done
    ]
    return InlineKeyboardMarkup(inline_keyboard=[inline_keyboard])


def request_postponement(event_id: int) -> InlineKeyboardMarkup:
    inline_keyboard = [
        InlineKeyboardButton(text=f'Да', callback_data=f'event_req_new_deadline:{event_id}'),  # don
        InlineKeyboardButton(text=f'Нет', callback_data=f'event_not_change:{event_id}')  # done
    ]
    return InlineKeyboardMarkup(inline_keyboard=[inline_keyboard])


def processing_postponement_request(event_id: int) -> InlineKeyboardMarkup:
    inline_keyboard = [
        [InlineKeyboardButton(text=f'Назначить новый срок', callback_data=f'event_new_deadline:{event_id}')],
        [InlineKeyboardButton(text=f'Не переносить срок', callback_data=f'event_not_change:{event_id}')]  # done
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


def event_validation(event_id: int) -> InlineKeyboardMarkup:
    inline_keyboard = [
        [InlineKeyboardButton(text=f'Подтвердить выполнение', callback_data=f'event_completed:{event_id}')],  # done
        [InlineKeyboardButton(text=f'Назначить новый срок', callback_data=f'event_new_deadline:{event_id}')]
    ]
    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)

