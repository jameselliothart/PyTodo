import file
import todo_domain as td
from typing import List


PATH = 'todo.txt'


def add(path: str, todo: str):
    existing = file.read_all_lines(path)
    updated = td.add_todo(existing, todo)
    file.write_all_lines(path, updated)

def save(path: str, todos: List[td.Todos._Todo]):
    file.write_all_lines(path, [todo.item for todo in todos])

def get(path: str) -> List[td.Todos._Todo]:
    return td.Todos.create(file.read_all_lines(path))
