"""Command handlers extracted from the inherited Bao input loop."""

from pathlib import Path
from typing import Any

if __package__:
    from .parser import (
        parse_deadline,
        parse_delete,
        parse_due,
        parse_event,
        parse_find,
        parse_mark_unmark,
        parse_note,
        parse_recurring,
        parse_todo,
    )
    from .storage import save_tasks
    from .tasklist import (
        add_deadline,
        add_event,
        add_recurring,
        add_todo,
        clear_completed,
        delete_task,
        due_tasks,
        find_tasks,
        set_done,
        set_note,
    )
    from .ui import (
        show_added,
        show_cleared,
        show_deleted,
        show_due_tasks,
        show_found_tasks,
        show_marked,
        show_noted,
        show_tasks,
    )
else:
    from parser import (
        parse_deadline,
        parse_delete,
        parse_due,
        parse_event,
        parse_find,
        parse_mark_unmark,
        parse_note,
        parse_recurring,
        parse_todo,
    )
    from storage import save_tasks
    from tasklist import (
        add_deadline,
        add_event,
        add_recurring,
        add_todo,
        clear_completed,
        delete_task,
        due_tasks,
        find_tasks,
        set_done,
        set_note,
    )
    from ui import (
        show_added,
        show_cleared,
        show_deleted,
        show_due_tasks,
        show_found_tasks,
        show_marked,
        show_noted,
        show_tasks,
    )


def handle_empty_input() -> None:
    """Print the response to empty input.

    Returns:
        None.
    """
    # UI: respond to empty input.
    print("Nothing there.")


def handle_bye() -> None:
    """Print the farewell; the caller controls exiting the input loop.

    Returns:
        None.
    """
    # UI: display the farewell.
    print("Later.")


def handle_list(tasks: list[dict[str, Any]]) -> None:
    """Display the supplied tasks and their notes.

    Args:
        tasks: Task list to display without modifying it.

    Returns:
        None.
    """
    # UI: display the task list and its optional notes.
    show_tasks(tasks)


def handle_todo(line: str, tasks: list[dict[str, Any]], data_file: Path) -> None:
    """Parse a to-do command, append its task, display it, and save.

    Updates the supplied list in place, prints confirmation, and saves JSON.
    A save failure does not roll back the in-memory change.

    Args:
        line: Raw to-do command containing the description.
        tasks: Task list to append the new to-do task to in place.
        data_file: Destination for saving the updated task list as JSON.

    Returns:
        None.

    Raises:
        InputError: If the command arguments are invalid.
        OSError: If the save directory cannot be created or data cannot be written.
    """
    # Parser: extract the description and check that it is present.
    description = parse_todo(line)
    # Tasklist: build the task from parsed values and append it to the list.
    task = add_todo(tasks, description)
    # UI: display the added task.
    show_added(task)
    # Storage: create the destination directory and save the task list as JSON.
    save_tasks(tasks, data_file)


def handle_deadline(line: str, tasks: list[dict[str, Any]], data_file: Path) -> None:
    """Parse a deadline command, append its task, display it, and save.

    Updates the supplied list in place, prints confirmation, and saves JSON.
    A save failure does not roll back the in-memory change.

    Args:
        line: Raw deadline command containing the description and /by value.
        tasks: Task list to append the new deadline task to in place.
        data_file: Destination for saving the updated task list as JSON.

    Returns:
        None.

    Raises:
        InputError: If the command arguments are invalid.
        OSError: If the save directory cannot be created or data cannot be written.
    """
    # Parser: require a description and /by value, then parse the deadline.
    description, parsed = parse_deadline(line)
    # Tasklist: build the task from parsed values and append it to the list.
    task = add_deadline(tasks, description, parsed)
    # UI: display the added task.
    show_added(task)
    # Storage: create the destination directory and save the task list as JSON.
    save_tasks(tasks, data_file)


def handle_event(line: str, tasks: list[dict[str, Any]], data_file: Path) -> None:
    """Parse an event command, append its task, display it, and save.

    Updates the supplied list in place, prints confirmation, and saves JSON.
    A save failure does not roll back the in-memory change.

    Args:
        line: Raw event command containing description, /from, and /to values.
        tasks: Task list to append the new event task to in place.
        data_file: Destination for saving the updated task list as JSON.

    Returns:
        None.

    Raises:
        InputError: If the command arguments are invalid.
        ValueError: If /to occurs only before /from, preserving the existing
            unpacking error.
        OSError: If the save directory cannot be created or data cannot be written.
    """
    # Parser: extract the description, start, and end from the event command.
    description, start, end = parse_event(line)
    # Tasklist: build the task from parsed values and append it to the list.
    task = add_event(tasks, description, start, end)
    # UI: display the added task.
    show_added(task)
    # Storage: create the destination directory and save the task list as JSON.
    save_tasks(tasks, data_file)


def handle_recurring(line: str, tasks: list[dict[str, Any]], data_file: Path) -> None:
    """Parse a recurring command, append its task, display it, and save.

    Updates the supplied list in place, prints confirmation, and saves JSON.
    A save failure does not roll back the in-memory change.

    Args:
        line: Raw recurring command containing description and /every value.
        tasks: Task list to append the new recurring task to in place.
        data_file: Destination for saving the updated task list as JSON.

    Returns:
        None.

    Raises:
        InputError: If the command arguments are invalid.
        OSError: If the save directory cannot be created or data cannot be written.
    """
    # Parser: require a description and /every value.
    description, every = parse_recurring(line)
    # Tasklist: build the task from parsed values and append it to the list.
    task = add_recurring(tasks, description, every)
    # UI: display the added task.
    show_added(task)
    # Storage: create the destination directory and save the task list as JSON.
    save_tasks(tasks, data_file)


def handle_mark_unmark(line: str, tasks: list[dict[str, Any]], data_file: Path) -> None:
    """Parse a mark or unmark command, update its task, display it, and save.

    Updates the supplied list in place, prints confirmation, and saves JSON.
    A save failure does not roll back the in-memory change.

    Args:
        line: Raw mark or unmark command containing a task number.
        tasks: Task list whose selected completion state is updated in place.
        data_file: Destination for saving the updated task list as JSON.

    Returns:
        None.

    Raises:
        InputError: If the command arguments are invalid.
        TaskNotFoundError: If the requested task does not exist.
        IndexError: If called directly without a command name.
        OSError: If the save directory cannot be created or data cannot be written.
    """
    # Parser: identify the command and parse its task-number argument.
    command, index = parse_mark_unmark(line)
    # Tasklist: validate the index and update the completion state.
    set_done(tasks, index, command == "mark")
    # UI: format and display the updated completion state and description.
    show_marked(tasks[index])
    # Storage: create the destination directory and save the task list as JSON.
    save_tasks(tasks, data_file)


def handle_note(line: str, tasks: list[dict[str, Any]], data_file: Path) -> None:
    """Parse a note command, replace the task note, display it, and save.

    Updates the supplied list in place, prints confirmation, and saves JSON.
    A save failure does not roll back the in-memory change.

    Args:
        line: Raw note command containing a task number and note text.
        tasks: Task list whose selected note is replaced in place.
        data_file: Destination for saving the updated task list as JSON.

    Returns:
        None.

    Raises:
        InputError: If the command arguments are invalid.
        TaskNotFoundError: If the requested task does not exist.
        OSError: If the save directory cannot be created or data cannot be written.
    """
    # Parser: extract the task index and preserve the remaining note text.
    index, note = parse_note(line)
    # Tasklist: validate the index and replace the note.
    set_note(tasks, index, note)
    # UI: display the task and its updated note.
    show_noted(tasks[index])
    # Storage: create the destination directory and save the task list as JSON.
    save_tasks(tasks, data_file)


def handle_delete(line: str, tasks: list[dict[str, Any]], data_file: Path) -> None:
    """Parse a delete command, remove its task, display the result, and save.

    Updates the supplied list in place, prints confirmation, and saves JSON.
    A save failure does not roll back the in-memory change.

    Args:
        line: Raw delete command containing a task number.
        tasks: Task list to remove the selected task from in place.
        data_file: Destination for saving the updated task list as JSON.

    Returns:
        None.

    Raises:
        InputError: If the command arguments are invalid.
        TaskNotFoundError: If the requested task does not exist.
        OSError: If the save directory cannot be created or data cannot be written.
    """
    # Parser: require and parse a single task-number argument.
    index = parse_delete(line)
    # Tasklist: validate the index and remove the task for confirmation.
    removed = delete_task(tasks, index)
    # UI: display the removed task and the remaining task count.
    show_deleted(removed, len(tasks))
    # Storage: create the destination directory and save the task list as JSON.
    save_tasks(tasks, data_file)


def handle_clear(tasks: list[dict[str, Any]], data_file: Path) -> None:
    """Remove completed tasks, display the result, and save.

    Updates the supplied list in place, prints confirmation, and saves JSON.
    A save failure does not roll back the in-memory change.

    Args:
        tasks: Task list to remove completed tasks from in place.
        data_file: Destination for saving the updated task list as JSON.

    Returns:
        None.

    Raises:
        OSError: If the save directory cannot be created or data cannot be written.
    """
    # Tasklist: remove completed tasks in place and count the removals.
    removed = clear_completed(tasks)
    # UI: display the number removed and the remaining task count.
    show_cleared(removed, len(tasks))
    # Storage: create the destination directory and save the task list as JSON.
    save_tasks(tasks, data_file)


def handle_find(line: str, tasks: list[dict[str, Any]]) -> None:
    """Parse a search command and display matching task descriptions.

    Args:
        line: Raw find command containing the search query.
        tasks: Task list to search without modifying it.

    Returns:
        None.

    Raises:
        InputError: If the command arguments are invalid.
    """
    # Parser: extract the search text and check that it is present.
    query = parse_find(line)
    # Tasklist: find tasks whose descriptions contain the query, ignoring case.
    matches = find_tasks(tasks, query)
    # UI: display matching tasks or the empty-result message.
    show_found_tasks(matches)


def handle_due(line: str, tasks: list[dict[str, Any]]) -> None:
    """Parse a date query and display deadlines due that day.

    Args:
        line: Raw due command containing the requested calendar date.
        tasks: Task list to filter by deadline date without modifying it.

    Returns:
        None.

    Raises:
        InputError: If the command arguments are invalid.
    """
    # Parser: extract and validate the requested calendar date.
    wanted = parse_due(line)
    # Tasklist: select deadlines by their stored due date.
    matches = due_tasks(tasks, wanted)
    # UI: display matching tasks or the empty-result message.
    show_due_tasks(matches)


def handle_unknown_command() -> None:
    """Print guidance for an unrecognized command.

    Returns:
        None.
    """
    # UI: display guidance after the caller finds no matching command.
    print(
        "Never heard of it. Try: todo, deadline, event, recurring, list, mark, "
        "unmark, note, delete, clear, find, due, bye."
    )
