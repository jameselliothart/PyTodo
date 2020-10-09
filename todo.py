import done
import shared
import file
import click
from functools import partial, singledispatch
from rx.subject import Subject
from typing import Any, List, NamedTuple, Tuple


class Todos():
    class _Todo():
        def __init__(self, index: int, item: str) -> None:
            self.index = index
            self.item = item

        def __str__(self) -> str:
            return f'{self.index}. {self.item}'

    @staticmethod
    def create(todos: List[str]) -> List[_Todo]:
        return [Todos._Todo(index, item) for index, item in enumerate(todos)]


class TodosEvent(NamedTuple):
    args: Any

class TodosAddedEvent(TodosEvent):
    args: str

class TodosAddedEventHandler(Subject): pass

class TodosRemainingEvent(TodosEvent):
    args: List[Todos._Todo]

class TodosRemainingEventHandler(Subject): pass

class TodosCompletedEvent(TodosEvent):
    args: List[Todos._Todo]

class TodosCompletedEventHandler(Subject): pass

class TodosPurgedEvent(TodosEvent):
    args: List[Todos._Todo]

class TodosPurgedEventHandler(Subject): pass

# def _create(todos: List[str]) -> List[Todos._Todo]:
#     return [Todos._Todo(index, item) for index, item in enumerate(todos)]

def _to_string(todos: List[Todos._Todo]) -> List[str]:
    return [str(todo) for todo in todos] if todos else [f"No todos"]

def _add_todo(existing: List[str], todo: str) -> List[str]:
    new_todos = [todo]
    new_todos.extend(existing)
    return new_todos

def _partition_todos(todos: List[Todos._Todo], index: int) -> Tuple[List[Todos._Todo], List[Todos._Todo]]:
    partitioned: List[Todos._Todo] = []
    remaining: List[Todos._Todo] = []
    for todo in todos: (partitioned if todo.index == index else remaining).append(todo)
    return partitioned, remaining

def _complete_todos(todos: List[Todos._Todo], index: int) -> List[TodosEvent]:
    completed, remaining = _partition_todos(todos, index)
    return [TodosCompletedEvent(completed), TodosRemainingEvent(remaining)]

def _purge_todos(todos: List[Todos._Todo], index: int) -> List[TodosEvent]:
    purged, remaining = _partition_todos(todos, index)
    return [TodosPurgedEvent(purged), TodosRemainingEvent(remaining)]

def _add_to_file(path: str, todo: str):
    existing = file.read_all_lines(path)
    updated = _add_todo(existing, todo)
    file.write_all_lines(path, updated)

def _save_to_file(path: str, todos: List[Todos._Todo]):
    file.write_all_lines(path, [todo.item for todo in todos])

def get() -> List[Todos._Todo]:
    return Todos.create(file.read_all_lines('todo.txt'))

_add = partial(_add_to_file, 'todo.txt')
_save = partial(_save_to_file, 'todo.txt')

added = TodosAddedEventHandler()
added.subscribe(_add)

remaining = TodosRemainingEventHandler()
remaining.subscribe(_save)

completed = TodosCompletedEventHandler()
completed.subscribe(lambda todos: done.save([todo.item for todo in todos]))
completed.subscribe(lambda todos: shared.display(_to_string(todos)))

purged = TodosPurgedEventHandler()
purged.subscribe(lambda todos: shared.display(_to_string(todos)))

@singledispatch
def handle(event):
    print(f'Unregistered event type: [{type(event)}]')

@handle.register
def _(event: TodosAddedEvent):
    print(f'hi {event}')

# Python 3.7+ can use the type annotation of the first argument
@handle.register(TodosAddedEvent)
def _handle_added(event: TodosAddedEvent):
    added.on_next(event.args)

@handle.register(TodosRemainingEvent)
def _handle_remaining(event: TodosRemainingEvent):
    remaining.on_next(event.args)

@handle.register(TodosCompletedEvent)
def _handle_completed(event: TodosCompletedEvent):
    completed.on_next(event.args)

@handle.register(TodosPurgedEvent)
def _handle_purged(event: TodosPurgedEvent):
    purged.on_next(event.args)


@click.group()
def cli(): pass

@cli.command(name='s')
def show():
    shared.display(get())

@cli.command(name='a')
@click.argument('todo_item', type=str)
def add_cli(todo_item: str):
    handle(TodosAddedEvent(todo_item))

@cli.command(name='r')
@click.argument('index_to_remove', type=int)
def get_by_days(index_to_remove):
    events = _complete_todos(get(), index_to_remove)
    for event in events: handle(event)

@cli.command(name='p')
@click.argument('index_to_purge', type=int)
def get_by_weeks(index_to_purge):
    events = _purge_todos(get(), index_to_purge)
    for event in events: handle(event)


if __name__ == "__main__":
    cli()
