"""Parse input values for the inherited Bao application."""

from datetime import datetime


def parse_task_index(text: str) -> int:
    """Convert a task-number argument to a zero-based index.

    Args:
        text: Task-number text supplied by the user.

    Returns:
        The parsed number minus one; task existence is checked by the caller.

    Raises:
        ValueError: If the text cannot be converted to an integer.
    """
    try:
        return int(text) - 1
    except ValueError:
        raise ValueError("The task number must be a whole number.") from None


def parse_required_pair(
    text: str, separator: str, error_message: str
) -> tuple[str, str]:
    """Split input once at a separator and require two nonempty values.

    Args:
        text: Command arguments to split.
        separator: Nonempty delimiter separating the required values.
        error_message: Input-error message to use when either value is missing.

    Returns:
        The two values with surrounding whitespace removed.

    Raises:
        ValueError: If the separator or either required value is missing.
    """
    if separator not in text:
        raise ValueError(error_message)
    first, second = (part.strip() for part in text.split(separator, 1))
    if not first or not second:
        raise ValueError(error_message)
    return first, second


def parse_deadline_datetime(text: str) -> datetime:
    """Parse a deadline date with an optional four-digit time.

    Args:
        text: Date text in YYYY-MM-DD or YYYY-MM-DD HHMM format.

    Returns:
        The parsed datetime, using midnight when no time is supplied.

    Raises:
        ValueError: If neither supported date format can parse the text.
    """
    for pattern in ("%Y-%m-%d %H%M", "%Y-%m-%d"):
        try:
            return datetime.strptime(text, pattern)
        except ValueError:
            pass
    raise ValueError("Use YYYY-MM-DD with an optional four-digit time.")
