"""Entry point and input loop for the inherited Bao application."""

import json
from pathlib import Path
from typing import Any

if __package__:
    from . import command_handlers
else:
    import command_handlers


TASKS: list[dict[str, Any]] = []
DATA_FILE = Path("data/inherited-tasks.json")


def run() -> None:
    """Load saved tasks and process user input until exit; return None."""
    TASKS.clear()
    if DATA_FILE.exists():
        try:
            TASKS.extend(json.loads(DATA_FILE.read_text()))
        except (OSError, json.JSONDecodeError):
            print("Could not read saved tasks. Starting with an empty list.")

    print("bao here. What needs doing?")
    while True:
        try:
            line = input("> ")
        except (EOFError, KeyboardInterrupt):
            command_handlers.handle_bye()
            return

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


if __name__ == "__main__":
    run()
