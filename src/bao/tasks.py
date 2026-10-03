"""Define the Tasks class and task persistence helpers."""

from __future__ import annotations

import json
from collections.abc import Iterator
from datetime import datetime
from pathlib import Path
from typing import Any, cast

from .task import DeadlineTask, EventTask, RecurringTask, Task, TodoTask

DATA_FILE = Path("data/tasks.json")


def save_tasks(tasks: list[Task], path: Path = DATA_FILE) -> None:
    """
    Save tasks as JSON, creating the destination directory if needed.

    Args:
    -----
    tasks (list[Task]): The mixed task list to serialize.
    path (Path): The destination JSON file.

    Returns:
    --------
    None.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    records = [task.to_dict() for task in tasks]
    path.write_text(json.dumps(records, indent=2), encoding="utf-8")


def load_tasks(path: Path = DATA_FILE) -> list[Task]:
    """
    Load tasks from JSON and reconstruct their concrete task classes.

    Args:
    -----
    path (Path): The source JSON file.

    Returns:
    --------
    list[Task]: The loaded mixed task list.
    """
    if not path.exists():
        save_tasks([], path)
        return []

    records = cast(list[dict[str, Any]], json.loads(path.read_text(encoding="utf-8")))
    return [_task_from_record(record) for record in records]


def _task_from_record(record: dict[str, Any]) -> Task:
    """
    Reconstruct one concrete task from its serialized record.

    Args:
    -----
    record (dict[str, Any]): One saved task record.

    Returns:
    --------
    Task: The matching concrete task instance.
    """
    task_type = record["task_type"]
    common = {
        "done": record["done"],
        "note": record["note"],
    }

    if task_type == "todo":
        return TodoTask(record["description"], **common)

    if task_type == "deadline":
        due_datetime = record.get("due_datetime")
        return DeadlineTask(
            record["description"],
            datetime.fromisoformat(due_datetime) if due_datetime is not None else None,
            **common,
        )

    if task_type == "event":
        return EventTask(
            record["description"],
            (
                datetime.fromisoformat(record["start_datetime"])
                if record.get("start_datetime") is not None
                else None
            ),
            (
                datetime.fromisoformat(record["end_datetime"])
                if record.get("end_datetime") is not None
                else None
            ),
            **common,
        )

    if task_type == "recurring":
        return RecurringTask(
            record["description"], record.get("recurrence_rule"), **common
        )

    raise ValueError(f"Unknown task type: {task_type}")


class Tasks:
    """Owns the mixed task list and its state-changing operations."""

    def __init__(self) -> None:
        """Load the saved mixed task list."""
        # State
        self._items: list[Task] = load_tasks()

    def save(self) -> None:
        """Persist the current task list."""
        save_tasks(self._items)

    def append(self, task: Task) -> None:
        """Append a task to the task list."""
        self._items.append(task)

    def __iter__(self) -> Iterator[Task]:
        """Iterate over the tasks in the task list."""
        return iter(self._items)

    def __len__(self) -> int:
        """Return the number of tasks in the task list."""
        return len(self._items)

    def __getitem__(self, index: int) -> Task:
        """Return the task at the requested zero-based index."""
        return self._items[index]

    def pop(self, index: int) -> Task:
        """Remove and return the task at the requested zero-based index."""
        return self._items.pop(index)
