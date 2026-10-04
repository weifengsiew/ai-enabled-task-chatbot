"""Provide optional LLM assistance for Bao's task workspace."""

from __future__ import annotations

import os
from collections.abc import Sequence
from typing import Any, cast

from openai import (
    OpenAI,
    OpenAIError,
)

from bao.tasks import Tasks

LLM_STYLE_VARIABLE = "BAO_LLM_API_STYLE"
LLM_BASE_URL_VARIABLE = "BAO_LLM_BASE_URL"
LLM_API_KEY_VARIABLE = "BAO_LLM_API_KEY"
LLM_MODEL_VARIABLE = "BAO_LLM_MODEL"


def llm_configuration_error() -> str | None:
    """Return a user-facing configuration error, or None when configured."""
    style = os.environ.get(LLM_STYLE_VARIABLE, "openai").casefold()
    if style != "openai":
        return f"Unsupported LLM API style: {style}. Use BAO_LLM_API_STYLE=openai."
    missing = [
        name
        for name in (LLM_BASE_URL_VARIABLE, LLM_API_KEY_VARIABLE, LLM_MODEL_VARIABLE)
        if not os.environ.get(name)
    ]
    if missing:
        return f"Configure these environment variables first: {', '.join(missing)}."
    return None


def _task_context(username: str) -> str:
    tasks = Tasks(username)
    if not len(tasks):
        return "The user has no saved tasks."
    return "\n".join(f"#{task.task_id}: {task}" for task in tasks)


def ask_task_assistant(
    username: str,
    question: str,
    conversation: Sequence[tuple[str, str]] = (),
) -> str:
    """Ask the configured LLM for read-only assistance with the user's tasks."""
    configuration_error = llm_configuration_error()
    if configuration_error is not None:
        return configuration_error

    messages: list[dict[str, str]] = [
        {
            "role": "system",
            "content": (
                "You are Bao's task assistant. Help the user understand and "
                "navigate their tasks. Use only the task context provided. "
                "Do not invent tasks and do not claim to modify, complete, or "
                "delete anything. If the user wants an action, suggest the "
                "exact Bao command they can submit. Put the command alone in "
                "a fenced text code block so it can be copied and pasted. "
                "Use only these command forms: `todo <description> [/on "
                "YYYY-MM-DD]`; `deadline <description> /by YYYY-MM-DD "
                "[HHMM]`; `event <description> /from YYYY-MM-DD HHMM /to "
                "YYYY-MM-DD HHMM`; and `recurring <description> /every "
                "<weekday> at HH:MM`. Use ISO dates (YYYY-MM-DD), four-digit "
                "HHMM times for deadline and event commands, and `/by`—not "
                "`/due`—when creating a deadline. "
                "Keep answers concise.\n\n"
                f"Current task context:\n{_task_context(username)}"
            ),
        }
    ]
    messages.extend(
        {"role": role, "content": content} for role, content in conversation[-8:]
    )
    messages.append({"role": "user", "content": question})

    try:
        client = OpenAI(
            api_key=os.environ[LLM_API_KEY_VARIABLE],
            base_url=os.environ[LLM_BASE_URL_VARIABLE],
            max_retries=0,
            timeout=30.0,
        )
        response = client.chat.completions.create(
            model=os.environ[LLM_MODEL_VARIABLE],
            messages=cast(Any, messages),
        )
    except (OpenAIError, ValueError) as error:
        return f"The task assistant request failed ({type(error).__name__})."

    return (
        response.choices[0].message.content or "The task assistant returned no answer."
    )
