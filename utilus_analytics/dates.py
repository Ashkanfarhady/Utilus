from __future__ import annotations

from calendar import monthrange
from datetime import date


def month_key(value: date) -> str:
    return value.strftime("%Y-%m")


def month_start(value: date) -> date:
    return date(value.year, value.month, 1)


def month_end(value: date) -> date:
    return date(value.year, value.month, monthrange(value.year, value.month)[1])


def add_months(value: date, months: int) -> date:
    month_index = value.month - 1 + months
    year = value.year + month_index // 12
    month = month_index % 12 + 1
    day = min(value.day, monthrange(year, month)[1])
    return date(year, month, day)


def iter_month_starts(start: date, end: date) -> list[date]:
    current = month_start(start)
    stop = month_start(end)
    months: list[date] = []
    while current <= stop:
        months.append(current)
        current = add_months(current, 1)
    return months
