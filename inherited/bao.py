"""Entry point and input loop for the inherited Bao application."""

import json
from pathlib import Path

if __package__:
    from . import command_handlers
    from .parser import InputError
    from .storage import load_tasks
    from .tasks import TaskNotFoundError, Tasks
    from .ui import show_error
else:
    import command_handlers
    from parser import InputError
    from storage import load_tasks
    from tasks import TaskNotFoundError, Tasks
    from ui import show_error


TASKS = Tasks([])
DATA_FILE = Path("data/inherited-tasks.json")


def run() -> None:
    """Load tasks and run the terminal conversation until the user exits.

    Clears global TASKS and repopulates it from DATA_FILE. Reads terminal input
    and dispatches commands that may mutate TASKS, print messages, and save JSON.
    Displays expected input and missing-task errors, then continues the loop.
    Handles file-read and JSON-decoding errors during loading; unexpected command
    errors propagate. A save failure does not roll back an in-memory change.

    Returns:
        None after bye, end-of-input, or a keyboard interrupt while reading input.

    Raises:
        OSError: If saving task data fails.
        ValueError: If event separators trigger the preserved unpacking error,
            or stored deadline data cannot be interpreted.
    """
    TASKS.clear()
    try:
        TASKS.extend(load_tasks(DATA_FILE))
    except (OSError, json.JSONDecodeError):
        print("Could not read saved tasks. Starting with an empty list.")

    print("bao here. What needs doing?")
    while True:
        try:
            line = input("> ")
        except (EOFError, KeyboardInterrupt):
            command_handlers.handle_bye()
            return

        try:
            if not line.strip():
                command_handlers.handle_empty_input()
            elif line == "bye":
                command_handlers.handle_bye()
                return
            elif line == "list":
                command_handlers.handle_list(TASKS)
            elif line.startswith("todo "):
                command_handlers.handle_todo(line, TASKS, DATA_FILE)
            elif line.startswith("deadline"):
                command_handlers.handle_deadline(line, TASKS, DATA_FILE)
            elif line.startswith("event"):
                command_handlers.handle_event(line, TASKS, DATA_FILE)
            elif line.startswith("recurring"):
                command_handlers.handle_recurring(line, TASKS, DATA_FILE)
            elif line.startswith("mark") or line.startswith("unmark"):
                command_handlers.handle_mark_unmark(line, TASKS, DATA_FILE)
            elif line.startswith("note"):
                command_handlers.handle_note(line, TASKS, DATA_FILE)
            elif line.startswith("delete"):
                command_handlers.handle_delete(line, TASKS, DATA_FILE)
            elif line == "clear":
                command_handlers.handle_clear(TASKS, DATA_FILE)
            elif line.startswith("find"):
                command_handlers.handle_find(line, TASKS)
            elif line.startswith("due"):
                command_handlers.handle_due(line, TASKS)
            else:
                command_handlers.handle_unknown_command()
        except InputError as error:
            show_error(str(error))
        except TaskNotFoundError:
            # Preserve the task number exactly as entered after successful parsing.
            number_text = line.split(maxsplit=2)[1]
            show_error(f"No task {number_text}.")


if __name__ == "__main__":
    run()
