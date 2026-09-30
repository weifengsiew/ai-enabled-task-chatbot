"""Command-line entry point for bao."""

from .tasks import Tasks


def greeting() -> None:
    """
    Prints Bao's opening greeting to the terminal.

    Returns:
    --------
    None.
    """
    print("Hello! I'm bao. What needs doing?")


def farewell() -> None:
    """
    Prints Bao's closing message to the terminal.

    Returns:
    --------
    None.
    """
    print("Later.")


def chat() -> None:
    """
    Runs an interactive task-management session with the saved task collection.
    Reads terminal commands and dispatches task operations until "bye" is entered.
    Prints guidance for unrecognized commands. Successful changes are saved.

    Returns:
    --------
    None.
    """

    tasks = Tasks()

    while True:
        user_response = input("> ")

        if user_response == "bye":
            break

        elif user_response == "list":
            tasks.list_tasks()

        elif user_response.startswith("due"):
            tasks.list_due_tasks(user_response)

        elif user_response.startswith("find"):
            tasks.find_tasks(user_response)

        elif user_response.startswith("mark"):
            tasks.mark_task(user_response)

        elif user_response.startswith("unmark"):
            tasks.unmark_task(user_response)

        elif user_response.startswith("note"):
            tasks.note_task(user_response)

        elif user_response.startswith("delete"):
            tasks.delete_task(user_response)

        elif user_response.startswith(("todo", "deadline", "event", "recurring")):
            tasks.add_task(user_response)

        else:
            print(
                "Never heard of it. Try: todo, deadline, event, recurring, list, due, find, mark, unmark, note, delete, bye."
            )


def main() -> None:
    """
    Runs Bao's command-line interface.
    Prints the opening greeting, starts the chat session,
    and prints the closing message when the session ends normally.

    Returns:
    --------
    None.
    """
    greeting()
    chat()
    farewell()
