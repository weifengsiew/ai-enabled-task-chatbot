import builtins
import json

import pytest

from inherited import bao


@pytest.fixture(autouse=True)
def isolated_data_file(tmp_path, monkeypatch):
    monkeypatch.setattr(bao, "DATA_FILE", tmp_path / "data" / "tasks.json")
    bao.TASKS.clear()


def run_session(monkeypatch, capsys, *commands):
    entries = iter(commands)
    monkeypatch.setattr(builtins, "input", lambda _prompt="": next(entries))
    bao.run()
    return capsys.readouterr().out


def test_empty_list_and_blank_input_keep_the_conversation_running(monkeypatch, capsys):
    output = run_session(monkeypatch, capsys, "", "list", "bye")

    assert "Nothing there." in output
    assert "Nothing on your plate." in output
    assert output.endswith("Later.\n")


def test_adds_and_lists_every_task_kind(monkeypatch, capsys):
    output = run_session(
        monkeypatch,
        capsys,
        "todo read the paper",
        "deadline submit the abstract /by 2026-03-01 1800",
        "event lab retreat /from monday /to wednesday",
        "recurring wash the mugs /every monday",
        "list",
        "bye",
    )

    assert "1.[T][ ] read the paper" in output
    assert "2.[D][ ] submit the abstract (by: Mar 01 2026, 6pm)" in output
    assert "3.[E][ ] lab retreat (from: monday to: wednesday)" in output
    assert "4.[R][ ] wash the mugs (every: monday)" in output


def test_changes_state_and_attaches_a_note(monkeypatch, capsys):
    output = run_session(
        monkeypatch,
        capsys,
        "todo read the paper",
        "mark 1",
        "note 1 ask about funding",
        "list",
        "unmark 1",
        "bye",
    )

    assert "1.[T][X] read the paper" in output
    assert "Note: ask about funding" in output
    assert "Not done:\n  [ ] read the paper" in output


def test_deletes_and_clears_tasks(monkeypatch, capsys):
    output = run_session(
        monkeypatch,
        capsys,
        "todo first",
        "todo second",
        "todo third",
        "mark 2",
        "clear",
        "delete 1",
        "list",
        "bye",
    )

    assert "Cleared 1 completed tasks." in output
    assert "Deleted:\n  first" in output
    assert "1.[T][ ] third" in output


def test_finds_partial_text_without_caring_about_case(monkeypatch, capsys):
    output = run_session(
        monkeypatch,
        capsys,
        "todo read the Paper",
        "todo buy fruit",
        "find PAP",
        "bye",
    )

    assert "1.[ ] read the Paper" in output
    assert "buy fruit" in output
    assert "2.[ ] buy fruit" not in output


def test_lists_deadlines_due_on_one_day(monkeypatch, capsys):
    output = run_session(
        monkeypatch,
        capsys,
        "deadline morning task /by 2026-03-01 0900",
        "deadline later task /by 2026-03-02",
        "due 2026-03-01",
        "bye",
    )

    assert "1.[D][ ] morning task (by: Mar 01 2026, 9am)" in output
    assert "later task" in output
    assert "2.[D][ ] later task" not in output


def test_saves_changes_and_loads_them_on_the_next_run(monkeypatch, capsys):
    run_session(monkeypatch, capsys, "todo survive restart", "bye")
    bao.TASKS.clear()

    output = run_session(monkeypatch, capsys, "list", "bye")

    assert "1.[T][ ] survive restart" in output
    saved = json.loads(bao.DATA_FILE.read_text())
    assert saved[0]["description"] == "survive restart"


@pytest.mark.parametrize(
    ("command", "message"),
    [
        ("mark", "Tell me which task to mark"),
        ("mark abc", "whole number"),
        ("mark 99", "No task 99"),
        ("deadline soon", "needs something to do and a /by"),
        ("due someday", "Use due YYYY-MM-DD"),
        ("find", "Tell me what to find"),
    ],
)
def test_bad_input_reports_an_error_and_keeps_running(
    monkeypatch, capsys, command, message
):
    output = run_session(monkeypatch, capsys, command, "list", "bye")

    assert message in output
    assert "Nothing on your plate." in output
    assert output.endswith("Later.\n")
