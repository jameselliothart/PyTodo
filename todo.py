import done
from file import read_all_lines
import shared
import file
import click
from functools import partial, singledispatch
from rx.subject import Subject
from typing import Any, List, NamedTuple, Tuple


class Todo(NamedTuple):
    idx: int
    item: str

class TodoEvent(NamedTuple):
    args: Any

class TodosAddedEvent(TodoEvent):
    args: str

class TodosAddedEventHandler(Subject): pass

class TodosRemainingEvent(TodoEvent):
    args: List[Todo]

class TodosRemainingEventHandler(Subject): pass

class TodosCompletedEvent(TodoEvent):
    args: List[Todo]

class TodosCompletedEventHandler(Subject): pass

class TodosPurgedEvent(TodoEvent):
    args: List[Todo]

class TodosPurgedEventHandler(Subject): pass

def _create(todos: List[str]) -> List[Todo]:
    return [Todo(index, item) for index, item in enumerate(todos)]

def _to_string(todos: List[Todo]) -> List[str]:
    return [f"{todo.idx}. {todo.item}" for todo in todos] if todos else [f"No todos"]

def _add_todo(existing: List[str], todo: str) -> List[str]:
    new_todos = [todo]
    new_todos.extend(existing)
    return new_todos

def _partition_todos(todos: List[Todo], index: int) -> Tuple[List[Todo], List[Todo]]:
    partitioned: List[Todo] = []
    remaining: List[Todo] = []
    for todo in todos: (partitioned if todo.idx == index else remaining).append(todo)
    return partitioned, remaining

def _complete_todos(todos: List[Todo], index: int) -> List[TodoEvent]:
    completed, remaining = _partition_todos(todos, index)
    return [TodosCompletedEvent(completed), TodosRemainingEvent(remaining)]

def _purge_todos(todos: List[Todo], index: int) -> List[TodoEvent]:
    purged, remaining = _partition_todos(todos, index)
    return [TodosPurgedEvent(purged), TodosRemainingEvent(remaining)]

def _add_to_file(path: str, todo: str):
    existing = file.read_all_lines(path)
    updated = _add_todo(existing, todo)
    file.write_all_lines(path, updated)

def _save_to_file(path: str, todos: List[Todo]):
    file.write_all_lines(path, [todo.item for todo in todos])

def get():
    file.read_all_lines('todo.txt')

_add = partial(_add_to_file, 'todo.txt')
_save = partial(_save_to_file, 'todo.txt')

added = TodosAddedEventHandler()
added.subscribe(_add)

remaining = TodosRemainingEventHandler()
remaining.subscribe(_save)

completed = TodosCompletedEventHandler()
completed.subscribe(lambda todos: done.save([done.CompletedItem(todo.item) for todo in todos]))
completed.subscribe(lambda todos: shared.display(_to_string(todos)))

purged = TodosPurgedEventHandler()
completed.subscribe(lambda todos: shared.display(_to_string(todos)))

@singledispatch
def _handle(event):
    print(f'Unregistered event type: [{type(event)}]')

@_handle.register
def _handle_added(event: TodosAddedEvent):
    added.on_next(event.args)

@_handle.register
def _handle_remaining(event: TodosRemainingEvent):
    remaining.on_next(event.args)

@_handle.register
def _handle_completed(event: TodosCompletedEvent):
    completed.on_next(event.args)

@_handle.register
def _handle_purged(event: TodosPurgedEvent):
    purged.on_next(event.args)


@click.group()
def cli(): pass

@cli.command()
def show():
    shared.display(get())

@cli.command(name='a')
@click.argument('todo_item', type=str)
def add_cli(todo_item: str):
    _add(todo_item)

@cli.command(name='r')
@click.argument('index_to_remove', type=int)
def get_by_days(index_to_remove):
    _handle(_com)

@cli.command(name='p')
@click.argument('number_of_weeks_ago', type=int)
def get_by_weeks(number_of_weeks_ago):
    completed_since = weeks_ago(datetime.now(), number_of_weeks_ago)
    shared.display(get(completed_since))


if __name__ == "__main__":
