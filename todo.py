import done
import shared
import todo_file
import click
import todo_domain as td
from functools import partial, singledispatch


def get(): return todo_file.get(todo_file.PATH)

add = partial(todo_file.add, todo_file.PATH)
save = partial(todo_file.save, todo_file.PATH)

added = td.TodosAddedEventHandler()
added.subscribe(add)

remaining = td.TodosRemainingEventHandler()
remaining.subscribe(save)

completed = td.TodosCompletedEventHandler()
completed.subscribe(lambda todos: done.save_from_string([todo.item for todo in todos]))
completed.subscribe(lambda todos: shared.display(todos))

purged = td.TodosPurgedEventHandler()
purged.subscribe(lambda todos: shared.display(todos))

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
    shared.display(get())

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
