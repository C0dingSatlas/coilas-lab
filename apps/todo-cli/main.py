"""Command-line entry point for todo-cli."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import List, Optional

from storage import DEFAULT_DATA_FILE, StorageError, load_todos, save_todos
from todo import TodoError, add_todo, complete_todo, delete_todo


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="todo",
        description="一个简单的命令行待办事项工具",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = subparsers.add_parser("add", help="添加任务")
    add_parser.add_argument("task", help="任务内容")

    subparsers.add_parser("list", help="列出所有任务")

    done_parser = subparsers.add_parser("done", help="完成任务")
    done_parser.add_argument("id", type=int, help="任务 ID")

    delete_parser = subparsers.add_parser("delete", help="删除任务")
    delete_parser.add_argument("id", type=int, help="任务 ID")

    return parser


def main(
    argv: Optional[List[str]] = None,
    data_file: Path = DEFAULT_DATA_FILE,
) -> int:
    args = build_parser().parse_args(argv)

    try:
        todos = load_todos(data_file)

        if args.command == "add":
            created = add_todo(todos, args.task)
            save_todos(todos, data_file)
            print(f"已添加任务 #{created['id']}：{created['task']}")
            return 0

        if args.command == "list":
            print_todos(todos)
            return 0

        if args.command == "done":
            completed = complete_todo(todos, args.id)
            save_todos(todos, data_file)
            print(f"已完成任务 #{completed['id']}：{completed['task']}")
            return 0

        if args.command == "delete":
            deleted = delete_todo(todos, args.id)
            save_todos(todos, data_file)
            print(f"已删除任务 #{deleted['id']}：{deleted['task']}")
            return 0

    except (TodoError, StorageError) as exc:
        print(f"错误：{exc}")
        return 1

    return 1


def print_todos(todos: List[dict]) -> None:
    if not todos:
        print("暂无任务")
        return

    for todo in todos:
        status = "x" if todo.get("done") else " "
        print(f"[{status}] {todo.get('id')} - {todo.get('task', '')}")


if __name__ == "__main__":
    raise SystemExit(main())
