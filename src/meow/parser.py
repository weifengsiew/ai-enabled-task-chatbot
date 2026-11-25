"""Parse shared command input formats."""

from __future__ import annotations

import re
from datetime import date, time
from typing import TYPE_CHECKING, TypeVar

if TYPE_CHECKING:
    from .modify_task_commands import CommandDelete, CommandMark, CommandUnmark

    type NumberCommand = CommandMark | CommandUnmark | CommandDelete
    NumberCommandT = TypeVar("NumberCommandT", bound=NumberCommand)
else:
    NumberCommandT = TypeVar("NumberCommandT")


def _parse_number_command(  # noqa: UP047
    command: NumberCommandT,
    user_response: str,
) -> NumberCommandT | str | None:
    """
    Parse a command that accepts one task number.

    Args:
    -----
    command: The numeric command to populate.
    user_response: The user's raw command text.

    Returns:
    --------
    NumberCommandT | str | None:
        The parsed command, a usage message, or None when the keyword does not match.
    """
    matched_keyword = command.match_user_response_with_command_keyword(user_response)
    if not matched_keyword:
        return None

    matched_command_pattern = command.command_pattern.fullmatch(user_response)
    if matched_command_pattern is None:
        return command.unmatched_command_pattern_message

    matched_number_pattern = re.fullmatch(r"\d+", matched_command_pattern.group(1))
    if matched_number_pattern is None:
        return command.unmatched_command_pattern_message

    command.task_number = int(matched_command_pattern.group(1))
    return command


def _parse_datetime_parts(value: str) -> tuple[date, time | None] | None:
    """
    Parse a date and optional four-digit time.

    Args:
    -----
    value: The date and optional time text to parse.

    Returns:
    --------
    tuple[date, time | None] | None: The parsed date and optional time, or None if invalid.
    """

    matched_datetime_pattern = re.fullmatch(
        r"([0-9]{4}-[0-9]{2}-[0-9]{2})(?:\s+([0-9]{4}))?", value
    )
    if matched_datetime_pattern is None:
        return None

    try:
        due_date = date.fromisoformat(matched_datetime_pattern.group(1))
        time_text = matched_datetime_pattern.group(2)

        due_time = (
            time(hour=int(time_text[:2]), minute=int(time_text[2:]))
            if time_text is not None
            else None
        )

    except ValueError:
        return None

    return due_date, due_time
