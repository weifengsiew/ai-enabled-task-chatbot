"""End-to-end command sessions for Bao's chat loop."""

import io
import json
import unittest
from contextlib import chdir, redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import call, patch

from bao.cli import chat


class ChatTests(unittest.TestCase):
    def setUp(self) -> None:
        """
        Isolates each test's saved data in a temporary working directory.

        Returns:
        --------
        None.
        """
        directory = self.enterContext(TemporaryDirectory())
        # Isolate test data.
        self.enterContext(chdir(directory))

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

    def _assert_session(self, steps: list[tuple[str, str]]) -> None:
        """
        Runs command/output pairs and verifies the complete session output.

        Args:
        -----
        steps (list[tuple[str, str]]): Commands paired with expected responses,
            ending with ("bye", "").

        Returns:
        --------
        None.
        """
        commands = [command for command, _ in steps]
        expected = "".join(output for _, output in steps)
        self.assertEqual(self._run_session(commands), expected)

    def test_valid_inputs(self) -> None:
        """
        Verifies every command using a shared set of five tasks.
        Checks case-insensitive partial-word searches preserve original spelling.

        Returns:
        --------
        None.
        """
        updated_list = (
            "1. [T][ ]read paper\n"
            "2. [D][ ]renew licence (by: Mar 01 2026)\n"
            "Note: attach receipts\n"
            "3. [D][X]submit Paper (by: Mar 01 2026, 6pm)\n"
            "4. [E][ ]meeting (from: 2026-03-01 to: 2026-03-02)\n"
            "5. [R][ ]water plants (every: sunday)\n"
            "That's 4 on your plate.\n"
        )
        self._assert_session([
            # Create todo, deadline (date-only and timed), event, and recurring tasks.
            ("todo read paper",
             "Added:\n[T][ ]read paper\n"),
            ("deadline renew licence /by 2026-03-01",
             "Added:\n[D][ ]renew licence (by: Mar 01 2026)\n"),
            ("deadline submit Paper /by 2026-03-01 1800",
             "Added:\n[D][ ]submit Paper (by: Mar 01 2026, 6pm)\n"),
            ("event meeting /from 2026-03-01 /to 2026-03-02",
             "Added:\n[E][ ]meeting (from: 2026-03-01 to: 2026-03-02)\n"),
            ("recurring water plants /every sunday",
             "Added:\n[R][ ]water plants (every: sunday)\n"),
            ("list",
             "1. [T][ ]read paper\n"
             "2. [D][ ]renew licence (by: Mar 01 2026)\n"
             "3. [D][ ]submit Paper (by: Mar 01 2026, 6pm)\n"
             "4. [E][ ]meeting (from: 2026-03-01 to: 2026-03-02)\n"
             "5. [R][ ]water plants (every: sunday)\n"
             "That's 5 on your plate.\n"),
            # Mark, unmark, and note.
            ("mark 1",
             "Done:\n[T][X]read paper\n"),
            ("unmark 1",
             "Not done:\n[T][ ]read paper\n"),
            ("mark 3",
             "Done:\n[D][X]submit Paper (by: Mar 01 2026, 6pm)\n"),
            ("note 2 attach receipts",
             "Noted:\n[D][ ]renew licence (by: Mar 01 2026)\nNote: attach receipts\n"),
            ("list",
             updated_list),
            # Due.
            ("due 2026-03-01",
             "1. [D][ ]renew licence (by: Mar 01 2026)\n"
             "Note: attach receipts\n"
             "2. [D][X]submit Paper (by: Mar 01 2026, 6pm)\n"),
            ("due 2026-03-02",
             "No deadlines due on 2026-03-02.\n"),
            ("list",
             updated_list),
            # Find: ignore case, match partial words, preserve spelling.
            ("find PAP",
             "1. [T][ ]read paper\n"
             "2. [D][X]submit Paper (by: Mar 01 2026, 6pm)\n"),
            ("find APE",
             "1. [T][ ]read paper\n"
             "2. [D][X]submit Paper (by: Mar 01 2026, 6pm)\n"),
            ("find receipts",
             'No tasks found matching "receipts".\n'),
            ("list",
             updated_list),
            # Delete and list.
            ("delete 1",
             "Deleted:\n[T][ ]read paper\n4 tasks left.\n"),
            ("list",
             "1. [D][ ]renew licence (by: Mar 01 2026)\n"
             "Note: attach receipts\n"
             "2. [D][X]submit Paper (by: Mar 01 2026, 6pm)\n"
             "3. [E][ ]meeting (from: 2026-03-01 to: 2026-03-02)\n"
             "4. [R][ ]water plants (every: sunday)\n"
             "That's 3 on your plate.\n"),
            ("bye",
             ""),
        ])

    def test_invalid_inputs(self) -> None:
        """
        Verifies invalid commands report guidance without changing saved tasks.

        Returns:
        --------
        None.
        """
        unknown_command = (
            "Never heard of it. Try: todo, deadline, event, recurring, "
            "list, due, find, mark, unmark, note, delete, bye.\n"
        )
        invalid_deadline = (
            "Invalid deadline. Use a valid date as YYYY-MM-DD, "
            "optionally followed by a time as HHMM (0000–2359).\n"
        )
        steps = [
            # Invalid command arguments.
            ("list extra",
             unknown_command),
            ("bye extra",
             unknown_command),
            ("todo",
             "Use: todo <description>\n"),
            ("deadline submit report",
             "Use: deadline <description> /by YYYY-MM-DD [HHMM]\n"),
            ("event meeting /from monday",
             "Use: event <description> /from <start> /to <end>\n"),
            ("recurring water plants",
             "Use: recurring <description> /every <day>\n"),
            ("mark abc",
             "Use: mark <number>\n"),
            ("unmark abc",
             "Use: unmark <number>\n"),
            ("note 1",
             "Use: note <number> <note>\n"),
            ("delete abc",
             "Use: delete <number>\n"),
            # Invalid dates/times.
            ("deadline submit report /by 2026-02-30",
             invalid_deadline),
            ("deadline submit report /by 2026-03-01 2400",
             invalid_deadline),
            ("due",
             "Use: due YYYY-MM-DD\n"),
            ("due 2026-3-01",
             "Use: due YYYY-MM-DD\n"),
            ("due 2026-03-01 1800",
             "Use: due YYYY-MM-DD\n"),
            ("due 2026-02-30",
             "Invalid date. Use a valid calendar date as YYYY-MM-DD.\n"),
            # Empty searches.
            ("find",
             "Use: find <text>\n"),
            ("find   ",
             "Use: find <text>\n"),
            ("list",
             "That's 0 on your plate.\n"),
            ("bye",
             ""),
        ]
        self._run_session(["bye"])
        path = Path("data/tasks.json")
        original = path.read_text(encoding="utf-8")
        with patch("bao.cli.Tasks._save_tasks") as save:
            self._assert_session(steps)
            save.assert_not_called()
        self.assertEqual(path.read_text(encoding="utf-8"), original)

    def test_saving_and_reloading(self) -> None:
        """
        Verifies tasks retain their details and changes across chat sessions.
        Checks date queries and searches against the reloaded list.

        Returns:
        --------
        None.
        """
        # First-run setup.
        self._run_session(["bye"])
        path = Path("data/tasks.json")
        self.assertEqual(json.loads(path.read_text(encoding="utf-8")), [])

        # Save tasks and updates.
        self._run_session([
            "todo read book",
            "deadline submit report /by 2026-03-02",
            "deadline send slides /by 2026-03-01 2100",
            "event meeting /from monday /to tuesday",
            "recurring water plants /every sunday",
            "todo remove this",
            "mark 1",
            "unmark 1",
            "mark 3",
            "note 2 attach receipts",
            "delete 6",
            "bye",
        ])
        saved = path.read_text(encoding="utf-8")

        # Reload in a new session.
        steps = [
            ("list",
             "1. [T][ ]read book\n"
             "2. [D][ ]submit report (by: Mar 02 2026)\n"
             "Note: attach receipts\n"
             "3. [D][X]send slides (by: Mar 01 2026, 9pm)\n"
             "4. [E][ ]meeting (from: monday to: tuesday)\n"
             "5. [R][ ]water plants (every: sunday)\n"
             "That's 4 on your plate.\n"),
            # Due after reload.
            ("due 2026-03-01",
             "1. [D][X]send slides (by: Mar 01 2026, 9pm)\n"),
            # Find after reload.
            ("find slides",
             "1. [D][X]send slides (by: Mar 01 2026, 9pm)\n"),
            ("bye",
             ""),
        ]
        with patch("bao.cli.Tasks._save_tasks") as save:
            self._assert_session(steps)
            save.assert_not_called()
        self.assertEqual(path.read_text(encoding="utf-8"), saved)


if __name__ == "__main__":
    unittest.main()
