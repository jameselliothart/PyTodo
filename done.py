import shared
import file
import re
import click
import sqlite3
from contextlib import closing, contextmanager
from functools import partial
from datetime import datetime, timedelta
from typing import List, Optional


class CompletedItem():
    def __init__(self, item: str, completed_on: datetime = None) -> None:
        self.item = item
        self.completed_on = datetime.now() if not completed_on else completed_on

    def __str__(self) -> str:
        return f'[{self.completed_on.isoformat()}] {self.item}'

    @staticmethod
    def create_default(items: List[str]):
        return [CompletedItem(item) for item in items]

# Python 3.7+ has `datetime.fromisoformat()`
def _parse_datetime(iso_date: str) -> datetime:
    return datetime.strptime(iso_date, "%Y-%m-%dT%H:%M:%S.%f")

def try_parse(done_item: str) -> Optional[CompletedItem]:
    matches = re.match(r'^\[(?P<completedOn>.*)\] (?P<item>.*)', done_item)
    if matches:
        completed_on = _parse_datetime(matches.group('completedOn'))
        item = matches.group('item')
        return CompletedItem(item, completed_on)
    return None

def _start_of_day(date: datetime) -> datetime:
    return date.replace(hour=0, minute=0, second=0, microsecond=0)

def _start_of_week(date: datetime):
    return _start_of_day(date - timedelta(days=date.isoweekday()))

def days_ago(date: datetime, num_days: int) -> datetime:
    return _start_of_day(date - timedelta(days=num_days))

def weeks_ago(date: datetime, num_weeks: int) -> datetime:
    return _start_of_week(date - timedelta(days=7*num_weeks))

def _save_to_file(path: str, completed_items: List[str]) -> None:
    for completed_item in CompletedItem.create_default(completed_items):
        file.append_line(path, str(completed_item))

def _check_completed_since(completed_item: str, completed_since: datetime) -> bool:
    item = try_parse(completed_item)
    return completed_since < item.completed_on if item else False

def _get_from_file(path: str, completed_since: datetime) -> List[str]:
    return file.read_all_lines_filtered(path, lambda l: _check_completed_since(l, completed_since))

# https://www.digitalocean.com/community/tutorials/how-to-use-the-sqlite3-module-in-python-3
# https://docs.python.org/3.6/library/sqlite3.html#sqlite3-controlling-transactions
# https://stackoverflow.com/questions/1829872/how-to-read-datetime-back-from-sqlite-as-a-datetime-instead-of-string-in-python
# declare CompletedOn as TIMESTAMP and use detect_types to get back datetime
@contextmanager
def _cursor(db_path: str):
    with closing(sqlite3.connect(db_path, isolation_level=None, detect_types=sqlite3.PARSE_DECLTYPES)) as connection:
        with closing(connection.cursor()) as cursor:
            yield cursor

def _initialize_db(db_path: str):
    with _cursor(db_path) as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS CompletedItems (
                Id INTEGER PRIMARY KEY,
                CompletedOn TIMESTAMP,
                Item VARCHAR(255)
                )"""
            )

def _save_to_db(db_path: str, completed_items: List[str]):
    with _cursor(db_path) as cursor:
        for completed_item in CompletedItem.create_default(completed_items):
            cursor.execute(
                "INSERT INTO CompletedItems (CompletedOn, Item) VALUES (?, ?)",
                (completed_item.completed_on, completed_item.item)
                )

def _get_from_db(db_path: str, completed_since: datetime) -> List[CompletedItem]:
    with _cursor(db_path) as cursor:
        rows = cursor.execute(
            "SELECT CompletedOn, Item from CompletedItems WHERE CompletedOn > ?",
            (completed_since,)
            )
        return [CompletedItem(row[1], row[0]) for row in rows.fetchall()]

save = partial(_save_to_file, 'todo.done.txt')
get = partial(_get_from_file, 'todo.done.txt')


@click.group()
def cli(): pass

@cli.command(name='a')
@click.argument('completed_item', type=str)
def save_cli(completed_item: str):
    save([completed_item])

@cli.command(name='d')
@click.argument('number_of_days_ago', type=int)
def get_by_days(number_of_days_ago):
    completed_since = days_ago(datetime.now(), number_of_days_ago)
    shared.display(get(completed_since))

@cli.command(name='w')
@click.argument('number_of_weeks_ago', type=int)
def get_by_weeks(number_of_weeks_ago):
    completed_since = weeks_ago(datetime.now(), number_of_weeks_ago)
    shared.display(get(completed_since))


if __name__ == "__main__":
    cli()
