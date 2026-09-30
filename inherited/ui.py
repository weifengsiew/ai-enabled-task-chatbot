"""Display formatting for the inherited Bao application."""

from datetime import datetime
from typing import Any


def format_deadline(when: datetime) -> str:
    """Format a deadline date and optional time for display.

    Args:
        when: Deadline date and time to format.

    Returns:
        The date alone at midnight, otherwise the date and hour with am/pm.
    """
    if when.hour == 0 and when.minute == 0:
        return when.strftime("%b %d %Y")
    return when.strftime("%b %d %Y, ") + when.strftime("%I%p").lstrip("0").lower()


def format_task(task: dict[str, Any]) -> str:
    """Format a task's kind, completion state, description, and details.

    Args:
        task: Task data containing its kind and associated display fields.

    Returns:
        The formatted task text, without numbering, indentation, or notes.
    """
    box = "X" if task["done"] else " "
    if task["kind"] == "todo":
        return f'[T][{box}] {task["description"]}'
    elif task["kind"] == "deadline":
        due = datetime.fromisoformat(task["when"])
        formatted = format_deadline(due)
        return f'[D][{box}] {task["description"]} (by: {formatted})'
    elif task["kind"] == "event":
        return (
            f'[E][{box}] {task["description"]} '
            f'(from: {task["from"]} to: {task["to"]})'
        )
    else:
        return f'[R][{box}] {task["description"]} (every: {task["every"]})'


def show_added(task: dict[str, Any]) -> None:
    """Print the confirmation and formatted text for an added task.

    Args:
        task: Added task to display using the shared task formatter.

    Returns:
        None.
    """
    print("Added:")
    print(f"  {format_task(task)}")
