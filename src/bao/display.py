"""Shared task display and lookup helpers."""

from __future__ import annotations

from collections.abc import Iterable

from .task import Task
from .tasks import Tasks


def _number_tasks_for_display(tasks: Iterable[object]) -> list[str]:
    """
    Format tasks with one-based display numbering.

    Args:
    -----
    tasks: The tasks to format.

    Returns:
    --------
    list[str]: The formatted task strings.
    """

    return [f"{number}. {task}" for number, task in enumerate(tasks, start=1)]


def _format_missing_task_message(tasks: Tasks, task_number: int) -> str:
    """
    Format guidance for a missing task number.

    Args:
    -----
    tasks: The current task collection.
    task_number: The requested task number.

    Returns:
    --------
    str: The guidance message for the missing task.
    """

    if len(tasks) > 0:
        message = f"Choose a number from 1 to {len(tasks)}."
    else:
        message = "There are no tasks yet."
    missing_task_message = f"No task {task_number}. {message}"
    return missing_task_message


def _get_task_by_number(tasks: Tasks, task_number: int) -> Task | None:
    """
    Return a task by its number, if it exists.

    Args:
    -----
    tasks: The current task collection.
    task_number: The one-based task number to find.

    Returns:
    --------
    Task | None: The matching task, or None if the number is invalid.
    """

    if 1 <= task_number <= len(tasks):
        return tasks[task_number - 1]
    return None
