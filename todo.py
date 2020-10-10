import done
import shared
import file
import click
import todo_domain as td
from todo_domain import Todos
from functools import partial, singledispatch
from typing import List


def _add_to_file(path: str, todo: str):
    existing = file.read_all_lines(path)
    updated = td.add_todo(existing, todo)
    file.write_all_lines(path, updated)

def _save_to_file(path: str, todos: List[Todos._Todo]):
    file.write_all_lines(path, [todo.item for todo in todos])

def get() -> List[Todos._Todo]:
    return Todos.create(file.read_all_lines('todo.txt'))

_add = partial(_add_to_file, 'todo.txt')
_save = partial(_save_to_file, 'todo.txt')

added = td.TodosAddedEventHandler()
added.subscribe(_add)

remaining = td.TodosRemainingEventHandler()
remaining.subscribe(_save)

completed = td.TodosCompletedEventHandler()
completed.subscribe(lambda todos: done.save_from_string([todo.item for todo in todos]))
completed.subscribe(lambda todos: shared.display(Todos.to_string(todos)))

purged = td.TodosPurgedEventHandler()
purged.subscribe(lambda todos: shared.display(Todos.to_string(todos)))

@singledispatch
def handle(event):
    print(f'Unregistered event type: [{type(event)}]')

# Python 3.7+ can use the type annotation of the first argument
@handle.register(td.TodosAddedEvent)
def _handle_added(event: td.TodosAddedEvent):
    added.on_next(event.args)

@handle.register(td.TodosRemainingEvent)
def _handle_remaining(event: td.TodosRemainingEvent):
    remaining.on_next(event.args)

@handle.register(td.TodosCompletedEvent)
def _handle_completed(event: td.TodosCompletedEvent):
    completed.on_next(event.args)

@handle.register(td.TodosPurgedEvent)
def _handle_purged(event: td.TodosPurgedEvent):
    purged.on_next(event.args)


@click.group()
def cli(): pass

@cli.command(name='s')
def show():
    shared.display(Todos.to_string(get()))

@cli.command(name='a')
@click.argument('todo_item', type=str)
def add_cli(todo_item: str):
    handle(td.TodosAddedEvent(todo_item))

@cli.command(name='r')
@click.argument('index_to_remove', type=int)
def get_by_days(index_to_remove):
    events = td.complete_todos(get(), index_to_remove)
    for event in events: handle(event)

@cli.command(name='p')
@click.argument('index_to_purge', type=int)
def get_by_weeks(index_to_purge):
    events = td.purge_todos(get(), index_to_purge)
    for event in events: handle(event)


if __name__ == "__main__":
    cli()
