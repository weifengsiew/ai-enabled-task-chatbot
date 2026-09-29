"""Command-line entry point for bao."""


def farewell() -> None:
    """End the conversation."""
    print("Later.")

def chat() -> None:
    """Chat with the user."""

    tasks = []

    while True:
        user_response = input("> ")

        if user_response == "bye":
            break

        if user_response == "list":
            for i, task in enumerate(tasks, start=1):
                print(f"{i}. {task}")
        else:
            tasks.append(user_response)
            print(f"Added {user_response}")

def main() -> None:
    """Run bao."""
    print("Hello! I'm bao. What needs doing?")
    chat()
    farewell()
