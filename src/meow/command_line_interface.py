"""Command-line entry point for Meow."""

from .read_task_commands import Command, CommandBye
from .tasks import Tasks


def greeting() -> None:
    """Print Meow's greeting."""
    print("Hello! I'm meow. What needs doing?")


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
    """Print Meow's closing message."""
    print("Later.")


def main() -> None:
    """
    Run Meow's command-line interface.

    Returns:
    --------
    None.
    """
    greeting()
    chat()
    farewell()
