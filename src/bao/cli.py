"""Command-line entry point for Bao."""

from .commands import Command, CommandBye
from .tasks import Tasks


def greeting() -> None:
    """Prints Bao's opening greeting."""
    print("Hello! I'm bao. What needs doing?")


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
        parsed = Command.parse_user_response_with_command_pattern(user_response)

        if parsed is None:
            continue

        if isinstance(parsed, str):
            print(parsed)
            continue

        if isinstance(parsed, CommandBye):
            return

        print(parsed.execute_command(tasks))


def farewell() -> None:
    """Prints Bao's closing message."""
    print("Later.")


def main() -> None:
    """
    Runs Bao's command-line interface.

    Returns:
    --------
    None.
    """
    greeting()
    chat()
    farewell()
