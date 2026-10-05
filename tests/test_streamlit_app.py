"""Tests for Bao's Streamlit application helpers."""

from datetime import time
from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast

import pytest

from bao import llm
from bao.streamlit_app import (
    CAT_ASSET_DIRECTORY,
    CAT_ASSETS,
    CAT_THEME_CSS,
    _authenticate,
    _recurrence_rule,
    _run_command,
    _task_matches,
    _valid_username,
)
from bao.tasks import Tasks
from bao.users import account_file, create_account


@pytest.fixture(autouse=True)
def isolated_data_directory(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Isolate persisted accounts and tasks for each test."""
    monkeypatch.chdir(tmp_path)


def test_configured_user_authentication(monkeypatch: pytest.MonkeyPatch) -> None:
    """Configured users can authenticate through the Streamlit UI."""
    monkeypatch.setenv("BAO_USERS", "alice:secret")

    assert _authenticate("alice", "secret") is True
    assert _authenticate("alice", "wrong") is False


def test_signup_account_authentication() -> None:
    """Streamlit uses the shared account store for signup-created users."""
    create_account("alice", "secret123")

    assert account_file().exists()
    assert _authenticate("alice", "secret123") is True


@pytest.mark.parametrize("username", ["ab", "has space", "has.dot", ""])
def test_invalid_usernames_are_rejected(username: str) -> None:
    """Signup usernames follow the documented format."""
    assert _valid_username(username) is False


def test_valid_username_is_accepted() -> None:
    """Signup accepts documented usernames."""
    assert _valid_username("bao-user_1") is True


def test_cat_theme_defines_shared_light_and_dark_palette() -> None:
    """The Streamlit theme includes the approved palette and dark-mode support."""
    assert "--bao-ginger: #d97745" in CAT_THEME_CSS
    assert "--bao-sage: #7b9a82" in CAT_THEME_CSS
    assert "prefers-color-scheme: dark" in CAT_THEME_CSS


def test_cat_theme_has_an_illustration_for_each_workflow_and_task_type() -> None:
    """Every themed workflow maps to a local cat illustration asset."""
    assert set(CAT_ASSETS) == {
        "chat",
        "create",
        "search",
        "deadline",
        "recurring",
        "todo",
        "event",
        "close",
    }
    assert all((CAT_ASSET_DIRECTORY / asset).exists() for asset in CAT_ASSETS.values())


def test_streamlit_command_execution_is_user_scoped() -> None:
    """Commands use the authenticated user's task store."""
    response = _run_command("alice", "todo buy groceries")

    assert response.startswith("Added:")
    assert len(Tasks("alice")) == 1
    assert len(Tasks("bob")) == 0


def test_task_search_matches_supported_attributes() -> None:
    """Search matching supports task text and task metadata."""
    _run_command("alice", "todo buy groceries")
    task = next(iter(Tasks("alice")))

    assert _task_matches(task, "groceries", "description")
    assert _task_matches(task, "todo", "type")
    assert not _task_matches(task, "deadline", "type")


def test_todo_date_is_parsed_and_persisted() -> None:
    """Todo creation stores and displays its selected date."""
    response = _run_command("alice", "todo submit report /on 2026-10-10")

    assert "(on: Oct 10 2026)" in response
    task = next(iter(Tasks("alice")))
    task_fields = cast(Any, task)
    loaded_fields = cast(Any, next(iter(Tasks("alice"))))
    assert task_fields.due_date.isoformat() == "2026-10-10"
    assert loaded_fields.due_date == task_fields.due_date


def test_deadline_due_alias_is_accepted() -> None:
    """Copied AI suggestions using /due remain executable."""
    response = _run_command("alice", "deadline biology assignment /due 2026-01-25")

    assert response.startswith("Added:")
    assert "Jan 25 2026" in response


def test_streamlit_recurrence_rule_uses_selected_day_and_time() -> None:
    """Recurring creation stores the selected weekday and time."""
    rule = _recurrence_rule("Wednesday", time(21, 0))
    response = _run_command("alice", f"recurring exercise /every {rule}")

    assert "every: Wednesday at 21:00" in response
    task = next(iter(Tasks("alice")))
    assert cast(Any, task).recurrence_rule == "Wednesday at 21:00"


def test_llm_reports_missing_configuration(monkeypatch: pytest.MonkeyPatch) -> None:
    """AI assistance explains how to configure the endpoint."""
    monkeypatch.delenv("BAO_LLM_BASE_URL", raising=False)
    monkeypatch.delenv("BAO_LLM_API_KEY", raising=False)
    monkeypatch.delenv("BAO_LLM_MODEL", raising=False)

    response = llm.ask_task_assistant("alice", "What should I do next?")

    assert "BAO_LLM_BASE_URL" in response


def test_llm_uses_user_tasks_and_configured_openai_endpoint(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """AI assistance sends only the authenticated user's task context."""
    monkeypatch.setenv("BAO_LLM_BASE_URL", "https://example.test/v1")
    monkeypatch.setenv("BAO_LLM_API_KEY", "test-key")
    monkeypatch.setenv("BAO_LLM_MODEL", "FW-DeepSeek-V4.1-Flash")
    captured: dict[str, Any] = {}

    class FakeCompletions:
        def create(self, **kwargs: Any) -> Any:
            captured.update(kwargs)
            return SimpleNamespace(
                choices=[
                    SimpleNamespace(
                        message=SimpleNamespace(content="Try the deadline first.")
                    )
                ]
            )

    class FakeClient:
        def __init__(self, **kwargs: Any) -> None:
            captured.update(kwargs)
            self.chat = SimpleNamespace(completions=FakeCompletions())

    monkeypatch.setattr(llm, "OpenAI", FakeClient)
    _run_command("alice", "todo buy groceries")

    response = llm.ask_task_assistant("alice", "What is on my list?")

    assert response == "Try the deadline first."
    assert captured["base_url"] == "https://example.test/v1"
    assert captured["model"] == "FW-DeepSeek-V4.1-Flash"
    system_message = captured["messages"][0]["content"]
    assert "buy groceries" in system_message
    assert "alice" not in system_message
