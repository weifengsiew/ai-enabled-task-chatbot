"""Command-line entry point for Bao."""

from .read_task_commands import Command, CommandBye
from .tasks import Tasks


def greeting() -> None:
    """Print Bao's greeting."""
    print("Hello! I'm bao. What needs doing?")


def chat() -> None:
    """
    Run the interactive conversation.

    Returns:
    --------
    None.
    """
    tasks = Tasks()

    while True:
        user_response = input("> ")
        matched_command = Command.parse_user_response_with_command_pattern(
            user_response
        )

        if matched_command is None:
            continue

        if isinstance(matched_command, str):
            print(matched_command)
            continue

        if isinstance(matched_command, CommandBye):
            return

        print(matched_command.execute_command(tasks))


def farewell() -> None:
    """Print Bao's closing message."""
    print("Later.")


def main() -> None:
    """
    Run Bao's command-line interface.

    Returns:
    --------
    None.
    """
    greeting()
    chat()
    farewell()
