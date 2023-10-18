import re
from datetime import datetime, timedelta
from aiogram.filters import BaseFilter
from aiogram.types import Message


class TimeFormatFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return bool(re.match(r'^([0-1]\d|2[0-3]):([0-5]\d)$', message.text))


class DateFormatFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        date_pattern = r'^(0[1-9]|[12][0-9]|3[01])\.(0[1-9]|1[012])$'
        if not re.match(date_pattern, message.text):
            return False
        day, month = map(int, message.text.split('.'))
        current_year = datetime.now().year
        try:
            date_current_year = datetime(year=current_year, month=month, day=day)
            if date_current_year >= datetime.now():
                return True
            date_next_year = datetime(year=current_year + 1, month=month, day=day)
            return True
        except ValueError:
            return False
