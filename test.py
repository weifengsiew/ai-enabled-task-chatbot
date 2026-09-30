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
        Verifies task operations, deadline formatting, and date-based queries.
        Checks each change is saved before the next input and survives restart.

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

        todo = {
            "description": "read book", "task_type": "todo", "done": False,
            "note": None, "day": None, "start": None, "end": None,
            "due_date": None, "due_time": None,
        }
        deadline = {
            **todo, "description": "submit report", "task_type": "deadline",
            "due_date": "2026-03-02",
        }
        abstract = {
            **deadline, "description": "submit abstract",
            "due_date": "2026-03-01", "due_time": "18:00:00",
        }
        noted_deadline = {**deadline, "note": "attach receipts"}
        slides = {**abstract, "description": "send slides", "due_time": "21:00:00"}
        done_slides = {**slides, "done": True}
        licence = {
            **deadline, "description": "renew licence", "due_date": "2026-03-01",
        }
        another_todo = {**todo, "description": "read another book"}
        event = {
            **todo, "description": "meeting", "task_type": "event",
            "start": "2026-03-01", "end": "2026-03-02",
        }
        recurring = {
            **todo, "description": "water plants", "task_type": "recurring",
            "day": "sunday",
        }
        remaining = [noted_deadline, abstract, done_slides, licence]
        all_saved = [*remaining, another_todo, event, recurring]
        # Expected file contents before each command, including first-run setup.
        expected_saved = [
            [],                                                   # todo read book
            [todo],                                               # deadline report
            [todo, deadline],                                     # deadline abstract
            [todo, deadline, abstract],                           # mark 2
            [todo, {**deadline, "done": True}, abstract],           # unmark 2
            [todo, deadline, abstract],                           # note 2
            [todo, noted_deadline, abstract],                      # delete 1
            [noted_deadline, abstract],                            # list
            [noted_deadline, abstract],                            # deadline slides
            [noted_deadline, abstract, slides],                    # mark 3
            [noted_deadline, abstract, done_slides],                # deadline licence
            remaining,                                            # todo another book
            [*remaining, another_todo],                            # event meeting
            [*remaining, another_todo, event],                     # recurring plants
            all_saved,                                            # due March 1
            all_saved,                                            # due March 3
            all_saved,                                            # bye
        ]
        self.assertEqual(self._run_session(commands, expected_saved), expected)

        # A fresh session must preserve timing, notes, status, and query results.
        restart_steps = [
            (
                "list",
                "1. [D][ ]submit report (by: Mar 02 2026)\n"
                "Note: attach receipts\n"
                "2. [D][ ]submit abstract (by: Mar 01 2026, 6pm)\n"
                "3. [D][X]send slides (by: Mar 01 2026, 9pm)\n"
                "4. [D][ ]renew licence (by: Mar 01 2026)\n"
                "5. [T][ ]read another book\n"
                "6. [E][ ]meeting (from: 2026-03-01 to: 2026-03-02)\n"
                "7. [R][ ]water plants (every: sunday)\n"
                "That's 6 on your plate.\n",
            ),
            (
                "due 2026-03-01",
                "1. [D][ ]submit abstract (by: Mar 01 2026, 6pm)\n"
                "2. [D][X]send slides (by: Mar 01 2026, 9pm)\n"
                "3. [D][ ]renew licence (by: Mar 01 2026)\n",
            ),
            ("bye", ""),
        ]
        restart_commands = [command for command, _ in restart_steps]
        restart_expected = "".join(output for _, output in restart_steps)
        self.assertEqual(
            self._run_session(restart_commands, [all_saved] * len(restart_steps)),
            restart_expected,
        )

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
