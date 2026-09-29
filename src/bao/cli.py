"""Command-line entry point for bao."""


def farewell() -> None:
    """End the conversation."""
    print("Later.")


def main() -> None:
    """Run bao."""
    print("Hello! I'm bao. What needs doing?")
    farewell()
