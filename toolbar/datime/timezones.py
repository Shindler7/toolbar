"""
Методы для работы с временными зонами. Опирается на pytz.
"""
import datetime as dt
from typing import Union

import pytz
from pytz.tzinfo import BaseTzInfo

from toolbar.datime.validators import validate_is_datetime


def add_timezone(date: dt.datetime,
                 *,
                 tz: Union[str, dt.timezone, BaseTzInfo] = None
                 ) -> dt.datetime:
    """
    Добавляет часовую зону к объекту datetime.

    :param date: Объект datetime без часовой зоны.
    :param tz: Часовая зона (строка или объект timezone), по умолчанию UTC.
    """

    if tz is None:
        tz = get_utc_tz()

    if tz is dt.timezone.utc:
        # Сохраняем utc datetime
        return (date.replace(tzinfo=tz)
                if is_naive(date) else date.astimezone(tz))

    if isinstance(tz, str):
        tz = pytz.timezone(tz)

    return tz.localize(date) if is_naive(date) else date.astimezone(tz)


def get_timezone(date: dt.datetime) -> Union[str, dt.timezone, None]:
    """
    Получает текстовое значение временной зоны из объекта datetime.

    :param date: Объект datetime для анализа.
    :return: Текстовое значение временной зоны или ничего, если её нет.
    """

    if not isinstance(date, dt.datetime):
        raise TypeError('атрибут date должен быть datetime')

    if is_naive(date):
        return None

    tz_info = date.tzinfo

    if tz_info is dt.timezone.utc:
        return tz_info

    if hasattr(tz_info, 'zone'):
        return tz_info.zone

    raise ValueError('неизвестный тип временной зоны')


def are_eq_tz(*date: dt.datetime) -> bool:
    """
    Проверяет эквивалентно ли состояние временных зон у всех переданных
    объектов datetime. Эквивалентным считается как идентичное tz
    (если точнее смещение), либо отсутствие.

    :param date: Объекты datetime для сравнения.
    :return: Логический тип.
    """

    if len(date) < 2:
        raise ValueError('атрибутов date должно быть 2 и более')

    if not all(isinstance(d, dt.datetime) for d in date):
        raise TypeError('объекты date должны быть datetime')

    return all(date[0].utcoffset() == d.utcoffset() for d in date)


def get_utc_tz():
    utc = 'UTC'
    return pytz.timezone(utc)


def get_moscow_tz():
    moscow = 'Europe/Moscow'
    return pytz.timezone(moscow)


def local_now() -> dt.datetime:
    """
    Возвращает объект datetime с локальным временем и часовой зоной.
    """

    current_time = dt.datetime.now()

    return current_time.astimezone()


def utc_now():
    """
    Текущее время UTC.
    """

    return add_timezone(local_now(), tz=get_utc_tz())


def set_moscow_time(date: dt.datetime = None) -> dt.datetime:
    """
    Преобразует часовую зону date в московское время.

    :param date: Объект datetime для обработки.
    """

    validate_is_datetime(date, allow_date=True)

    return add_timezone(date, tz=get_moscow_tz())


def moscow_now() -> dt.datetime:
    """
    Текущее московское время.
    """

    return add_timezone(local_now(), tz=get_moscow_tz())


def since_time() -> dt.datetime:
    """
    Дата начала эпохи во временной зоне UTC.
    """

    s_time: dt.datetime = dt.datetime(year=1970, month=1, day=1,
                                      hour=0, minute=0, second=0)

    return add_timezone(s_time, tz=get_utc_tz())


def str_moscow_now(fmt='%d.%m.%Y %H:%M:%S') -> str:
    """
    Возвращает текстовое локализованное представление текущих времени и даты
    по Москве.

    :param fmt: Формат представления даты и времени.
    """

    return moscow_now().strftime(fmt)


def is_naive(date: dt.datetime) -> bool:
    """
    Возвращает установлено ли значение временной зоны для объекта datetime.

    :param date: Объект datetime для проверки.
    :return: Логический тип.
    """

    return date.utcoffset() is None
