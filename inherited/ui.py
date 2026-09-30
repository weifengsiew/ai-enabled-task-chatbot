"""Display formatting for the inherited Bao application."""

from datetime import datetime


def format_deadline(when: datetime) -> str:
    """Format a deadline date and optional time for display.

    Args:
        when: Deadline date and time to format.

    Returns:
        The date alone at midnight, otherwise the date and hour with am/pm.
    """
    if when.hour == 0 and when.minute == 0:
        return when.strftime("%b %d %Y")
    return when.strftime("%b %d %Y, ") + when.strftime("%I%p").lstrip("0").lower()
