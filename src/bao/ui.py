"""Provide Bao's local Gradio user interface."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import gradio as gr

from .read_task_commands import Command
from .tasks import Tasks

Message = dict[str, str]


def submit_command(
    user_response: str, history: Sequence[Message] | None
) -> tuple[str, list[Message]]:
    """Execute one Bao command and append the exchange to the chat history."""
    messages = list(history or [])
    matched_command = Command.parse_user_response_with_command_pattern(user_response)

    if isinstance(matched_command, str):
        response = matched_command
    elif matched_command is None:
        response = ""
    else:
        response = matched_command.execute_command(Tasks())

    messages.extend(
        [
            {"role": "user", "content": user_response},
            {"role": "assistant", "content": response},
        ]
    )
    return "", messages


def clear_conversation() -> tuple[list[Message], str]:
    """Return empty values for the chat and command input."""
    return [], ""


def create_app() -> Any:
    """Build and return Bao's local Gradio application."""
    with gr.Blocks(title="Bao") as app:
        chatbot = gr.Chatbot(label="Conversation")
        command_input = gr.Textbox(
            label="Command",
            placeholder="Try: todo buy groceries",
        )
        with gr.Row():
            submit = gr.Button("Submit", variant="primary")
            clear = gr.Button("Clear")

        submit_events = [command_input, chatbot]
        submit.click(
            submit_command,
            inputs=[command_input, chatbot],
            outputs=submit_events,
        )
        command_input.submit(
            submit_command,
            inputs=[command_input, chatbot],
            outputs=submit_events,
        )
        clear.click(
            clear_conversation,
            outputs=[chatbot, command_input],
        )
    return app


def main() -> None:
    """Launch Bao's local web interface."""
    create_app().launch(server_name="127.0.0.1")


if __name__ == "__main__":
    main()
