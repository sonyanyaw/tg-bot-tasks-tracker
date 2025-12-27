from datetime import datetime, date, timedelta, time


def now_utc() -> datetime:
    return datetime.utcnow()


def today_date() -> date:
    return date.today()


def parse_time(value: str) -> time:
    try:
        return datetime.strptime(value, "%H:%M").time()
    except ValueError:
        raise ValueError("Invalid time format")


def combine_date_time(date, time_value: time):
    from datetime import datetime
    return datetime.combine(date, time_value)


from datetime import datetime, timezone
from pytz import timezone as pytz_timezone

async def detect_timezone_from_message(message):
    """
    Попытка определить таймзону пользователя по UTC-времени сообщения.
    Возвращает смещение в часах и примерную таймзону.
    """
    # Время, когда пользователь отправил сообщение
    message_time_utc = message.date  # datetime в UTC

    # Время на сервере UTC
    now_utc = datetime.now(timezone.utc)

    # Простейший способ: догадка по локальному времени
    # Например, считаем, что пользователь активен около 9:00 утра
    approximate_local_hour = 9
    offset_hours = approximate_local_hour - message_time_utc.hour

    # Ограничим offset до диапазона [-12, +14] часов
    if offset_hours < -12:
        offset_hours += 24
    elif offset_hours > 14:
        offset_hours -= 24

    # Формируем строку таймзоны для pytz
    tz_guess = f"Etc/GMT{('-' if offset_hours > 0 else '+')}{abs(offset_hours)}"
    return tz_guess


def format_time_delta(delta: timedelta) -> str:
    total_seconds = int(delta.total_seconds())
    past = total_seconds < 0
    total_seconds = abs(total_seconds)

    days, remainder = divmod(total_seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)

    parts = []
    if days:
        parts.append(f"{days} дн.")
    if hours:
        parts.append(f"{hours} ч.")
    if minutes:
        parts.append(f"{minutes} мин.")
    if not parts:
        parts.append(f"{seconds} сек.")

    text = " ".join(parts)
    return f"Просрочено на {text}" if past else f"Осталось {text} до задачи"
