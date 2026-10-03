"""Loading and saving task data."""

import json
from datetime import date, time
from pathlib import Path
from typing import Any, cast

from .task import DeadlineTask, EventTask, RecurringTask, Task, TodoTask

DATA_FILE = Path("data/tasks.json")


def save_tasks(tasks: list[Task], path: Path = DATA_FILE) -> None:
    """
    Saves tasks as JSON, creating the destination directory if needed.

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
    Loads tasks from JSON and reconstructs their concrete task classes.

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
    Reconstructs one concrete task from its serialized record.

    Args:
    -----
    record (dict[str, Any]): One saved task record.

    Returns:
    --------
    Task: The matching concrete task instance.
    """
    task_type = record["type"]
    common = {
        "done": record["done"],
        "note": record["note"],
    }

    if task_type == "todo":
        return TodoTask(record["description"], **common)

    if task_type == "deadline":
        due_date = record.get("due_date")
        due_time = record.get("due_time")
        return DeadlineTask(
            record["description"],
            date.fromisoformat(due_date) if due_date is not None else None,
            time.fromisoformat(due_time) if due_time is not None else None,
            **common,
        )

    if task_type == "event":
        return EventTask(
            record["description"],
            record.get("start"),
            record.get("end"),
            **common,
        )

    if task_type == "recurring":
        return RecurringTask(record["description"], record.get("day"), **common)

    raise ValueError(f"Unknown task type: {task_type}")
