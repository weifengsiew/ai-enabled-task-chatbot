"""Parse Bao input into commands or useful input errors."""

import re
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, time

UNKNOWN_COMMAND = (
    "Never heard of it. Try: todo, deadline, event, recurring, list, due, find, "
    "mark, unmark, note, delete, bye."
)


@dataclass(frozen=True)
class Command:
    """A validated command and its parsed values."""

    name: str
    description: str | None = None
    due_date: date | None = None
    due_time: time | None = None
    start: str | None = None
    end: str | None = None
    day: str | None = None
    task_number: int | None = None
    note: str | None = None
    query: str | None = None


@dataclass(frozen=True)
class ParseError:
    """A user-facing input error."""

    message: str


CommandParser = Callable[[re.Match[str]], Command | ParseError]


def parse_command(user_response: str) -> Command | ParseError:
    """
    Parses one complete user response.

    Args:
    -----
    user_response (str): The command text entered by the user.

    Returns:
    --------
    Command | ParseError: A validated command or its user-facing error.
    """
    if user_response == "bye":
        return Command("bye")
    if user_response == "list":
        return Command("list")

    patterns: tuple[tuple[str, CommandParser], ...] = (
        (r"^todo\s+(.+)$", _parse_todo),
        (r"^deadline\s+(.+?)\s+/by\s+(.+)$", _parse_deadline_command),
        (r"^event\s+(.+?)\s+/from\s+(.+?)\s+/to\s+(.+)$", _parse_event),
        (r"^recurring\s+(.+?)\s+/every\s+(\w+)$", _parse_recurring),
        (r"^due\s+(.+)$", _parse_due),
        (r"^find\s+(.+)$", _parse_find),
        (r"^mark\s+(.+)$", _parse_mark),
        (r"^unmark\s+(.+)$", _parse_unmark),
        (r"^note\s+(\d+)\s+(.+)$", _parse_note),
        (r"^delete\s+(.+)$", _parse_delete),
    )

    for pattern, parser in patterns:
        match = re.fullmatch(pattern, user_response)
        if match is not None:
            return parser(match)

    if user_response == "todo" or user_response.startswith("todo "):
        return ParseError("Use: todo <description>")
    if user_response == "deadline" or user_response.startswith("deadline "):
        return ParseError("Use: deadline <description> /by YYYY-MM-DD [HHMM]")
    if user_response == "event" or user_response.startswith("event "):
        return ParseError("Use: event <description> /from <start> /to <end>")
    if user_response == "recurring" or user_response.startswith("recurring "):
        return ParseError("Use: recurring <description> /every <day>")
    if user_response == "note" or user_response.startswith("note "):
        return ParseError("Use: note <number> <note>")
    if user_response == "due" or user_response.startswith("due "):
        return ParseError("Use: due YYYY-MM-DD")
    if user_response == "find" or user_response.startswith("find "):
        return ParseError("Use: find <text>")
    if user_response.startswith("mark "):
        return ParseError("Use: mark <number>")
    if user_response.startswith("unmark "):
        return ParseError("Use: unmark <number>")
    if user_response.startswith("delete "):
        return ParseError("Use: delete <number>")
    return ParseError(UNKNOWN_COMMAND)


def _parse_todo(match: re.Match[str]) -> Command:
    """Builds a parsed to-do command."""
    return Command("todo", description=match.group(1))


def _parse_deadline_command(match: re.Match[str]) -> Command | ParseError:
    """Builds a parsed deadline command or its validation error."""
    parsed = _parse_deadline(match.group(2))
    if parsed is None:
        return ParseError(
            "Invalid deadline. Use a valid date as YYYY-MM-DD, "
            "optionally followed by a time as HHMM (0000–2359)."
        )
    due_date, due_time = parsed
    return Command(
        "deadline",
        description=match.group(1),
        due_date=due_date,
        due_time=due_time,
    )


def _parse_event(match: re.Match[str]) -> Command:
    """Builds a parsed event command."""
    return Command(
        "event",
        description=match.group(1),
        start=match.group(2),
        end=match.group(3),
    )


def _parse_recurring(match: re.Match[str]) -> Command:
    """Builds a parsed recurring command."""
    return Command("recurring", description=match.group(1), day=match.group(2))


def _parse_due(match: re.Match[str]) -> Command | ParseError:
    """Builds a parsed due command or its validation error."""
    value = match.group(1)
    if re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value) is None:
        return ParseError("Use: due YYYY-MM-DD")
    try:
        query_date = date.fromisoformat(value)
    except ValueError:
        return ParseError("Invalid date. Use a valid calendar date as YYYY-MM-DD.")
    return Command("due", due_date=query_date)


def _parse_find(match: re.Match[str]) -> Command | ParseError:
    """Builds a parsed find command or its usage error."""
    query = match.group(1)
    if re.fullmatch(r"\S(?:.*\S)?\s*", query) is None:
        return ParseError("Use: find <text>")
    return Command("find", query=query.strip())


def _parse_mark(match: re.Match[str]) -> Command | ParseError:
    """Builds a parsed mark command or its usage error."""
    return _parse_number_command(match.group(1), "mark")


def _parse_unmark(match: re.Match[str]) -> Command | ParseError:
    """Builds a parsed unmark command or its usage error."""
    return _parse_number_command(match.group(1), "unmark")


def _parse_delete(match: re.Match[str]) -> Command | ParseError:
    """Builds a parsed delete command or its usage error."""
    return _parse_number_command(match.group(1), "delete")


def _parse_number_command(value: str, command_name: str) -> Command | ParseError:
    """Parses a one-number command."""
    if re.fullmatch(r"\d+", value) is None:
        return ParseError(f"Use: {command_name} <number>")
    return Command(command_name, task_number=int(value))


def _parse_note(match: re.Match[str]) -> Command:
    """Builds a parsed note command."""
    return Command("note", task_number=int(match.group(1)), note=match.group(2))


def _parse_deadline(value: str) -> tuple[date, time | None] | None:
    """Parses an ISO date and optional four-digit time."""
    deadline_match = re.fullmatch(
        r"([0-9]{4}-[0-9]{2}-[0-9]{2})(?:\s+([0-9]{4}))?", value
    )
    if deadline_match is None:
        return None

    try:
        due_date = date.fromisoformat(deadline_match.group(1))
        time_text = deadline_match.group(2)
        due_time = (
            time(hour=int(time_text[:2]), minute=int(time_text[2:]))
            if time_text is not None
            else None
        )
    except ValueError:
        return None
    return due_date, due_time
