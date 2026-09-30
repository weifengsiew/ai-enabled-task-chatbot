"""Task-list operations for the inherited Bao application."""

from datetime import date, datetime
from typing import Any


class TaskNotFoundError(IndexError):
    """The requested task index is outside the current task list."""


def validate_task_index(tasks: list[dict[str, Any]], index: int) -> None:
    """Check that an index identifies a task without changing the list.

    Args:
        tasks: Current task list.
        index: Zero-based task index to validate.

    Returns:
        None.

    Raises:
        TaskNotFoundError: If the index is negative or outside the task list.
    """
    if index < 0 or index >= len(tasks):
        raise TaskNotFoundError(index)


def clear_completed(tasks: list[dict[str, Any]]) -> int:
    """Remove completed tasks in place and count the removals.

    Args:
        tasks: Task list to mutate, preserving the order of remaining tasks.

    Returns:
        The number of completed tasks removed.
    """
    before = len(tasks)
    tasks[:] = [task for task in tasks if not task["done"]]
    return before - len(tasks)


def find_tasks(tasks: list[dict[str, Any]], query: str) -> list[dict[str, Any]]:
    """Find tasks whose descriptions contain a query, ignoring case.

    Args:
        tasks: Task list to search without modifying it.
        query: Substring to match against task descriptions.

    Returns:
        A new list of matching task references in their original order.
    """
    return [task for task in tasks if query.casefold() in task["description"].casefold()]


def due_tasks(tasks: list[dict[str, Any]], wanted: date) -> list[dict[str, Any]]:
    """Select deadline tasks due on a calendar date without changing the list.

    Args:
        tasks: Task list to search.
        wanted: Calendar date to match against stored deadline dates.

    Returns:
        A new list of matching task references in their original order.
    """
    return [
        task
        for task in tasks
        if task["kind"] == "deadline"
        and datetime.fromisoformat(task["when"]).date() == wanted
    ]


def set_done(tasks: list[dict[str, Any]], index: int, done: bool) -> None:
    """Validate a task index and update its completion state in place.

    Args:
        tasks: Task list containing the task to update.
        index: Zero-based task index.
        done: Completion state to assign.

    Returns:
        None.

    Raises:
        TaskNotFoundError: If the index is negative or outside the task list.
    """
    validate_task_index(tasks, index)
    tasks[index]["done"] = done


def set_note(tasks: list[dict[str, Any]], index: int, note: str) -> None:
    """Validate a task index and replace its note in place.

    Args:
        tasks: Task list containing the task to update.
        index: Zero-based task index.
        note: Note text to assign without changing its whitespace.

    Returns:
        None.

    Raises:
        TaskNotFoundError: If the index is negative or outside the task list.
    """
    validate_task_index(tasks, index)
    tasks[index]["note"] = note


def delete_task(tasks: list[dict[str, Any]], index: int) -> dict[str, Any]:
    """Validate an index and remove its task from the list in place.

    Args:
        tasks: Task list to mutate.
        index: Zero-based index of the task to remove.

    Returns:
        The removed task for confirmation display.

    Raises:
        TaskNotFoundError: If the index is negative or outside the task list.
    """
    validate_task_index(tasks, index)
    return tasks.pop(index)


def add_todo(tasks: list[dict[str, Any]], description: str) -> dict[str, Any]:
    """Construct a to-do task and append it to the supplied list in place.

    Args:
        tasks: Task list to mutate.
        description: Parsed task description.

    Returns:
        The appended task, initially incomplete with an empty note.
    """
    task = {"kind": "todo", "description": description, "done": False, "note": ""}
    tasks.append(task)
    return task


def add_deadline(
    tasks: list[dict[str, Any]], description: str, when: datetime
) -> dict[str, Any]:
    """Construct a deadline task and append it to the supplied list in place.

    Args:
        tasks: Task list to mutate.
        description: Parsed task description.
        when: Parsed deadline datetime to store in ISO format.

    Returns:
        The appended task, initially incomplete with an empty note.
    """
    task = {
        "kind": "deadline",
        "description": description,
        "done": False,
        "note": "",
        "when": when.isoformat(),
    }
    tasks.append(task)
    return task
