"""Business rules for managing todos."""

from __future__ import annotations

from typing import Any, Dict, List


Todo = Dict[str, Any]


class TodoError(Exception):
    """Base exception for invalid todo operations."""


class TodoNotFoundError(TodoError):
    """Raised when a todo id does not exist."""


def add_todo(todos: List[Todo], task: str) -> Todo:
    """Create and append a todo, then return it."""

    normalized_task = task.strip()
    if not normalized_task:
        raise TodoError("任务内容不能为空")

    todo = {
        "id": _next_id(todos),
        "task": normalized_task,
        "done": False,
    }
    todos.append(todo)
    return todo


def complete_todo(todos: List[Todo], todo_id: int) -> Todo:
    """Mark a todo as completed and return it."""

    todo = _find_todo(todos, todo_id)
    todo["done"] = True
    return todo


def delete_todo(todos: List[Todo], todo_id: int) -> Todo:
    """Remove a todo and return the removed item."""

    todo = _find_todo(todos, todo_id)
    todos.remove(todo)
    return todo


def _find_todo(todos: List[Todo], todo_id: int) -> Todo:
    for todo in todos:
        if todo.get("id") == todo_id:
            return todo
    raise TodoNotFoundError(f"没有找到 ID 为 {todo_id} 的任务")


def _next_id(todos: List[Todo]) -> int:
    ids = [
        todo["id"]
        for todo in todos
        if isinstance(todo.get("id"), int) and not isinstance(todo.get("id"), bool)
    ]
    return max(ids, default=0) + 1
