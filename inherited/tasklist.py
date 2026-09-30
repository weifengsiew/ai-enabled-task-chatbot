"""Task-list operations for the inherited Bao application."""

from typing import Any


def validate_task_index(tasks: list[dict[str, Any]], index: int) -> None:
    """Check that an index identifies a task without changing the list.

    Args:
        tasks: Current task list.
        index: Zero-based task index to validate.

    Returns:
        None.

    Raises:
        IndexError: If the index is negative or outside the task list.
    """
    if index < 0 or index >= len(tasks):
        raise IndexError(index)


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
