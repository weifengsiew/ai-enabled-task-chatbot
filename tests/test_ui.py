"""Tests for Bao's local Gradio interface handlers."""

from pathlib import Path

import pytest

from bao.ui import clear_conversation, submit_command


@pytest.fixture(autouse=True)
def isolated_data_directory(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Isolate persisted tasks for each UI test."""
    monkeypatch.chdir(tmp_path)


def test_submit_command_adds_bao_exchange() -> None:
    """A valid command appears with Bao's response in the conversation."""
    input_value, history = submit_command("todo buy groceries", None)

    assert input_value == ""
    assert history == [
        {"role": "user", "content": "todo buy groceries"},
        {"role": "assistant", "content": "Added:\n[T][ ]buy groceries"},
    ]


def test_submit_command_reuses_saved_tasks() -> None:
    """A later list command sees tasks created by an earlier submission."""
    _, history = submit_command("todo buy groceries", None)
    _, history = submit_command("list", history)

    assert history[-1] == {
        "role": "assistant",
        "content": "1. [T][ ]buy groceries\nThat's 1 on your plate.",
    }


def test_clear_conversation_removes_messages() -> None:
    """Clear returns an empty conversation and input value."""
    assert clear_conversation() == ([], "")
