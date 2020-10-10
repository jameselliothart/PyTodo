import done
import sqlite3
from datetime import datetime
from typing import List
from contextlib import contextmanager, closing


DB_PATH = 'done.db'

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
        for completed_item in done.CompletedItem.create_default(completed_items):
            cursor.execute(
                "INSERT INTO CompletedItems (CompletedOn, Item) VALUES (?, ?)",
                (completed_item.completed_on, completed_item.item)
                )

def _get_from_db(db_path: str, completed_since: datetime) -> List[done.CompletedItem]:
    with _cursor(db_path) as cursor:
        rows = cursor.execute(
            "SELECT CompletedOn, Item from CompletedItems WHERE CompletedOn > ?",
            (completed_since,)
            )
        return [done.CompletedItem(row[1], row[0]) for row in rows.fetchall()]
