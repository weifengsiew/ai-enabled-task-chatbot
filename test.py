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
        Verifies task operations, deadline formatting, and date-based queries.

        Returns:
        --------
        None.
        """
        steps = [
            (
                "todo read book",
                "Added:\n"
                "[T][ ]read book\n",
            ),
            (
                "deadline submit report /by 2026-03-02",
                "Added:\n"
                "[D][ ]submit report (by: Mar 02 2026)\n",
            ),
            (
                "deadline submit abstract /by 2026-03-01 1800",
                "Added:\n"
                "[D][ ]submit abstract (by: Mar 01 2026, 6pm)\n",
            ),
            (
                "mark 2",
                "Done:\n"
                "[D][X]submit report (by: Mar 02 2026)\n",
            ),
            (
                "unmark 2",
                "Not done:\n"
                "[D][ ]submit report (by: Mar 02 2026)\n",
            ),
            (
                "note 2 attach receipts",
                "Noted:\n"
                "[D][ ]submit report (by: Mar 02 2026)\n"
                "Note: attach receipts\n",
            ),
            (
                "delete 1",
                "Deleted:\n"
                "[T][ ]read book\n"
                "2 tasks left.\n",
            ),
            (
                "list",
                "1. [D][ ]submit report (by: Mar 02 2026)\n"
                "Note: attach receipts\n"
                "2. [D][ ]submit abstract (by: Mar 01 2026, 6pm)\n"
                "That's 2 on your plate.\n",
            ),
            (
                "deadline send slides /by 2026-03-01 2100",
                "Added:\n"
                "[D][ ]send slides (by: Mar 01 2026, 9pm)\n",
            ),
            (
                "mark 3",
                "Done:\n"
                "[D][X]send slides (by: Mar 01 2026, 9pm)\n",
            ),
            (
                "deadline renew licence /by 2026-03-01",
                "Added:\n"
                "[D][ ]renew licence (by: Mar 01 2026)\n",
            ),
            (
                "todo read another book",
                "Added:\n"
                "[T][ ]read another book\n",
            ),
            (
                "event meeting /from 2026-03-01 /to 2026-03-02",
                "Added:\n"
                "[E][ ]meeting (from: 2026-03-01 to: 2026-03-02)\n",
            ),
            (
                "recurring water plants /every sunday",
                "Added:\n"
                "[R][ ]water plants (every: sunday)\n",
            ),
            (
                "due 2026-03-01",
                "1. [D][ ]submit abstract (by: Mar 01 2026, 6pm)\n"
                "2. [D][X]send slides (by: Mar 01 2026, 9pm)\n"
                "3. [D][ ]renew licence (by: Mar 01 2026)\n",
            ),
            (
                "due 2026-03-03",
                "No deadlines due on 2026-03-03.\n",
            ),
            ("bye", ""),
        ]
        commands = [command for command, _ in steps]
        expected = "".join(output for _, output in steps)

        self.assertEqual(self._run_session(commands), expected)

    def test_invalid_inputs(self) -> None:
        """
        Verifies invalid commands, deadlines, and queries leave the task list empty.

        Returns:
        --------
        None.
        """
        unknown_command = (
            "Never heard of it. Try: todo, deadline, event, recurring, "
            "list, due, mark, unmark, note, delete, bye.\n"
        )
        steps = [
            ("list extra", unknown_command),
            ("bye extra", unknown_command),
            (
                "todo",
                "Use: todo <description>\n",
            ),
            (
                "deadline submit report",
                "Use: deadline <description> /by YYYY-MM-DD [HHMM]\n",
            ),
            (
                "event meeting /from monday",
                "Use: event <description> /from <start> /to <end>\n",
            ),
            (
                "recurring water plants",
                "Use: recurring <description> /every <day>\n",
            ),
            (
                "mark abc",
                "Use: mark <number>\n",
            ),
            (
                "unmark abc",
                "Use: unmark <number>\n",
            ),
            (
                "note 1",
                "Use: note <number> <note>\n",
            ),
            (
                "delete abc",
                "Use: delete <number>\n",
            ),
            (
                "deadline submit report /by 2026-02-30",
                "Invalid deadline. Use a valid date as YYYY-MM-DD, optionally followed by a time as HHMM (0000–2359).\n",
            ),
            (
                "deadline submit report /by 2026-03-01 2400",
                "Invalid deadline. Use a valid date as YYYY-MM-DD, optionally followed by a time as HHMM (0000–2359).\n",
            ),
            (
                "due",
                "Use: due YYYY-MM-DD\n",
            ),
            (
                "due 2026-3-01",
                "Use: due YYYY-MM-DD\n",
            ),
            (
                "due 2026-03-01 1800",
                "Use: due YYYY-MM-DD\n",
            ),
            (
                "due 2026-02-30",
                "Invalid date. Use a valid calendar date as YYYY-MM-DD.\n",
            ),
            (
                "list",
                "That's 0 on your plate.\n",
            ),
            ("bye", ""),
        ]
        commands = [command for command, _ in steps]
        expected = "".join(output for _, output in steps)

        self.assertEqual(self._run_session(commands), expected)


if __name__ == "__main__":
    unittest.main()
