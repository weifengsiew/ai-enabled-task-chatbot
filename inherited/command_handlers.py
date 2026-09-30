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
        add_todo,
        clear_completed,
        delete_task,
        due_tasks,
        find_tasks,
        set_done,
        set_note,
    )
    from .ui import (
        format_task,
        format_task_summary,
        show_added,
        show_deleted,
        show_marked,
        show_noted,
        show_tasks,
        show_tasks_left,
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
        add_todo,
        clear_completed,
        delete_task,
        due_tasks,
        find_tasks,
        set_done,
        set_note,
    )
    from ui import (
        format_task,
        format_task_summary,
        show_added,
        show_deleted,
        show_marked,
        show_noted,
        show_tasks,
        show_tasks_left,
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
        tasks: Current task list; commands that change tasks mutate it in place.

    Returns:
        None.
    """
    # UI: display the task list and its optional notes.
    show_tasks(tasks)


def handle_todo(line: str, tasks: list[dict[str, Any]], data_file: Path) -> None:
    """Parse a to-do command, append its task, display it, and save.

    Args:
        line: Raw command text to parse.
        tasks: Current task list; commands that change tasks mutate it in place.
        data_file: Destination for saving the updated task list as JSON.

    Returns:
        None.
    """
    # Parser: extract the description and check that it is present.
    try:
        description = parse_todo(line)
    except ValueError as error:
        # UI: display the parser's input error.
        print(str(error))
        return
    # Tasklist: build the task from parsed values and append it to the list.
    task = add_todo(tasks, description)
    # UI: display the added task.
    show_added(task)
    # Storage: create the destination directory and save the task list as JSON.
    save_tasks(tasks, data_file)


def handle_deadline(line: str, tasks: list[dict[str, Any]], data_file: Path) -> None:
    """Parse a deadline command, append its task, display it, and save.

    Args:
        line: Raw command text to parse.
        tasks: Current task list; commands that change tasks mutate it in place.
        data_file: Destination for saving the updated task list as JSON.

    Returns:
        None.
    """
    # Parser: require a description and /by value, then parse the deadline.
    try:
        description, parsed = parse_deadline(line)
    except ValueError as error:
        # UI: display the parser's input error.
        print(str(error))
        return
    # Tasklist: build the task from parsed values and append it to the list.
    task = add_deadline(tasks, description, parsed)
    # UI: display the added task.
    show_added(task)
    # Storage: create the destination directory and save the task list as JSON.
    save_tasks(tasks, data_file)


def handle_event(line: str, tasks: list[dict[str, Any]], data_file: Path) -> None:
    """Parse an event command, append its task, display it, and save.

    Args:
        line: Raw command text to parse.
        tasks: Current task list; commands that change tasks mutate it in place.
        data_file: Destination for saving the updated task list as JSON.

    Returns:
        None.
    """
    # Parser: extract the description, start, and end from the event command.
    try:
        description, start, end = parse_event(line)
    except ValueError as error:
        # Preserve the existing uncaught error for incorrectly ordered separators.
        if str(error) != "An event needs a description, /from, and /to.":
            raise
        # UI: display the parser's input error.
        print(str(error))
        return
    # Tasklist: build the task from parsed values and append it to the list.
    task = {
        "kind": "event",
        "description": description,
        "done": False,
        "note": "",
        "from": start,
        "to": end,
    }
    tasks.append(task)
    # UI: display the added task.
    show_added(task)
    # Storage: create the destination directory and save the task list as JSON.
    save_tasks(tasks, data_file)


def handle_recurring(line: str, tasks: list[dict[str, Any]], data_file: Path) -> None:
    """Parse a recurring command, append its task, display it, and save.

    Args:
        line: Raw command text to parse.
        tasks: Current task list; commands that change tasks mutate it in place.
        data_file: Destination for saving the updated task list as JSON.

    Returns:
        None.
    """
    # Parser: require a description and /every value.
    try:
        description, every = parse_recurring(line)
    except ValueError as error:
        # UI: display the parser's input error.
        print(str(error))
        return
    # Tasklist: build the task from parsed values and append it to the list.
    task = {
        "kind": "recurring",
        "description": description,
        "done": False,
        "note": "",
        "every": every,
    }
    tasks.append(task)
    # UI: display the added task.
    show_added(task)
    # Storage: create the destination directory and save the task list as JSON.
    save_tasks(tasks, data_file)


def handle_mark_unmark(line: str, tasks: list[dict[str, Any]], data_file: Path) -> None:
    """Parse a mark or unmark command, update its task, display it, and save.

    Args:
        line: Raw command text to parse.
        tasks: Current task list; commands that change tasks mutate it in place.
        data_file: Destination for saving the updated task list as JSON.

    Returns:
        None.
    """
    # Parser: identify the command and parse its task-number argument.
    try:
        command, index = parse_mark_unmark(line)
    except ValueError as error:
        # UI: display the parser's input error.
        print(str(error))
        return
    # Tasklist: validate the index and update the completion state.
    try:
        set_done(tasks, index, command == "mark")
    except IndexError:
        # UI: preserve the task number exactly as entered in the error message.
        number_text = line.split()[1]
        print(f"No task {number_text}.")
        return
    # UI: format and display the updated completion state and description.
    show_marked(tasks[index])
    # Storage: create the destination directory and save the task list as JSON.
    save_tasks(tasks, data_file)


def handle_note(line: str, tasks: list[dict[str, Any]], data_file: Path) -> None:
    """Parse a note command, replace the task note, display it, and save.

    Args:
        line: Raw command text to parse.
        tasks: Current task list; commands that change tasks mutate it in place.
        data_file: Destination for saving the updated task list as JSON.

    Returns:
        None.
    """
    # Parser: extract the task index and preserve the remaining note text.
    try:
        index, note = parse_note(line)
    except ValueError as error:
        # UI: display the parser's input error.
        print(str(error))
        return
    # Tasklist: validate the index and replace the note.
    try:
        set_note(tasks, index, note)
    except IndexError:
        # UI: preserve the task number exactly as entered in the error message.
        number_text = line.split(maxsplit=2)[1]
        print(f"No task {number_text}.")
        return
    # UI: display the task and its updated note.
    show_noted(tasks[index])
    # Storage: create the destination directory and save the task list as JSON.
    save_tasks(tasks, data_file)


def handle_delete(line: str, tasks: list[dict[str, Any]], data_file: Path) -> None:
    """Parse a delete command, remove its task, display the result, and save.

    Args:
        line: Raw command text to parse.
        tasks: Current task list; commands that change tasks mutate it in place.
        data_file: Destination for saving the updated task list as JSON.

    Returns:
        None.
    """
    # Parser: require and parse a single task-number argument.
    try:
        index = parse_delete(line)
    except ValueError as error:
        # UI: display the parser's input error.
        print(str(error))
        return
    # Tasklist: validate the index and remove the task for confirmation.
    try:
        removed = delete_task(tasks, index)
    except IndexError:
        # UI: preserve the task number exactly as entered in the error message.
        number_text = line.split()[1]
        print(f"No task {number_text}.")
        return
    # UI: display the removed task and the remaining task count.
    show_deleted(removed, len(tasks))
    # Storage: create the destination directory and save the task list as JSON.
    save_tasks(tasks, data_file)


def handle_clear(tasks: list[dict[str, Any]], data_file: Path) -> None:
    """Remove completed tasks, display the result, and save.

    Args:
        tasks: Current task list; commands that change tasks mutate it in place.
        data_file: Destination for saving the updated task list as JSON.

    Returns:
        None.
    """
    # Tasklist: remove completed tasks in place and count the removals.
    removed = clear_completed(tasks)
    # UI: display the number removed and the remaining task count.
    print(f"Cleared {removed} completed tasks.")
    show_tasks_left(len(tasks))
    # Storage: create the destination directory and save the task list as JSON.
    save_tasks(tasks, data_file)


def handle_find(line: str, tasks: list[dict[str, Any]]) -> None:
    """Parse a search command and display matching task descriptions.

    Args:
        line: Raw command text to parse.
        tasks: Current task list; commands that change tasks mutate it in place.

    Returns:
        None.
    """
    # Parser: extract the search text and check that it is present.
    try:
        query = parse_find(line)
    except ValueError as error:
        # UI: display the parser's input error.
        print(str(error))
        return
    # Tasklist: find tasks whose descriptions contain the query, ignoring case.
    matches = find_tasks(tasks, query)
    # UI: display an empty-result message when the search found no tasks.
    if not matches:
        print("No matching tasks.")
    # UI: number, format, and display the matching tasks.
    for number, task in enumerate(matches, 1):
        print(f"{number}.{format_task_summary(task)}")


def handle_due(line: str, tasks: list[dict[str, Any]]) -> None:
    """Parse a date query and display deadlines due that day.

    Args:
        line: Raw command text to parse.
        tasks: Current task list; commands that change tasks mutate it in place.

    Returns:
        None.
    """
    # Parser: extract and validate the requested calendar date.
    try:
        wanted = parse_due(line)
    except ValueError as error:
        # UI: display the parser's input error.
        print(str(error))
        return
    # Tasklist: select deadlines by their stored due date.
    matches = due_tasks(tasks, wanted)
    # UI: display an empty-result message when the search found no tasks.
    if not matches:
        print("Nothing due that day.")
    # UI: number, format, and display the matching tasks.
    for number, task in enumerate(matches, 1):
        print(f"{number}.{format_task(task)}")


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
