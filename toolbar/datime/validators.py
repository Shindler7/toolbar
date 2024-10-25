"""
Валидаторы, связанные с объектами datetime.
"""
import datetime as dt
from typing import Union, Tuple


def validate_any_datetime(date_time: Union[dt.datetime, dt.date, dt.time]
                          ) -> None:
    """
    Проверка, что date_time является любым объектом datetime: datetime, date,
    time.

    :param date_time: Проверяемый объект даты/времени.
    :raise TypeError: Если не является любым из ожидаемых объектов.
    """

    if not isinstance(date_time, (dt.datetime, dt.date, dt.time)):
        raise TypeError(f'объект должен быть datetime, date или time, '
                        f'получено: {type(date_time)}')


def validate_is_datetime(date: Union[dt.datetime, dt.date],
                         *,
                         allow_date: bool = False) -> None:
    """
    Проверка, что дата является datetime.datetime или datetime.date.

    :param date: Проверяемый объект даты.
    :param allow_date: Опция. Разрешает валидным считать как datetime, так и
                       date. По-умолчанию отключена, валидным считается только
                       datetime.
    :raise TypeError: Если не является datetime или date.
    """

    msg_type: str = 'datetime или date' if allow_date else 'datetime'
    check_types: Tuple[type, ...] = (
        (dt.datetime, dt.date) if allow_date else (dt.datetime,)
    )

    if not isinstance(date, check_types):
        raise TypeError(f'ожидается {msg_type}, получено: {type(date)}')


def validate_is_date(date: dt.date) -> None:
    """
    Проверка, что дата является datetime.date.

    :raise TypeError: Если не является date.
    """

    if not isinstance(date, dt.date):
        raise TypeError(f'ожидается datetime.date, получено: {type(date)}')


def validate_is_time(time: dt.time) -> None:
    """
    Проверка, что время является datetime.time.

    :param time: Проверяемый объект даты.
    :raise TypeError: Если не является time.
    """

    if not isinstance(time, dt.date):
        raise TypeError(f'Ожидается datetime.time, получено: {type(time)}')
