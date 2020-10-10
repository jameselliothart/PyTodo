from rx.subject import Subject
from typing import List, Tuple, NamedTuple, Any


class Todos():
    class _Todo(NamedTuple):
        idx : int
        item : str

        def __str__(self) -> str:
            return f'{self.idx}. {self.item}'

    @staticmethod
    def create(todos: List[str]) -> List[_Todo]:
        return [Todos._Todo(index, item) for index, item in enumerate(todos)]

    @staticmethod
    def to_string(todos: List[_Todo]) -> List[str]:
        return [str(todo) for todo in todos] if todos else [f"No todos"]

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

def add_todo(existing: List[str], todo: str) -> List[str]:
    new_todos = [todo]
    new_todos.extend(existing)
    return new_todos

def _partition_todos(todos: List[Todos._Todo], index: int) -> Tuple[List[Todos._Todo], List[Todos._Todo]]:
    partitioned: List[Todos._Todo] = []
    remaining: List[Todos._Todo] = []
    for todo in todos: (partitioned if todo.idx == index else remaining).append(todo)
    return partitioned, remaining

def complete_todos(todos: List[Todos._Todo], index: int) -> List[TodosEvent]:
    completed, remaining = _partition_todos(todos, index)
    return [TodosCompletedEvent(completed), TodosRemainingEvent(remaining)]

def purge_todos(todos: List[Todos._Todo], index: int) -> List[TodosEvent]:
    purged, remaining = _partition_todos(todos, index)
    return [TodosPurgedEvent(purged), TodosRemainingEvent(remaining)]
