"""Define commands that modify existing tasks."""

from __future__ import annotations

import re

from .parser import _parse_number_command
from .read_task_commands import (
    Command,
    _format_missing_task_message,
    _get_task_by_number,
)
from .tasks import Tasks


class CommandMark(Command):
    """Mark a task as done."""

    def __init__(self, task_number: int) -> None:
        self.command_keyword = "mark"
        self.command_usage = "mark <number>"
        self.command_pattern = re.compile(r"^mark\s+(.+)$")
        self.unmatched_command_pattern_message = f"Use: {self.command_usage}"
        self.success_message_prefix = "Done:"
        self.task_number = task_number

    @classmethod
    def match_user_response_with_command_keyword(cls, user_response: str) -> bool:
        """Return whether user response matches command keyword."""

        command = cls(0)
        matched_keyword = (
            command.command_keyword == user_response
            or user_response.startswith(f"{command.command_keyword} ")
        )
        return matched_keyword

    @classmethod
    def parse_user_response_with_command_pattern(
        cls, user_response: str
    ) -> CommandMark | str | None:
        """Return command if user response matches command pattern, else None."""
        return _parse_number_command(cls(0), user_response)

    def execute_command(self, tasks: Tasks) -> str:
        """Execute the command."""

        task = _get_task_by_number(tasks, self.task_number)
        if task is None:
            return _format_missing_task_message(tasks, self.task_number)

        task.done = True
        tasks.save()

        success_message = f"{self.success_message_prefix}\n{task}"
        return success_message


class CommandUnmark(Command):
    """Mark a task as incomplete."""

    def __init__(self, task_number: int) -> None:
        self.command_keyword = "unmark"
        self.command_usage = "unmark <number>"
        self.command_pattern = re.compile(r"^unmark\s+(.+)$")
        self.unmatched_command_pattern_message = f"Use: {self.command_usage}"
        self.success_message_prefix = "Not done:"
        self.task_number = task_number

    @classmethod
    def match_user_response_with_command_keyword(cls, user_response: str) -> bool:
        """Return whether user response matches command keyword."""

        command = cls(0)
        matched_keyword = (
            command.command_keyword == user_response
            or user_response.startswith(f"{command.command_keyword} ")
        )
        return matched_keyword

    @classmethod
    def parse_user_response_with_command_pattern(
        cls, user_response: str
    ) -> CommandUnmark | str | None:
        """Return command if user response matches command pattern, else None."""
        return _parse_number_command(cls(0), user_response)

    def execute_command(self, tasks: Tasks) -> str:
        """Execute the command."""

        task = _get_task_by_number(tasks, self.task_number)
        if task is None:
            return _format_missing_task_message(tasks, self.task_number)

        task.done = False
        tasks.save()

        success_message = f"{self.success_message_prefix}\n{task}"
        return success_message


class CommandNote(Command):
    """Replace a task's note."""

    def __init__(self, task_number: int, note: str) -> None:
        self.command_keyword = "note"
        self.command_usage = "note <number> <note>"
        self.command_pattern = re.compile(r"^note\s+(\d+)\s+(.+)$")
        self.unmatched_command_pattern_message = f"Use: {self.command_usage}"
        self.success_message_prefix = "Noted:"
        self.task_number = task_number
        self.note = note

    @classmethod
    def match_user_response_with_command_keyword(cls, user_response: str) -> bool:
        """Return whether user response matches command keyword."""

        command = cls(0, "")
        matched_keyword = (
            command.command_keyword == user_response
            or user_response.startswith(f"{command.command_keyword} ")
        )
        return matched_keyword

    @classmethod
    def parse_user_response_with_command_pattern(
        cls, user_response: str
    ) -> CommandNote | str | None:
        """Return command if user response matches command pattern, else None."""
        matched_keyword = cls.match_user_response_with_command_keyword(user_response)
        if not matched_keyword:
            return None

        command = cls(0, "")
        matched_command_pattern = command.command_pattern.fullmatch(user_response)
        if matched_command_pattern is None:
            return command.unmatched_command_pattern_message

        parsed_command = cls(
            int(matched_command_pattern.group(1)), matched_command_pattern.group(2)
        )
        return parsed_command

    def execute_command(self, tasks: Tasks) -> str:
        """Execute the command."""

        task = _get_task_by_number(tasks, self.task_number)
        if task is None:
            return _format_missing_task_message(tasks, self.task_number)

        task.note = self.note
        tasks.save()

        success_message = f"{self.success_message_prefix}\n{task}"
        return success_message


class CommandDelete(Command):
    """Delete a task."""

    def __init__(self, task_number: int) -> None:
        self.command_keyword = "delete"
        self.command_usage = "delete <number>"
        self.command_pattern = re.compile(r"^delete\s+(.+)$")
        self.unmatched_command_pattern_message = f"Use: {self.command_usage}"
        self.success_message_prefix = "Deleted:"
        self.task_number = task_number

    @classmethod
    def match_user_response_with_command_keyword(cls, user_response: str) -> bool:
        """Return whether user response matches command keyword."""

        command = cls(0)
        matched_keyword = (
            command.command_keyword == user_response
            or user_response.startswith(f"{command.command_keyword} ")
        )
        return matched_keyword

    @classmethod
    def parse_user_response_with_command_pattern(
        cls, user_response: str
    ) -> CommandDelete | str | None:
        """Return command if user response matches command pattern, else None."""
        return _parse_number_command(cls(0), user_response)

    def execute_command(self, tasks: Tasks) -> str:
        """Execute the command."""

        task = _get_task_by_number(tasks, self.task_number)
        if task is None:
            return _format_missing_task_message(tasks, self.task_number)

        deleted_task = tasks.pop(self.task_number - 1)
        tasks.save()

        success_message = (
            f"{self.success_message_prefix}\n{deleted_task}\n{len(tasks)} tasks left."
        )
        return success_message
