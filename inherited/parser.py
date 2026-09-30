"""Parse input values for the inherited Bao application."""

from datetime import date, datetime


class InputError(ValueError):
    """An expected input-validation error suitable for display to the user."""


def parse_task_index(text: str) -> int:
    """Convert a task-number argument to a zero-based index.

    Args:
        text: Task-number text supplied by the user.

    Returns:
        The parsed number minus one; task existence is checked by the caller.

    Raises:
        InputError: If the text cannot be converted to an integer.
    """
    try:
        return int(text) - 1
    except ValueError:
        raise InputError("The task number must be a whole number.") from None


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
        InputError: If the separator or either required value is missing.
    """
    if separator not in text:
        raise InputError(error_message)
    first, second = (part.strip() for part in text.split(separator, 1))
    if not first or not second:
        raise InputError(error_message)
    return first, second


def parse_deadline_datetime(text: str) -> datetime:
    """Parse a deadline date with an optional four-digit time.

    Args:
        text: Date text in YYYY-MM-DD or YYYY-MM-DD HHMM format.

    Returns:
        The parsed datetime, using midnight when no time is supplied.

    Raises:
        InputError: If neither supported date format can parse the text.
    """
    for pattern in ("%Y-%m-%d %H%M", "%Y-%m-%d"):
        try:
            # Deadlines represent local wall-clock values without a timezone.
            return datetime.strptime(text, pattern)  # noqa: DTZ007
        except ValueError:
            pass
    raise InputError("Use YYYY-MM-DD with an optional four-digit time.")


def parse_event(line: str) -> tuple[str, str, str]:
    """Parse an event command's description, start, and end text.

    Args:
        line: Raw event command text.

    Returns:
        The description, start, and end with surrounding whitespace removed.

    Raises:
        InputError: If separators or required values are missing.
        ValueError: If /to occurs only before /from, preserving the existing
            unpacking error.
    """
    rest = line[len("event") :].strip()
    if "/from" not in rest or "/to" not in rest:
        raise InputError("An event needs a description, /from, and /to.")
    description, times = (part.strip() for part in rest.split("/from", 1))
    start, end = (part.strip() for part in times.split("/to", 1))
    if not description or not start or not end:
        raise InputError("An event needs a description, /from, and /to.")
    return description, start, end


def parse_note(line: str) -> tuple[int, str]:
    """Parse a note command's task index and note text.

    Args:
        line: Raw note command text.

    Returns:
        The zero-based task index and note, preserving whitespace within the note.

    Raises:
        InputError: If arguments are missing or the task number is not an integer.
    """
    pieces = line.split(maxsplit=2)
    if len(pieces) != 3:
        raise InputError("Use note NUMBER TEXT, for example: note 2 ask about funding.")
    return parse_task_index(pieces[1]), pieces[2]


def parse_due_date(text: str) -> date:
    """Parse the calendar date supplied to a due command.

    Args:
        text: Date text in YYYY-MM-DD format.

    Returns:
        The parsed calendar date.

    Raises:
        InputError: If the date text cannot be parsed.
    """
    try:
        # Only the calendar date is used.
        return datetime.strptime(text, "%Y-%m-%d").date()  # noqa: DTZ007
    except ValueError:
        raise InputError("Use due YYYY-MM-DD.") from None


def parse_task_number_command(line: str, error_message: str) -> int:
    """Parse a command followed by exactly one task-number argument.

    Args:
        line: Raw command text.
        error_message: Usage message for an incorrect argument count.

    Returns:
        The zero-based task index; task existence is checked by the caller.

    Raises:
        InputError: If the argument count or task number is invalid.
    """
    pieces = line.split()
    if len(pieces) != 2:
        raise InputError(error_message)
    return parse_task_index(pieces[1])


def parse_required_text(text: str, error_message: str) -> str:
    """Strip surrounding whitespace and require a nonempty argument.

    Args:
        text: Argument text after the command prefix.
        error_message: Input-error message for an empty argument.

    Returns:
        The argument with surrounding whitespace removed.

    Raises:
        InputError: If the stripped argument is empty.
    """
    value = text.strip()
    if not value:
        raise InputError(error_message)
    return value


def parse_deadline(line: str) -> tuple[str, datetime]:
    """Parse a deadline command's description and due datetime.

    Args:
        line: Raw deadline command text.

    Returns:
        The stripped description and parsed deadline datetime.

    Raises:
        InputError: If required arguments are missing or the date is invalid.
    """
    rest = line[len("deadline") :].strip()
    description, when_text = parse_required_pair(
        rest, "/by", "A deadline needs something to do and a /by."
    )
    return description, parse_deadline_datetime(when_text)


def parse_recurring(line: str) -> tuple[str, str]:
    """Parse a recurring command's description and interval.

    Args:
        line: Raw recurring command text.

    Returns:
        The description and interval with surrounding whitespace removed.

    Raises:
        InputError: If the separator or either required value is missing.
    """
    rest = line[len("recurring") :].strip()
    return parse_required_pair(
        rest, "/every", "A recurring task needs something to do and an /every."
    )


def parse_todo(line: str) -> str:
    """Parse a to-do command's required description.

    Args:
        line: Raw to-do command text.

    Returns:
        The description with surrounding whitespace removed.

    Raises:
        InputError: If the description is empty.
    """
    return parse_required_text(line[5:], "A to-do needs something to do.")


def parse_find(line: str) -> str:
    """Parse a find command's required search query.

    Args:
        line: Raw find command text.

    Returns:
        The search query with surrounding whitespace removed.

    Raises:
        InputError: If the search query is empty.
    """
    return parse_required_text(line[len("find") :], "Tell me what to find.")


def parse_due(line: str) -> date:
    """Parse a due command's calendar date.

    Args:
        line: Raw due command text.

    Returns:
        The parsed calendar date.

    Raises:
        InputError: If the date is missing or invalid.
    """
    date_text = line[len("due") :].strip()
    return parse_due_date(date_text)


def parse_delete(line: str) -> int:
    """Parse a delete command's task index.

    Args:
        line: Raw delete command text.

    Returns:
        The zero-based task index; task existence is checked by the caller.

    Raises:
        InputError: If the argument count or task number is invalid.
    """
    return parse_task_number_command(
        line, "Tell me which task to delete, for example: delete 2."
    )


def parse_mark_unmark(line: str) -> tuple[str, int]:
    """Parse a mark or unmark command and its task index.

    Args:
        line: Raw mark or unmark command text.

    Returns:
        The command name and zero-based task index.

    Raises:
        InputError: If the argument count or task number is invalid.
        IndexError: If no command name is supplied, preserving existing behavior.
    """
    command = line.split()[0]
    index = parse_task_number_command(
        line, f"Tell me which task to {command}, for example: {command} 2."
    )
    return command, index
