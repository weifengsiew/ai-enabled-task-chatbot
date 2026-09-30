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


def format_task_summary(task: dict[str, Any]) -> str:
    """Format a task's completion box and description.

    Args:
        task: Task data containing its completion state and description.

    Returns:
        The completion box and description, without numbering or indentation.
    """
    box = "X" if task["done"] else " "
    return f'[{box}] {task["description"]}'


def show_tasks(tasks: list[dict[str, Any]]) -> None:
    """Print the numbered task list and notes, or the empty-list message.

    Args:
        tasks: Tasks to display in their supplied order.

    Returns:
        None.
    """
    if not tasks:
        print("Nothing on your plate.")
    else:
        for number, task in enumerate(tasks, 1):
            print(f"{number}.{format_task(task)}")
            if task["note"]:
                print(f'   Note: {task["note"]}')


def show_tasks_left(count: int) -> None:
    """Print the remaining task count.

    Args:
        count: Number of tasks remaining in the list.

    Returns:
        None.
    """
    print(f"{count} tasks left.")


def show_marked(task: dict[str, Any]) -> None:
    """Print confirmation of a task's updated completion state.

    Args:
        task: Updated task containing its completion state and description.

    Returns:
        None.
    """
    print("Done:" if task["done"] else "Not done:")
    print(f"  {format_task_summary(task)}")


def show_noted(task: dict[str, Any]) -> None:
    """Print confirmation of a task's updated note.

    Args:
        task: Updated task containing its description and note.

    Returns:
        None.
    """
    print("Noted:")
    print(f'  {task["description"]}')
    print(f'  Note: {task["note"]}')


def show_deleted(task: dict[str, Any], remaining_count: int) -> None:
    """Print the deleted task's description and remaining task count.

    Args:
        task: Removed task containing its description.
        remaining_count: Number of tasks remaining after deletion.

    Returns:
        None.
    """
    print("Deleted:")
    print(f'  {task["description"]}')
    show_tasks_left(remaining_count)
