from datetime import datetime, timedelta, timezone
from config import TIME_ZONE
import pytz


async def time_zone():
    return timezone(timedelta(hours=TIME_ZONE))


async def time_now():
    timezone_value = await time_zone()
    return datetime.now(timezone_value)


async def get_timezone():
    timezone_value = str(await time_zone())
    if isinstance(timezone_value, str):
        # Если строка начинается с "UTC", пытаемся распарсить как смещение
        if timezone_value.startswith("UTC"):
            # Получаем смещение (например, +01:00 или -03:00)
            hours, minutes = map(int, timezone_value[4:].split(":"))
            sign = -1 if timezone_value[3] == '-' else 1
            offset = timedelta(hours=hours * sign, minutes=minutes * sign)

            # Возвращаем FixedOffset
            return pytz.FixedOffset(offset.total_seconds() / 60)
        else:
            # Если это строка с именем временной зоны
            return pytz.timezone(timezone_value)
    raise ValueError(f"Unknown timezone format: {timezone_value}")
