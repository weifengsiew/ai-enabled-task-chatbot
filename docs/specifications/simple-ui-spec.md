# Add a Simple Local Gradio UI for Bao

## Status

Implemented

## User story

As a Bao user, I want to enter commands and see Bao's responses in a browser,
so that I can use Bao through a simple graphical interface instead of only
through the terminal.

## Acceptance examples

### Example 1: Submit a command

- Given the local Gradio UI is running
- When the user enters `todo buy groceries` and submits it
- Then the chat panel shows the user's command and Bao's response

### Example 2: View saved tasks

- Given the user has added a task
- When the user enters `list` and submits it
- Then the chat panel shows Bao's list response

### Example 3: Clear the conversation

- Given the chat panel contains commands and responses
- When the user selects Clear
- Then the displayed conversation is removed

### Example 4: Run locally

- Given the project dependencies are installed
- When the user runs `uv run python -m bao.ui`
- Then the UI is available at `http://127.0.0.1:7860`

## Tests covered

- `tests/test_ui.py` verifies command submission, saved-task responses, and
  conversation clearing.

## Changes made

The implementation:

- Adds a new `src/bao/ui.py` module using Gradio.
- Adds Gradio as a project dependency in `pyproject.toml` and updates `uv.lock`.
- Leaves the existing CLI and command modules unchanged.
- Reuses the existing `Command` and `Tasks` classes rather than duplicating
  command definitions.

## Code locations

The implementation changes are in:

- `src/bao/ui.py` — Gradio interface and message submission handling.
- `tests/test_ui.py` — UI handler tests.
- `pyproject.toml` — Gradio dependency.
- `uv.lock` — Locked dependency update.

## CI check results

- Pytest: [x] `uv run pytest` — 11 passed.
- Ruff lint: [x] `uv run ruff check src tests` — passed.
- Ruff format: [x] `uv run ruff format --check .` — passed.
- Mypy: [x] `uv run mypy src tests` — passed.
- Shared CI pipeline: [ ] Not run locally.

## Local UI details

The first version should contain:

- A chat panel showing the user's commands and Bao's responses.
- A text input for entering commands.
- A Submit action to send a command.
- A Clear action to clear the displayed conversation.

The first version is intended for single-user local use and should not expose
the application publicly. Future enhancements may include custom styling,
task-management buttons, multi-user session handling, network access, and
deployment to a hosted environment.
