"""End-to-end command sessions for Bao's chat loop."""

import io
import json
import unittest
from contextlib import chdir, redirect_stdout
from collections.abc import Iterator
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
        # Keep test data separate from the user's saved tasks.
        self.enterContext(chdir(directory))

    def _run_session(
        self,
        commands: list[str],
        expected_saved: list[list[dict[str, str | bool | None]]] | None = None,
    ) -> str:
        """
        Runs chat with supplied commands and captures its printed output.
        Verifies that every command is requested and chat returns normally.

        Args:
        -----
        commands (list[str]): The input sequence, ending with "bye".
        expected_saved (list | None): Expected saved records before each input,
            or None to skip intermediate file checks.

        Returns:
        --------
        str: The complete printed output, excluding mocked input prompts.
        """
        def inputs() -> Iterator[str]:
            """
            Checks saved data before yielding each simulated input.

            Returns:
            --------
            Iterator[str]: The session's commands in order.
            """
            for index, command in enumerate(commands):
                if expected_saved is not None:
                    # The previous command must be saved before the next input.
                    saved = json.loads(
                        Path("data/tasks.json").read_text(encoding="utf-8")
                    )
                    self.assertEqual(saved, expected_saved[index])
                yield command

        if expected_saved is not None:
            self.assertEqual(len(expected_saved), len(commands))
        output = io.StringIO()
        with patch("builtins.input", side_effect=inputs()) as mock_input:
            with redirect_stdout(output):
                result = chat()

        self.assertIsNone(result)
        self.assertEqual(mock_input.call_args_list, [call("> ")] * len(commands))
        return output.getvalue()

    def test_valid_inputs(self) -> None:
        """
        Verifies task creation, updates, deletion, and listing with two tasks.
        Checks each change is saved before the next input and survives restart.

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
            "1 tasks left.\n"
            "1. [D][ ]submit report (by: friday)\n"
            "Note: attach receipts\n"
            "That's 1 on your plate.\n"
        )

        todo = {
            "description": "read book", "task_type": "todo", "done": False,
            "note": None, "day": None, "start": None, "end": None,
        }
        deadline = {
            "description": "submit report", "task_type": "deadline", "done": False,
            "note": None, "day": "friday", "start": None, "end": None,
        }
        noted_deadline = {**deadline, "note": "attach receipts"}
        # Expected file contents before each command, including first-run setup.
        expected_saved = [
            [],
            [todo],
            [todo, deadline],
            [todo, {**deadline, "done": True}],
            [todo, deadline],
            [todo, noted_deadline],
            [noted_deadline],
            [noted_deadline],
        ]
        self.assertEqual(self._run_session(commands, expected_saved), expected)
        # A fresh session must reload the remaining task and its note from disk.
        self.assertEqual(
            self._run_session(["list", "bye"]),
            "1. [D][ ]submit report (by: friday)\n"
            "Note: attach receipts\n"
            "That's 1 on your plate.\n",
        )

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

        # First run must create an empty save file without manual setup.
        self._run_session(["bye"])
        path = Path("data/tasks.json")
        original = path.read_text(encoding="utf-8")
        self.assertEqual(json.loads(original), [])
        # Invalid commands must neither trigger a save nor alter the file.
        with patch("bao.cli.Tasks._save_tasks") as save:
            self.assertEqual(self._run_session(commands), expected)
            save.assert_not_called()
        self.assertEqual(path.read_text(encoding="utf-8"), original)



if __name__ == "__main__":
    unittest.main()
