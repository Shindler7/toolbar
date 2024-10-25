"""
Различные конвертеры datetime и дат.
"""
import datetime as dt
import os
from datetime import timedelta
from typing import Union, Literal

from toolbar.datime.timezones import (add_timezone, is_naive, get_utc_tz,
                                      get_timezone,
                                      are_eq_tz, local_now, since_time)
from toolbar.datime.validators import validate_is_datetime


def dt_or_str(date: Union[dt.datetime, dt.date, str],
              fmt: str = None) -> Union[dt.datetime, dt.date, str]:
    """
    При получении объекта datetime возвращает строку с датой, отформатированной
    по заданному формату. Если получает строку с датой, то возвращает datetime,
    опираясь на переданный формат.

    :param date: Объект datetime, datetime.date() или строка с датой.
    :param fmt: Шаблон для форматирования. Наиболее важен для трансформации из
                строки в datetime, так как должен точно соответствовать
                переданному формату даты. По-умолчанию применяется '%Y-%m-%d'.
    :raise TypeError: Если переданное значение не datetime и не str.
    """

    if fmt is None:
        fmt = '%Y-%m-%d'

    if isinstance(date, str):
        return dt.datetime.strptime(date, fmt)

    if isinstance(date, (dt.datetime, dt.date)):
        return date.strftime(fmt)

    raise TypeError(f'{date} должно быть строкой, date или datetime')


def convert_datetime_fmt(date: str,
                         *,
                         original_fmt: str,
                         target_fmt: str) -> str:
    """
    Получает в текстовом варианте дату и её маску, и переводит в формат по
    целевой маске. Например: "2024-09-15 09:56:35" в "09:56:35 15.09.2024".

    *Важно*: стоит обратить внимание, что временная зона не учитывается.
    Исключения, связанные с неверными входными данными, не обрабатываются.

    :param date: Текстовый вариант даты для обмена.
    :parameter original_fmt: Формат даты и времени в исходном варианте.
    :parameter target_fmt: Требуемый формат даты и времени.
    """

    if not isinstance(date, str):
        raise TypeError('{date} должно быть строкой')

    intermediate_convert: dt.datetime = dt_or_str(date, original_fmt)

    return dt_or_str(intermediate_convert, target_fmt)


def convert_iso_date(date: Union[dt.datetime, str],
                     *,
                     sep_time: str = 'T',
                     timespec: Literal['auto', 'hours', 'minutes', 'seconds',
                     'milliseconds', 'microseconds'] = 'seconds',
                     naive_tz='UTC') -> dt.datetime or str:
    """
    Конвертер даты в формате ISO *(2024-06-01T14:41:36-08:00)*.

    Возвращает для строкового представления datetime, а для datetime строку.
    Если дата наивная (без часового пояса), можно добавить временную зону,
    по-умолчанию предоставляется UTC.

    :param date: Обрабатываемая дата (строка или datetime).
    :param sep_time: Разделитель даты и времени (любое значение).
    :param timespec: Ограничитель по длине (варианты: 'auto', 'hours',
                     'minutes', 'seconds', 'milliseconds', 'microseconds').
                     По-умолчанию *'seconds'*.
    :param naive_tz: Если конвертируемая дата наивная (naive), добавляется
                     часовой пояс, если указано. По-умолчанию UTC. Если None,
                     действий с timezone не производится.
    :raise TypeError: В случае передачи необрабатываемого типа данных.
    """

    def set_tz(d: dt.datetime) -> dt.datetime:
        if is_naive(d) and naive_tz is not None:
            return add_timezone(d, tz=naive_tz)
        return d

    # Дата в строке.
    if isinstance(date, str):
        date = dt.datetime.fromisoformat(date)
        return set_tz(date)

    # Объект datetime.
    if isinstance(date, dt.datetime):
        return set_tz(date).isoformat(sep_time, timespec)

    raise TypeError(f'{date} должно быть строкой или datetime')


def calc_date(date: Union[dt.datetime, dt.date],
              *,
              d: Literal['+', '-'],
              **period) -> dt.datetime:
    """
    Вычисление новой даты на основе timedelta.

    :param date: Объект datetime.date или datetime.datetime.
    :param d: Направление вычисления.
    :param period: Параметры для timedelta: days, weeks, hours, minutes,
                   seconds и другие.
    :return: Объект datetime с новой датой.
    :raise TypeError: Если для вычисления передан неверный объект даты.
    :raise ValueError: Если неправильно указано направление вычисления.
    :raise AttributeError: Если не указаны атрибуты для timedelta.
    """

    validate_is_datetime(date, allow_date=True)

    if d not in ('+', '-'):
        raise ValueError(f'Направление {d} может быть + или -')
    if not period:
        raise AttributeError('Отсутствуют аттрибуты period')

    time_delta: dt.timedelta = timedelta(**period)
    result: dt.datetime = date + time_delta if d == '+' else date - time_delta

    return result


def make_datetime(*,
                  year: int = None,
                  month: int = None,
                  day: int = None,
                  hour: int,
                  minute: int = 0,
                  second: int = 0,
                  tz=None) -> dt.datetime:
    """
    Конструктор для ручного или частично автоматического создания объекта
    datetime с предустановленными временными данными.

    **Если год, месяц и день не переданы**, то используются текущие в той же
    часовой зоне.

    **Временная зона** по-умолчанию: UTC.
    """

    if tz is None:
        tz = get_utc_tz()

    today: dt.datetime = add_timezone(local_now(), tz=tz)
    d_time: dt.datetime = dt.datetime(
        year=today.year if year is None else year,
        month=today.month if month is None else month,
        day=today.day if day is None else day,
        hour=hour,
        minute=minute,
        second=second
    )

    return add_timezone(d_time, tz=tz)


def seconds_since_datetime(*,
                           since: dt.datetime = None,
                           end: dt.datetime) -> int:
    """
    Вычисляет время в секундах между датами (если начальная не указана, то
    используется по-умолчанию начало эпохи: 1 января 1970 года, 00:00).

    Временные зоны должны быть предустановлены. Для избежания ошибок у
    заказчиков из-за обработки функцией временных зон эти манипуляции здесь
    не осуществляются. За исключением since_time по-умолчанию. Для неё
    выставляется временная зона end_time.

    :param since: Опционально. Время отсчёта. Если не установлено,
                       применяется время начала эпохи UNIX. Должна быть
                       установлена временная зона. При отсутствии выбрасывается
                       исключение.
    :param end: Конечное время в формате datetime. Должна быть установлена
                     временная зона, при её отсутствии вызывается исключение.
    :return: Время в секундах между двумя временными точками.
    """

    validate_is_datetime(end)

    if since is None:
        since: dt.datetime = dt.datetime(1970, 1, 1)
        tz_info = get_timezone(end)
        if tz_info:
            since = add_timezone(since, tz=tz_info)
    else:
        validate_is_datetime(since)

    if not are_eq_tz(since, end):
        raise ValueError('Временные зоны since и end разные')

    diff = end - since
    return int(diff.total_seconds())


def seconds_since_constructor(*,
                              since: dt.datetime = None,
                              end_year: int = None,
                              end_month: int = None,
                              end_day: int = None,
                              end_hour: int,
                              end_minute: int = 0,
                              end_second: int = 0,
                              tz=None) -> int:
    """
    Расширенная версия функции seconds_since_datetime, где конечное время
    формируется с помощью функции, а не через передачу собранного datetime.

    **Временная зона** собранной даты копируется от *since*.

    Верность предоставленных цифр не проверяется. Ошибки конструктора напрямую
    транслируются заказчику.

    :param since: Опционально. Точка отсчёта. Если не указано, тогда время
                  с начала эпохи.
    :param end_year: Опционально. Год конечной временной точки. По-умолчанию,
                     текущий год.
    :param end_month: Опционально. Месяц конечной временной точки. По-умолчанию
                      текущий месяц.
    :param end_day: Опционально. День конечной временной точки. По-умолчанию
                    текущий день.
    :param end_hour: Час конечной временной точки.
    :param end_minute: Минута конечной временной точки.
    :param end_second: Секунда конечной временной точки.
    :param tz: Опционально, для случаев, когда *since* использует значение
               по-умолчанию. Если *tz* передан, то и *since* и *end* получают
               эту временную зону. Если нет, тогда *end* получает временную
               зону, которая выставлена для *since* (UTC).
    :return: Время в секундах между двумя временными точками.
    """

    if since is None:
        since = since_time()
    else:
        validate_is_datetime(since, allow_date=True)

    # Выравнивание временных зон.
    if tz is None:
        tz_info = get_timezone(since)
    else:
        tz_info = tz
        since = add_timezone(since, tz=tz_info)

    constructor: dt.datetime = make_datetime(
        year=end_year,
        month=end_month,
        day=end_day,
        hour=end_hour,
        minute=end_minute,
        second=end_second,
        tz=tz_info
    )

    return seconds_since_datetime(since=since, end=constructor)


def file_modified_time(filepath: str, *, tz=None) -> dt.datetime:
    """
    Предоставляет время последнего изменения файла в секундах с начала эпохи.
    Применяется часовая зона UTC.

    :param filepath: Полный путь к расположению файла.
    :param tz: Опционально. Временная зона. Если не установлено, то UTC.
    """

    if tz is None:
        tz = get_utc_tz()

    file_mtime = os.path.getmtime(filepath)
    modified: dt.datetime = dt.datetime.fromtimestamp(file_mtime, get_utc_tz())

    return add_timezone(modified, tz=tz)
