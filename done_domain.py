from datetime import datetime, timedelta
from typing import NamedTuple


class CompletedItem(NamedTuple):
    item: str
    completed_on: datetime

    def __str__(self) -> str:
        return f'[{self.completed_on.isoformat()}] {self.item}'


def create_default(item: str) -> CompletedItem:
    return CompletedItem(item, datetime.now())

def _start_of_day(date: datetime) -> datetime:
    return date.replace(hour=0, minute=0, second=0, microsecond=0)

def _start_of_week(date: datetime) -> datetime:
    return _start_of_day(date - timedelta(days=date.isoweekday()))

def days_ago(date: datetime, num_days: int) -> datetime:
    return _start_of_day(date - timedelta(days=num_days))

def weeks_ago(date: datetime, num_weeks: int) -> datetime:
    return _start_of_week(date - timedelta(days=7*num_weeks))
