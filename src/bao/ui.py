"""Bao's conversation loop and terminal display messages."""

from .parser import Command, ParseError, parse_command
from .task import Task
from .tasks import Tasks


def greeting() -> None:
    """Prints Bao's opening greeting."""
    print("Hello! I'm bao. What needs doing?")


def farewell() -> None:
    """Prints Bao's closing message."""
    print("Later.")


def chat() -> None:
    """
    Runs the interactive task-management conversation.

    Returns:
    --------
    None.
    """
    tasks = Tasks()

    while True:
        user_response = input("> ")
        parsed = parse_command(user_response)

        if isinstance(parsed, ParseError):
            print(parsed.message)
            continue

        if parsed.name == "bye":
            return

        _handle_command(tasks, parsed)


def _handle_command(tasks: Tasks, command: Command) -> None:
    """
    Performs one validated command and prints its result.

    Args:
    -----
    tasks (Tasks): The task-list service for this conversation.
    command (Command): A command produced by the parser.

    Returns:
    --------
    None.
    """
    if command.name == "list":
        _display_task_list(tasks)
    elif command.name == "todo":
        todo_task = tasks.add_todo(_required(command.description))
        print(f"Added:\n{todo_task}")
    elif command.name == "deadline":
        deadline_task = tasks.add_deadline(
            _required(command.description),
            _required(command.due_date),
            command.due_time,
        )
        print(f"Added:\n{deadline_task}")
    elif command.name == "event":
        event_task = tasks.add_event(
            _required(command.description),
            _required(command.start),
            _required(command.end),
        )
        print(f"Added:\n{event_task}")
    elif command.name == "recurring":
        recurring_task = tasks.add_recurring(
            _required(command.description), _required(command.day)
        )
        print(f"Added:\n{recurring_task}")
    elif command.name == "due":
        matches = tasks.due_tasks(_required(command.due_date))
        _display_due_matches(matches, _required(command.due_date))
    elif command.name == "find":
        query = _required(command.query)
        matches = tasks.find_tasks(query)
        if not matches:
            print(f'No tasks found matching "{query}".')
        else:
            _display_numbered(matches)
    elif command.name == "mark":
        task_number = _required(command.task_number)
        changed_task = tasks.mark(task_number)
        if changed_task is not None:
            print(f"Done:\n{changed_task}")
        else:
            _display_missing_task(tasks, task_number)
    elif command.name == "unmark":
        task_number = _required(command.task_number)
        changed_task = tasks.unmark(task_number)
        if changed_task is not None:
            print(f"Not done:\n{changed_task}")
        else:
            _display_missing_task(tasks, task_number)
    elif command.name == "note":
        task_number = _required(command.task_number)
        changed_task = tasks.add_note(task_number, _required(command.note))
        if changed_task is not None:
            print(f"Noted:\n{changed_task}")
        else:
            _display_missing_task(tasks, task_number)
    elif command.name == "delete":
        task_number = _required(command.task_number)
        result = tasks.delete(task_number)
        if result is None:
            _display_missing_task(tasks, task_number)
        else:
            deleted_task, remaining = result
            print(f"Deleted:\n{deleted_task}")
            print(f"{remaining} tasks left.")


def _display_task_list(tasks: Tasks) -> None:
    """Prints all tasks followed by the incomplete-task count."""
    _display_numbered(tasks.all_tasks())
    print(f"That's {tasks.incomplete_count()} on your plate.")


def _display_due_matches(matches: list[Task], query_date: object) -> None:
    """Prints due-task matches or the original no-match message."""
    if not matches:
        print(f"No deadlines due on {query_date}.")
        return
    _display_numbered(matches)


def _display_numbered(tasks: list[Task]) -> None:
    """Prints tasks with one-based display numbering."""
    for number, task in enumerate(tasks, start=1):
        print(f"{number}. {task}")


def _display_missing_task(tasks: Tasks, task_number: int) -> None:
    """Prints the existing task-number guidance."""
    all_tasks = tasks.all_tasks()
    if all_tasks:
        message = f"Choose a number from 1 to {len(all_tasks)}."
    else:
        message = "There are no tasks yet."
    print(f"No task {task_number}. {message}")


def _required[Value](value: Value | None) -> Value:
    """Returns a value that a validated command guarantees is present."""
    if value is None:
        raise AssertionError("validated command is missing a required value")
    return value
