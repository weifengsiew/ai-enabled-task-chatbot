"""Command-line entry point for bao."""

from .ui import chat as _chat
from .ui import farewell as _farewell
from .ui import greeting as _greeting


def greeting() -> None:
    """Prints Bao's opening greeting."""
    _greeting()


def chat() -> None:
    """Runs Bao's interactive conversation."""
    _chat()


def farewell() -> None:
    """Prints Bao's closing message."""
    _farewell()


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
