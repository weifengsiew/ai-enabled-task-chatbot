"""Pytest end-to-end command sessions for Bao's chat loop."""

import json
from pathlib import Path
from unittest.mock import call, patch

import pytest

from bao.cli import chat


@pytest.fixture(autouse=True)
def isolated_data_directory(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Use monkeypatch to isolate saved data in tmp_path until test cleanup."""
    monkeypatch.chdir(tmp_path)


def _run_session(capsys: pytest.CaptureFixture[str], commands: list[str]) -> str:
    """Run commands followed by bye; return captured output and allow task storage."""
    commands = [*commands, "bye"]
    with patch("builtins.input", side_effect=commands) as mock_input:
        result = chat()

    assert result is None
    assert mock_input.call_args_list == [call("> ")] * len(commands)
    return capsys.readouterr().out


def _assert_session(
    capsys: pytest.CaptureFixture[str], steps: list[tuple[str, str]]
) -> None:
    """Run command/output pairs with capsys and assert exact output; may save tasks."""
    commands = [command for command, _ in steps]
    expected = "".join(output for _, output in steps)
    assert _run_session(capsys, commands) == expected


def test_adding_and_listing(capsys: pytest.CaptureFixture[str]) -> None:
    """Verify adding and listing each task kind."""
    _assert_session(
        capsys,
        [
            # adding todo
            ("todo read paper", "Added:\n[T][ ]read paper\n"),
            # adding deadline with date only
            (
                "deadline renew licence /by 2026-03-01",
                "Added:\n[D][ ]renew licence (by: Mar 01 2026)\n",
            ),
            # adding deadline with date and time
            (
                "deadline submit Paper /by 2026-03-01 1800",
                "Added:\n[D][ ]submit Paper (by: Mar 01 2026, 6pm)\n",
            ),
            # adding event
            (
                "event meeting /from 2026-03-01 /to 2026-03-02",
                "Added:\n[E][ ]meeting (from: 2026-03-01 to: 2026-03-02)\n",
            ),
            # adding recurring
            (
                "recurring water plants /every sunday",
                "Added:\n[R][ ]water plants (every: sunday)\n",
            ),
            # listing
            (
                "list",
                (
                    "1. [T][ ]read paper\n"
                    "2. [D][ ]renew licence (by: Mar 01 2026)\n"
                    "3. [D][ ]submit Paper (by: Mar 01 2026, 6pm)\n"
                    "4. [E][ ]meeting (from: 2026-03-01 to: 2026-03-02)\n"
                    "5. [R][ ]water plants (every: sunday)\n"
                    "That's 5 on your plate.\n"
                ),
            ),
        ],
    )


def test_marking_unmarking_noting_and_deleting(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Verify marking, unmarking, noting, and deleting."""
    updated_list = (
        "1. [T][ ]read paper\n"
        "2. [D][ ]renew licence (by: Mar 01 2026)\n"
        "Note: attach receipts\n"
        "3. [D][X]submit Paper (by: Mar 01 2026, 6pm)\n"
        "That's 2 on your plate.\n"
    )
    # setup tasks
    _run_session(
        capsys,
        [
            "todo read paper",
            "deadline renew licence /by 2026-03-01",
            "deadline submit Paper /by 2026-03-01 1800",
        ],
    )

    _assert_session(
        capsys,
        [
            # marking
            ("mark 1", "Done:\n[T][X]read paper\n"),
            # unmarking
            ("unmark 1", "Not done:\n[T][ ]read paper\n"),
            # marking
            ("mark 3", "Done:\n[D][X]submit Paper (by: Mar 01 2026, 6pm)\n"),
            # noting
            (
                "note 2 attach receipts",
                "Noted:\n[D][ ]renew licence (by: Mar 01 2026)\nNote: attach receipts\n",
            ),
            # completion and note changes
            ("list", updated_list),
            # deleting
            ("delete 1", "Deleted:\n[T][ ]read paper\n2 tasks left.\n"),
            # deletion and renumbering
            (
                "list",
                (
                    "1. [D][ ]renew licence (by: Mar 01 2026)\n"
                    "Note: attach receipts\n"
                    "2. [D][X]submit Paper (by: Mar 01 2026, 6pm)\n"
                    "That's 1 on your plate.\n"
                ),
            ),
        ],
    )


def test_invalid_inputs(capsys: pytest.CaptureFixture[str]) -> None:
    """Verify missing, malformed, and out-of-range input.

    Includes invalid dates and out-of-range times.
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
        # missing input
        ("todo", "Use: todo <description>\n"),
        # missing input
        (
            "deadline submit report",
            "Use: deadline <description> /by YYYY-MM-DD [HHMM]\n",
        ),
        # missing input
        (
            "event meeting /from monday",
            "Use: event <description> /from <start> /to <end>\n",
        ),
        # missing input
        ("recurring water plants", "Use: recurring <description> /every <day>\n"),
        # missing input
        ("note 1", "Use: note <number> <note>\n"),
        # missing input
        ("due", "Use: due YYYY-MM-DD\n"),
        # missing input
        ("find", "Use: find <text>\n"),
        # missing input
        ("find   ", "Use: find <text>\n"),
        # malformed input
        ("list extra", unknown_command),
        # malformed input
        ("bye extra", unknown_command),
        # malformed input
        ("mark abc", "Use: mark <number>\n"),
        # malformed input
        ("unmark abc", "Use: unmark <number>\n"),
        # malformed input
        ("delete abc", "Use: delete <number>\n"),
        # malformed input
        ("due 2026-3-01", "Use: due YYYY-MM-DD\n"),
        # malformed input
        ("due 2026-03-01 1800", "Use: due YYYY-MM-DD\n"),
        # invalid dates
        ("deadline submit report /by 2026-02-30", invalid_deadline),
        # invalid dates
        ("due 2026-02-30", "Invalid date. Use a valid calendar date as YYYY-MM-DD.\n"),
        # out-of-range times
        ("deadline submit report /by 2026-03-01 2400", invalid_deadline),
        # unchanged after invalid input
        ("list", "That's 0 on your plate.\n"),
    ]
    # setup saved file
    _run_session(capsys, [])
    path = Path("data/tasks.json")
    original = path.read_text(encoding="utf-8")
    with patch("bao.cli.Tasks._save_tasks") as save:
        _assert_session(capsys, steps)
        save.assert_not_called()
    assert path.read_text(encoding="utf-8") == original


def test_saving_and_loading(capsys: pytest.CaptureFixture[str]) -> None:
    """Verify saving and loading, including a missing data folder."""
    # missing data folder
    _run_session(capsys, [])
    path = Path("data/tasks.json")
    assert json.loads(path.read_text(encoding="utf-8")) == []

    # saving tasks and changes
    _run_session(
        capsys,
        [
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
        ],
    )
    saved = path.read_text(encoding="utf-8")

    steps = [
        # loading saved tasks
        (
            "list",
            (
                "1. [T][ ]read book\n"
                "2. [D][ ]submit report (by: Mar 02 2026)\n"
                "Note: attach receipts\n"
                "3. [D][X]send slides (by: Mar 01 2026, 9pm)\n"
                "4. [E][ ]meeting (from: monday to: tuesday)\n"
                "5. [R][ ]water plants (every: sunday)\n"
                "That's 4 on your plate.\n"
            ),
        ),
        # `due` after loading
        ("due 2026-03-01", "1. [D][X]send slides (by: Mar 01 2026, 9pm)\n"),
        # `find` after loading
        ("find slides", "1. [D][X]send slides (by: Mar 01 2026, 9pm)\n"),
    ]
    with patch("bao.cli.Tasks._save_tasks") as save:
        # loading
        _assert_session(capsys, steps)
        save.assert_not_called()
    assert path.read_text(encoding="utf-8") == saved


def test_deadline_parsing_and_due(capsys: pytest.CaptureFixture[str]) -> None:
    """Verify deadline parsing and `due`."""
    updated_list = (
        "1. [T][ ]read paper\n"
        "2. [D][ ]renew licence (by: Mar 01 2026)\n"
        "Note: attach receipts\n"
        "3. [D][X]submit Paper (by: Mar 01 2026, 6pm)\n"
        "That's 2 on your plate.\n"
    )
    # setup tasks
    _run_session(
        capsys,
        [
            "todo read paper",
            "deadline renew licence /by 2026-03-01",
            "deadline submit Paper /by 2026-03-01 1800",
            "mark 3",
            "note 2 attach receipts",
        ],
    )

    _assert_session(
        capsys,
        [
            # `due` matches
            (
                "due 2026-03-01",
                (
                    "1. [D][ ]renew licence (by: Mar 01 2026)\n"
                    "Note: attach receipts\n"
                    "2. [D][X]submit Paper (by: Mar 01 2026, 6pm)\n"
                ),
            ),
            # `due` without matches
            ("due 2026-03-02", "No deadlines due on 2026-03-02.\n"),
            # unchanged after `due`
            ("list", updated_list),
        ],
    )


def test_find(capsys: pytest.CaptureFixture[str]) -> None:
    """Verify case-insensitive partial matching with `find`."""
    matches = "1. [T][ ]read paper\n2. [D][X]submit Paper (by: Mar 01 2026, 6pm)\n"
    updated_list = (
        "1. [T][ ]read paper\n"
        "2. [D][ ]renew licence (by: Mar 01 2026)\n"
        "Note: attach receipts\n"
        "3. [D][X]submit Paper (by: Mar 01 2026, 6pm)\n"
        "That's 2 on your plate.\n"
    )
    # setup tasks
    _run_session(
        capsys,
        [
            "todo read paper",
            "deadline renew licence /by 2026-03-01",
            "deadline submit Paper /by 2026-03-01 1800",
            "mark 3",
            "note 2 attach receipts",
        ],
    )

    _assert_session(
        capsys,
        [
            # case-insensitive partial matching with `find`
            ("find PAP", matches),
            # case-insensitive partial matching with `find`
            ("find APE", matches),
            # `find` excludes notes
            ("find receipts", 'No tasks found matching "receipts".\n'),
            # unchanged after `find`
            ("list", updated_list),
        ],
    )
