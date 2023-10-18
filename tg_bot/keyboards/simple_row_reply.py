from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton


def make_row_keyboard(items: list[str]) -> ReplyKeyboardMarkup:
    keyboard = [[KeyboardButton(text=item)] for item in items]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


def create_link(chat_id: int, project_name: str, flag: str):
    text = f"Присоединиться в проект: {project_name}"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=text,
                                  url=f'https://t.me/NAME_BOT?start={chat_id}_{flag}')]
        ]
    )
