"""Command handlers extracted from the inherited Bao input loop."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any


def handle_empty_input() -> None:
    """Print the response to empty input.

    Returns:
        None.
    """
    print("Nothing there.")


def handle_bye() -> None:
    """Print the farewell; the caller controls exiting the input loop.

    Returns:
        None.
    """
    print("Later.")


def handle_list(tasks: list[dict[str, Any]]) -> None:
    """Display the supplied tasks and their notes.

    Args:
        tasks: Current task list; commands that change tasks mutate it in place.

    Returns:
        None.
    """
    if not tasks:
        print("Nothing on your plate.")
    else:
        for number, task in enumerate(tasks, 1):
            box = "X" if task["done"] else " "
            if task["kind"] == "todo":
                display = f'[T][{box}] {task["description"]}'
            elif task["kind"] == "deadline":
                due = datetime.fromisoformat(task["when"])
                if due.hour == 0 and due.minute == 0:
                    formatted = due.strftime("%b %d %Y")
                else:
                    formatted = due.strftime("%b %d %Y, ") + due.strftime("%I%p").lstrip(
                        "0"
                    ).lower()
                display = f'[D][{box}] {task["description"]} (by: {formatted})'
            elif task["kind"] == "event":
                display = (
                    f'[E][{box}] {task["description"]} '
                    f'(from: {task["from"]} to: {task["to"]})'
                )
            else:
                display = f'[R][{box}] {task["description"]} (every: {task["every"]})'
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
    description = line[5:].strip()
    if not description:
        print("A to-do needs something to do.")
        return
    task = {"kind": "todo", "description": description, "done": False, "note": ""}
    tasks.append(task)
    print("Added:")
    print(f"  [T][ ] {description}")
    data_file.parent.mkdir(parents=True, exist_ok=True)
    data_file.write_text(json.dumps(tasks, indent=2))


def handle_deadline(line: str, tasks: list[dict[str, Any]], data_file: Path) -> None:
    """Parse a deadline command, append its task, display it, and save.

    Args:
        line: Raw command text to parse.
        tasks: Current task list; commands that change tasks mutate it in place.
        data_file: Destination for saving the updated task list as JSON.

    Returns:
        None.
    """
    rest = line[len("deadline") :].strip()
    if "/by" not in rest:
        print("A deadline needs something to do and a /by.")
        return
    description, when_text = (part.strip() for part in rest.split("/by", 1))
    if not description or not when_text:
        print("A deadline needs something to do and a /by.")
        return
    parsed = None
    for pattern in ("%Y-%m-%d %H%M", "%Y-%m-%d"):
        try:
            parsed = datetime.strptime(when_text, pattern)
            break
        except ValueError:
            pass
    if parsed is None:
        print("Use YYYY-MM-DD with an optional four-digit time.")
        return
    task = {
        "kind": "deadline",
        "description": description,
        "done": False,
        "note": "",
        "when": parsed.isoformat(),
    }
    tasks.append(task)
    if parsed.hour == 0 and parsed.minute == 0:
        formatted = parsed.strftime("%b %d %Y")
    else:
        formatted = parsed.strftime("%b %d %Y, ") + parsed.strftime("%I%p").lstrip(
            "0"
        ).lower()
    print("Added:")
    print(f"  [D][ ] {description} (by: {formatted})")
    data_file.parent.mkdir(parents=True, exist_ok=True)
    data_file.write_text(json.dumps(tasks, indent=2))


def handle_event(line: str, tasks: list[dict[str, Any]], data_file: Path) -> None:
    """Parse an event command, append its task, display it, and save.

    Args:
        line: Raw command text to parse.
        tasks: Current task list; commands that change tasks mutate it in place.
        data_file: Destination for saving the updated task list as JSON.

    Returns:
        None.
    """
    rest = line[len("event") :].strip()
    if "/from" not in rest or "/to" not in rest:
        print("An event needs a description, /from, and /to.")
        return
    description, times = (part.strip() for part in rest.split("/from", 1))
    start, end = (part.strip() for part in times.split("/to", 1))
    if not description or not start or not end:
        print("An event needs a description, /from, and /to.")
        return
    task = {
        "kind": "event",
        "description": description,
        "done": False,
        "note": "",
        "from": start,
        "to": end,
    }
    tasks.append(task)
    print("Added:")
    print(f"  [E][ ] {description} (from: {start} to: {end})")
    data_file.parent.mkdir(parents=True, exist_ok=True)
    data_file.write_text(json.dumps(tasks, indent=2))


def handle_recurring(line: str, tasks: list[dict[str, Any]], data_file: Path) -> None:
    """Parse a recurring command, append its task, display it, and save.

    Args:
        line: Raw command text to parse.
        tasks: Current task list; commands that change tasks mutate it in place.
        data_file: Destination for saving the updated task list as JSON.

    Returns:
        None.
    """
    rest = line[len("recurring") :].strip()
    if "/every" not in rest:
        print("A recurring task needs something to do and an /every.")
        return
    description, every = (part.strip() for part in rest.split("/every", 1))
    if not description or not every:
        print("A recurring task needs something to do and an /every.")
        return
    task = {
        "kind": "recurring",
        "description": description,
        "done": False,
        "note": "",
        "every": every,
    }
    tasks.append(task)
    print("Added:")
    print(f"  [R][ ] {description} (every: {every})")
    data_file.parent.mkdir(parents=True, exist_ok=True)
    data_file.write_text(json.dumps(tasks, indent=2))


def handle_mark_unmark(line: str, tasks: list[dict[str, Any]], data_file: Path) -> None:
    """Parse a mark or unmark command, update its task, display it, and save.

    Args:
        line: Raw command text to parse.
        tasks: Current task list; commands that change tasks mutate it in place.
        data_file: Destination for saving the updated task list as JSON.

    Returns:
        None.
    """
    pieces = line.split()
    command = pieces[0]
    if len(pieces) != 2:
        print(f"Tell me which task to {command}, for example: {command} 2.")
        return
    try:
        index = int(pieces[1]) - 1
    except ValueError:
        print("The task number must be a whole number.")
        return
    if index < 0 or index >= len(tasks):
        print(f"No task {pieces[1]}.")
        return
    tasks[index]["done"] = command == "mark"
    box = "X" if tasks[index]["done"] else " "
    print("Done:" if command == "mark" else "Not done:")
    print(f'  [{box}] {tasks[index]["description"]}')
    data_file.parent.mkdir(parents=True, exist_ok=True)
    data_file.write_text(json.dumps(tasks, indent=2))


def handle_note(line: str, tasks: list[dict[str, Any]], data_file: Path) -> None:
    """Parse a note command, replace the task note, display it, and save.

    Args:
        line: Raw command text to parse.
        tasks: Current task list; commands that change tasks mutate it in place.
        data_file: Destination for saving the updated task list as JSON.

    Returns:
        None.
    """
    pieces = line.split(maxsplit=2)
    if len(pieces) != 3:
        print("Use note NUMBER TEXT, for example: note 2 ask about funding.")
        return
    try:
        index = int(pieces[1]) - 1
    except ValueError:
        print("The task number must be a whole number.")
        return
    if index < 0 or index >= len(tasks):
        print(f"No task {pieces[1]}.")
        return
    tasks[index]["note"] = pieces[2]
    print("Noted:")
    print(f'  {tasks[index]["description"]}')
    print(f"  Note: {pieces[2]}")
    data_file.parent.mkdir(parents=True, exist_ok=True)
    data_file.write_text(json.dumps(tasks, indent=2))


def handle_delete(line: str, tasks: list[dict[str, Any]], data_file: Path) -> None:
    """Parse a delete command, remove its task, display the result, and save.

    Args:
        line: Raw command text to parse.
        tasks: Current task list; commands that change tasks mutate it in place.
        data_file: Destination for saving the updated task list as JSON.

    Returns:
        None.
    """
    pieces = line.split()
    if len(pieces) != 2:
        print("Tell me which task to delete, for example: delete 2.")
        return
    try:
        index = int(pieces[1]) - 1
    except ValueError:
        print("The task number must be a whole number.")
        return
    if index < 0 or index >= len(tasks):
        print(f"No task {pieces[1]}.")
        return
    removed = tasks.pop(index)
    print("Deleted:")
    print(f'  {removed["description"]}')
    print(f"{len(tasks)} tasks left.")
    data_file.parent.mkdir(parents=True, exist_ok=True)
    data_file.write_text(json.dumps(tasks, indent=2))


def handle_clear(tasks: list[dict[str, Any]], data_file: Path) -> None:
    """Remove completed tasks, display the result, and save.

    Args:
        tasks: Current task list; commands that change tasks mutate it in place.
        data_file: Destination for saving the updated task list as JSON.

    Returns:
        None.
    """
    before = len(tasks)
    tasks[:] = [task for task in tasks if not task["done"]]
    removed = before - len(tasks)
    print(f"Cleared {removed} completed tasks.")
    print(f"{len(tasks)} tasks left.")
    data_file.parent.mkdir(parents=True, exist_ok=True)
    data_file.write_text(json.dumps(tasks, indent=2))


def handle_find(line: str, tasks: list[dict[str, Any]]) -> None:
    """Parse a search command and display matching task descriptions.

    Args:
        line: Raw command text to parse.
        tasks: Current task list; commands that change tasks mutate it in place.

    Returns:
        None.
    """
    query = line[len("find") :].strip()
    if not query:
        print("Tell me what to find.")
        return
    matches = [task for task in tasks if query.casefold() in task["description"].casefold()]
    if not matches:
        print("No matching tasks.")
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
    date_text = line[len("due") :].strip()
    try:
        wanted = datetime.strptime(date_text, "%Y-%m-%d").date()
    except ValueError:
        print("Use due YYYY-MM-DD.")
        return
    matches = [
        task
        for task in tasks
        if task["kind"] == "deadline"
        and datetime.fromisoformat(task["when"]).date() == wanted
    ]
    if not matches:
        print("Nothing due that day.")
    for number, task in enumerate(matches, 1):
        due = datetime.fromisoformat(task["when"])
        if due.hour == 0 and due.minute == 0:
            formatted = due.strftime("%b %d %Y")
        else:
            formatted = due.strftime("%b %d %Y, ") + due.strftime("%I%p").lstrip(
                "0"
            ).lower()
        box = "X" if task["done"] else " "
        print(f'{number}.[D][{box}] {task["description"]} (by: {formatted})')


def handle_unknown_command() -> None:
    """Print guidance for an unrecognized command.

    Returns:
        None.
    """
    print(
        "Never heard of it. Try: todo, deadline, event, recurring, list, mark, "
        "unmark, note, delete, clear, find, due, bye."
    )
