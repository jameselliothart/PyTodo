import re
import os
import file
import done_domain as done
from datetime import datetime
from typing import List, Optional, Tuple


PATH = 'todo.done.txt'


# Python 3.7+ has `datetime.fromisoformat()`
def _parse_datetime(iso_date: str) -> datetime:
    return datetime.strptime(iso_date, "%Y-%m-%dT%H:%M:%S.%f")

# could add a print statement when parse fails
def try_parse(done_item: str) -> Optional[done.CompletedItem]:
    matches = re.match(r'^\[(?P<completedOn>.*)\] (?P<item>.*)', done_item)
    if matches:
        completed_on = _parse_datetime(matches.group('completedOn'))
        item = matches.group('item')
        return done.CompletedItem(item, completed_on)
    return None

def parse(done_item: str) -> done.CompletedItem:
    matches = re.match(r'^\[(?P<completedOn>.*)\] (?P<item>.*)', done_item)
    if matches:
        completed_on = _parse_datetime(matches.group('completedOn'))
        item = matches.group('item')
        return done.CompletedItem(item, completed_on)
    raise ValueError("`done_item` must be of format '[isodate] completed item'")

def _check_completed_since(completed_item: Optional[done.CompletedItem], completed_since: datetime) -> bool:
    return completed_since < completed_item.completed_on if completed_item else False

def get(path: str, completed_since: datetime) -> List[done.CompletedItem]:
    if not os.path.exists(path):
        return []
    with open(path) as f:
        return [
            parse(line.strip())
            for line in f.readlines()
            if _check_completed_since(try_parse(line), completed_since)
            ]

def save(path: str, completed_items: List[done.CompletedItem]) -> None:
    for completed_item in completed_items:
        file.append_line(path, str(completed_item))
