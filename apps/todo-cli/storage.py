"""JSON persistence for the todo application."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Union


Todo = Dict[str, Any]
PathLike = Union[str, Path]


def _default_data_file() -> Path:
    """Return an OS-appropriate per-user data file location."""

    override = os.environ.get("TODO_DATA_FILE")
    if override:
        return Path(override).expanduser()

    if os.name == "nt":
        data_home = Path(
            os.environ.get("LOCALAPPDATA")
            or os.environ.get("APPDATA")
            or Path.home()
        )
    elif sys.platform == "darwin":
        data_home = Path.home() / "Library" / "Application Support"
    else:
        data_home = Path(
            os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share")
        )

    return data_home / "todo-cli" / "data.json"


DEFAULT_DATA_FILE = _default_data_file()
LEGACY_DATA_FILE = Path(__file__).with_name("data.json")


class StorageError(Exception):
    """Raised when todo data cannot be read or written safely."""


def load_todos(file_path: PathLike = DEFAULT_DATA_FILE) -> List[Todo]:
    """Load todos from a JSON file.

    A missing or empty file represents an empty todo list.
    """

    path = Path(file_path)

    if not path.exists():
        if path == DEFAULT_DATA_FILE and LEGACY_DATA_FILE.exists():
            path = LEGACY_DATA_FILE
        else:
            return []

    try:
        content = path.read_text(encoding="utf-8").strip()
    except OSError as exc:
        raise StorageError(f"无法读取数据文件：{exc}") from exc

    if not content:
        return []

    try:
        data = json.loads(content)
    except json.JSONDecodeError as exc:
        raise StorageError(
            f"数据文件不是有效的 JSON（第 {exc.lineno} 行，第 {exc.colno} 列）"
        ) from exc

    if not isinstance(data, list):
        raise StorageError("数据文件格式错误：最外层必须是 JSON 数组")

    _validate_todos(data)
    return data


def save_todos(
    todos: List[Todo], file_path: PathLike = DEFAULT_DATA_FILE
) -> None:
    """Save todos atomically so an interrupted write does not corrupt data."""

    _validate_todos(todos)
    path = Path(file_path)
    temporary_path = path.with_suffix(path.suffix + ".tmp")

    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path.write_text(
            json.dumps(todos, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        os.replace(str(temporary_path), str(path))
    except OSError as exc:
        try:
            temporary_path.unlink(missing_ok=True)
        except OSError:
            pass
        raise StorageError(f"无法保存数据文件：{exc}") from exc


def _validate_todos(todos: List[Todo]) -> None:
    seen_ids = set()

    for index, todo in enumerate(todos, start=1):
        if not isinstance(todo, dict):
            raise StorageError(f"数据文件格式错误：第 {index} 项必须是对象")

        todo_id = todo.get("id")
        task = todo.get("task")
        done = todo.get("done")

        if (
            not isinstance(todo_id, int)
            or isinstance(todo_id, bool)
            or todo_id <= 0
        ):
            raise StorageError(f"数据文件格式错误：第 {index} 项的 id 必须是正整数")
        if todo_id in seen_ids:
            raise StorageError(f"数据文件格式错误：任务 ID {todo_id} 重复")
        if not isinstance(task, str) or not task.strip():
            raise StorageError(f"数据文件格式错误：第 {index} 项的 task 不能为空")
        if not isinstance(done, bool):
            raise StorageError(f"数据文件格式错误：第 {index} 项的 done 必须是布尔值")

        seen_ids.add(todo_id)
