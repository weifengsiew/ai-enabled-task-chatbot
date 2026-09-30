"""Command handlers extracted from the inherited Bao input loop."""

from datetime import datetime
from pathlib import Path
from typing import Any

if __package__:
    from .storage import save_tasks
    from .ui import format_deadline
else:
    from storage import save_tasks
    from ui import format_deadline


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
    # Parser: absent; the caller has already recognized the list command.
    # Storage: absent; tasks are supplied in memory, with no file access here.
    # Tasklist: read the supplied collection; no tasks are changed.
    if not tasks:
        # UI: display the empty-list message.
        print("Nothing on your plate.")
    else:
        # UI: number the supplied tasks for display, starting at 1.
        for number, task in enumerate(tasks, 1):
            # UI: format the completion box and each task kind.
            box = "X" if task["done"] else " "
            if task["kind"] == "todo":
                display = f'[T][{box}] {task["description"]}'
            elif task["kind"] == "deadline":
                # UI: convert the stored date for display, not command parsing.
                due = datetime.fromisoformat(task["when"])
                formatted = format_deadline(due)
                display = f'[D][{box}] {task["description"]} (by: {formatted})'
            elif task["kind"] == "event":
                display = (
                    f'[E][{box}] {task["description"]} '
                    f'(from: {task["from"]} to: {task["to"]})'
                )
            else:
                display = f'[R][{box}] {task["description"]} (every: {task["every"]})'
            # UI: print the formatted task and its optional note.
            print(f"{number}.{display}")
            if task["note"]:
                print(f'   Note: {task["note"]}')


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
    description = line[5:].strip()
    if not description:
        # Parser / UI: validation detects invalid input; UI displays the input error here.
        print("A to-do needs something to do.")
        return
    # Tasklist: build the task from parsed values and append it to the list.
    task = {"kind": "todo", "description": description, "done": False, "note": ""}
    tasks.append(task)
    # UI: display the added task.
    print("Added:")
    print(f"  [T][ ] {description}")
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
    # Parser: extract the arguments and check for the /by separator.
    rest = line[len("deadline") :].strip()
    if "/by" not in rest:
        # Parser / UI: validation detects invalid input; UI displays the input error here.
        print("A deadline needs something to do and a /by.")
        return
    # Parser: split the description and date, requiring both values.
    description, when_text = (part.strip() for part in rest.split("/by", 1))
    if not description or not when_text:
        # Parser / UI: validation detects invalid input; UI displays the input error here.
        print("A deadline needs something to do and a /by.")
        return
    # Parser: accept a date with an optional four-digit time.
    parsed = None
    for pattern in ("%Y-%m-%d %H%M", "%Y-%m-%d"):
        try:
            parsed = datetime.strptime(when_text, pattern)
            break
        except ValueError:
            pass
    if parsed is None:
        # Parser / UI: validation detects invalid input; UI displays the input error here.
        print("Use YYYY-MM-DD with an optional four-digit time.")
        return
    # Tasklist: build the task from parsed values and append it to the list.
    task = {
        "kind": "deadline",
        "description": description,
        "done": False,
        "note": "",
        "when": parsed.isoformat(),
    }
    tasks.append(task)
    # UI: format the deadline date and optional time for the confirmation.
    formatted = format_deadline(parsed)
    # UI: display the added task.
    print("Added:")
    print(f"  [D][ ] {description} (by: {formatted})")
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
    # Parser: extract the arguments and check for /from and /to.
    rest = line[len("event") :].strip()
    if "/from" not in rest or "/to" not in rest:
        # Parser / UI: validation detects invalid input; UI displays the input error here.
        print("An event needs a description, /from, and /to.")
        return
    # Parser: split the description, start, and end, requiring each value.
    description, times = (part.strip() for part in rest.split("/from", 1))
    start, end = (part.strip() for part in times.split("/to", 1))
    if not description or not start or not end:
        # Parser / UI: validation detects invalid input; UI displays the input error here.
        print("An event needs a description, /from, and /to.")
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
    print("Added:")
    print(f"  [E][ ] {description} (from: {start} to: {end})")
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
    # Parser: extract the arguments and check for /every.
    rest = line[len("recurring") :].strip()
    if "/every" not in rest:
        # Parser / UI: validation detects invalid input; UI displays the input error here.
        print("A recurring task needs something to do and an /every.")
        return
    # Parser: split the description and interval, requiring both values.
    description, every = (part.strip() for part in rest.split("/every", 1))
    if not description or not every:
        # Parser / UI: validation detects invalid input; UI displays the input error here.
        print("A recurring task needs something to do and an /every.")
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
    print("Added:")
    print(f"  [R][ ] {description} (every: {every})")
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
    # Parser: split the command and require a task-number argument.
    pieces = line.split()
    command = pieces[0]
    if len(pieces) != 2:
        # Parser / UI: validation detects invalid input; UI displays the input error here.
        print(f"Tell me which task to {command}, for example: {command} 2.")
        return
    try:
        # Parser: convert the task number to a zero-based index.
        index = int(pieces[1]) - 1
    except ValueError:
        # Parser / UI: validation detects invalid input; UI displays the input error here.
        print("The task number must be a whole number.")
        return
    # Tasklist: check that the requested task exists in the current list.
    if index < 0 or index >= len(tasks):
        # Tasklist / UI: the task lookup fails; UI displays the missing-task error here.
        print(f"No task {pieces[1]}.")
        return
    # Tasklist: update the selected task's completion state.
    tasks[index]["done"] = command == "mark"
    # UI: format and display the updated completion state and description.
    box = "X" if tasks[index]["done"] else " "
    print("Done:" if command == "mark" else "Not done:")
    print(f'  [{box}] {tasks[index]["description"]}')
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
    # Parser: extract the task number and preserve the remaining note text.
    pieces = line.split(maxsplit=2)
    if len(pieces) != 3:
        # Parser / UI: validation detects invalid input; UI displays the input error here.
        print("Use note NUMBER TEXT, for example: note 2 ask about funding.")
        return
    try:
        # Parser: convert the task number to a zero-based index.
        index = int(pieces[1]) - 1
    except ValueError:
        # Parser / UI: validation detects invalid input; UI displays the input error here.
        print("The task number must be a whole number.")
        return
    # Tasklist: check that the requested task exists in the current list.
    if index < 0 or index >= len(tasks):
        # Tasklist / UI: the task lookup fails; UI displays the missing-task error here.
        print(f"No task {pieces[1]}.")
        return
    # Tasklist: replace the selected task's note.
    tasks[index]["note"] = pieces[2]
    # UI: display the task and its updated note.
    print("Noted:")
    print(f'  {tasks[index]["description"]}')
    print(f"  Note: {pieces[2]}")
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
    # Parser: split the command and require a task-number argument.
    pieces = line.split()
    if len(pieces) != 2:
        # Parser / UI: validation detects invalid input; UI displays the input error here.
        print("Tell me which task to delete, for example: delete 2.")
        return
    try:
        # Parser: convert the task number to a zero-based index.
        index = int(pieces[1]) - 1
    except ValueError:
        # Parser / UI: validation detects invalid input; UI displays the input error here.
        print("The task number must be a whole number.")
        return
    # Tasklist: check that the requested task exists in the current list.
    if index < 0 or index >= len(tasks):
        # Tasklist / UI: the task lookup fails; UI displays the missing-task error here.
        print(f"No task {pieces[1]}.")
        return
    # Tasklist: remove the selected task and retain it for the confirmation.
    removed = tasks.pop(index)
    # UI: display the removed task and the remaining task count.
    print("Deleted:")
    print(f'  {removed["description"]}')
    print(f"{len(tasks)} tasks left.")
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
    before = len(tasks)
    tasks[:] = [task for task in tasks if not task["done"]]
    removed = before - len(tasks)
    # UI: display the number removed and the remaining task count.
    print(f"Cleared {removed} completed tasks.")
    print(f"{len(tasks)} tasks left.")
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
    query = line[len("find") :].strip()
    if not query:
        # Parser / UI: validation detects invalid input; UI displays the input error here.
        print("Tell me what to find.")
        return
    # Tasklist: find tasks whose descriptions contain the query, ignoring case.
    matches = [task for task in tasks if query.casefold() in task["description"].casefold()]
    # UI: display an empty-result message when the search found no tasks.
    if not matches:
        print("No matching tasks.")
    # UI: number, format, and display the matching tasks.
    for number, task in enumerate(matches, 1):
        box = "X" if task["done"] else " "
        print(f'{number}.[{box}] {task["description"]}')


def handle_due(line: str, tasks: list[dict[str, Any]]) -> None:
    """Parse a date query and display deadlines due that day.

    Args:
        line: Raw command text to parse.
        tasks: Current task list; commands that change tasks mutate it in place.

    Returns:
        None.
    """
    # Parser: extract and validate the requested calendar date.
    date_text = line[len("due") :].strip()
    try:
        wanted = datetime.strptime(date_text, "%Y-%m-%d").date()
    except ValueError:
        # Parser / UI: validation detects invalid input; UI displays the input error here.
        print("Use due YYYY-MM-DD.")
        return
    # Tasklist: select deadlines by their stored due date.
    matches = [
        task
        for task in tasks
        if task["kind"] == "deadline"
        and datetime.fromisoformat(task["when"]).date() == wanted
    ]
    # UI: display an empty-result message when the search found no tasks.
    if not matches:
        print("Nothing due that day.")
    # UI: number, format, and display the matching tasks.
    for number, task in enumerate(matches, 1):
        due = datetime.fromisoformat(task["when"])
        formatted = format_deadline(due)
        box = "X" if task["done"] else " "
        print(f'{number}.[D][{box}] {task["description"]} (by: {formatted})')


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
