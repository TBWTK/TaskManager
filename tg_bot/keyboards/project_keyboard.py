from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def inline_button_project_pr(items) -> InlineKeyboardMarkup:
    inline_keyboard = [InlineKeyboardButton(text=item.project.name,
                                            callback_data=f'ch_project_pr:{item.project.chat_id}') for item in items]
    return InlineKeyboardMarkup(inline_keyboard=[inline_keyboard])


choice_project = {
    'creating_or_viewing': ['Создать проект', 'Мои проекты'],
    'viewing': ['Проекты, где я ответственный', 'Проекты, где я админ'],
    'viewing_admin': ['Выгрузить отчет', 'Добавить админа', 'Добавить ответственного'],
    'viewing_responsible': ['Просмотр задач']
}
