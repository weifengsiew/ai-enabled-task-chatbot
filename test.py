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
        Verifies task creation, updates, deletion, and listing with two tasks.

        Returns:
        --------
        None.
        """
        commands = [
            "todo read book",
            "deadline submit report /by friday",
            "mark 2",
            "unmark 2",
            "note 2 attach receipts",
            "delete 1",
            "list",
            "bye",
        ]
        expected = (
            "Added:\n"
            "[T][ ]read book\n"
            "Added:\n"
            "[D][ ]submit report (by: friday)\n"
            "Done:\n"
            "[D][X]submit report (by: friday)\n"
            "Not done:\n"
            "[D][ ]submit report (by: friday)\n"
            "Noted:\n"
            "[D][ ]submit report (by: friday)\n"
            "Note: attach receipts\n"
            "Deleted:\n"
            "[T][ ]read book\n"
            "1 task left.\n"
            "1. [D][ ]submit report (by: friday)\n"
            "Note: attach receipts\n"
            "That's 1 on your plate.\n"
        )

        self.assertEqual(self._run_session(commands), expected)

    def test_invalid_inputs(self) -> None:
        """
        Verifies one invalid example per command without ending the session.

        Returns:
        --------
        None.
        """
        commands = [
            "list extra",
            "bye extra",
            "todo",
            "deadline submit report",
            "event meeting /from monday",
            "recurring water plants",
            "mark abc",
            "unmark abc",
            "note 1",
            "delete abc",
            "bye",
        ]
        unknown_command = (
            "Never heard of it. Try: todo, deadline, event, recurring, "
            "list, mark, unmark, note, delete, bye.\n"
        )
        expected = unknown_command * 2 + (
            "Use: todo <description>\n"
            "Use: deadline <description> /by <day>\n"
            "Use: event <description> /from <start> /to <end>\n"
            "Use: recurring <description> /every <day>\n"
            "Use: mark <number>\n"
            "Use: unmark <number>\n"
            "Use: note <number> <note>\n"
            "Use: delete <number>\n"
        )

        self.assertEqual(self._run_session(commands), expected)


if __name__ == "__main__":
    unittest.main()
