"""End-to-end command sessions for Bao's chat loop."""

import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import call, patch

from bao.cli import chat


class ChatTests(unittest.TestCase):
    def _run_session(self, commands: list[str]) -> str:
        """
        Runs chat with supplied commands and captures its printed output.
        Verifies that every command is requested and chat returns normally.

        Args:
        -----
        commands (list[str]): The input sequence, ending with "bye".

        Returns:
        --------
        str: The complete printed output, excluding mocked input prompts.
        """
        output = io.StringIO()
        with patch("builtins.input", side_effect=commands) as mock_input:
            with redirect_stdout(output):
                result = chat()

        self.assertIsNone(result)
        self.assertEqual(mock_input.call_args_list, [call("> ")] * len(commands))
        return output.getvalue()

    def test_valid_inputs(self) -> None:
        """
        Verifies all commands in a valid session, including task state changes.

        Returns:
        --------
        None.
        """
        commands = [
            "todo read book",
            "deadline submit report /by friday",
            "event team meeting /from monday /to tuesday",
            "recurring water plants /every sunday",
            "mark 1",
            "note 2 attach receipts",
            "list",
            "unmark 1",
            "list",
            "bye",
        ]
        expected = (
            "Added:\n"
            "[T][ ]read book\n"
            "Added:\n"
            "[D][ ]submit report (by: friday)\n"
            "Added:\n"
            "[E][ ]team meeting (from: monday to: tuesday)\n"
            "Added:\n"
            "[R][ ]water plants (every: sunday)\n"
            "Done:\n"
            "[T][X]read book\n"
            "Noted:\n"
            "[D][ ]submit report (by: friday)\n"
            "Note: attach receipts\n"
            "1. [T][X]read book\n"
            "2. [D][ ]submit report (by: friday)\n"
            "Note: attach receipts\n"
            "3. [E][ ]team meeting (from: monday to: tuesday)\n"
            "4. [R][ ]water plants (every: sunday)\n"
            "That's 3 on your plate.\n"
            "Not done:\n"
            "[T][ ]read book\n"
            "1. [T][ ]read book\n"
            "2. [D][ ]submit report (by: friday)\n"
            "Note: attach receipts\n"
            "3. [E][ ]team meeting (from: monday to: tuesday)\n"
            "4. [R][ ]water plants (every: sunday)\n"
            "That's 4 on your plate.\n"
        )

        self.assertEqual(self._run_session(commands), expected)

    def test_invalid_inputs(self) -> None:
        """
        Verifies invalid commands report errors without ending the session.
        Checks empty collections and out-of-range numbers do not alter tasks.

        Returns:
        --------
        None.
        """
        commands = [
            "hello",
            "",
            "list extra",
            "bye extra",
            "todo",
            "deadline submit report",
            "event meeting /from monday",
            "recurring water plants",
            "mark",
            "mark abc",
            "unmark",
            "unmark abc",
            "note",
            "note abc reminder",
            "note 1",
            "mark 1",
            "unmark 1",
            "note 1 reminder",
            "todo read book",
            "mark 0",
            "mark 2",
            "unmark 0",
            "unmark 2",
            "note 0 reminder",
            "note 2 reminder",
            "list",
            "bye",
        ]
        unknown_command = (
            "Never heard of it. Try: todo, deadline, event, recurring, "
            "list, mark, unmark, note, bye.\n"
        )
        expected = unknown_command * 4 + (
            "Use: todo <description>\n"
            "Use: deadline <description> /by <day>\n"
            "Use: event <description> /from <start> /to <end>\n"
            "Use: recurring <description> /every <day>\n"
            "Use: mark <number>\n"
            "Use: mark <number>\n"
            "Use: unmark <number>\n"
            "Use: unmark <number>\n"
            "Use: note <number> <note>\n"
            "Use: note <number> <note>\n"
            "Use: note <number> <note>\n"
            "No task 1. There are no tasks yet.\n"
            "No task 1. There are no tasks yet.\n"
            "No task 1. There are no tasks yet.\n"
            "Added:\n"
            "[T][ ]read book\n"
            "No task 0. Choose a number from 1 to 1.\n"
            "No task 2. Choose a number from 1 to 1.\n"
            "No task 0. Choose a number from 1 to 1.\n"
            "No task 2. Choose a number from 1 to 1.\n"
            "No task 0. Choose a number from 1 to 1.\n"
            "No task 2. Choose a number from 1 to 1.\n"
            "1. [T][ ]read book\n"
            "That's 1 on your plate.\n"
        )

        self.assertEqual(self._run_session(commands), expected)


if __name__ == "__main__":
    unittest.main()
