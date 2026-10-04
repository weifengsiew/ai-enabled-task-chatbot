# Bao Streamlit Application Specification

## Scope

This document consolidates the specifications used to build Bao's local
Streamlit web application. It supersedes the earlier UI implementation
details while preserving Bao's existing command behavior, task persistence,
CLI behavior, and local-only runtime model.

The application is intended for single-user browser sessions on a local
machine. It must not be exposed publicly in its first version.

## Product goals

The Streamlit application must allow a Bao user to:

1. Sign in or create a Bao account.
2. See and manage only their own tasks.
3. Enter existing Bao commands and view the responses.
4. Create, filter, search, update, complete, and delete tasks through guided
   controls.
5. Clear the displayed conversation without deleting stored tasks.
6. Stop the local Bao server safely from the authenticated interface.

## Runtime and entry points

The preferred startup command is:

```bash
uv run streamlit run src/bao/streamlit_app.py \
  --server.address 127.0.0.1 \
  --server.port 7860
```

The application must:

- Listen on `127.0.0.1` by default.
- Use port `7860` by default.
- Support an alternate port when `7860` is occupied.
- Remain local-only unless a future specification explicitly adds network
  access.
- Avoid scanning for or occupying unrelated ports.
- Keep `uv run python -m bao.ui` as a compatibility launcher for Streamlit.

## Authentication and accounts

### Sign-in

The application must provide a sign-in view containing:

- Username input.
- Password input.
- Sign-in action.
- Link or action to open sign-up.

The sign-in password is visible while typing by default so the user can verify
it. The field must remain keyboard-accessible and have an appropriate
accessible label.

Valid credentials grant access to the task workspace. Invalid credentials are
rejected without revealing task data.

Configured users remain supported through the `BAO_USERS` environment
variable, using comma-separated `username:password` pairs.

Authentication requirements:

- The authenticated username must come from server-side Streamlit session
  state.
- Task operations must not trust a username submitted in a form.
- Unauthenticated users must not see or modify task data.
- Passwords must not appear in conversation history, logs, errors, or other
  user-visible output.

### Sign-up

The sign-up view must contain:

- Username input.
- Password input.
- Password confirmation input.
- Create-account action.
- Return-to-sign-in action.

Sign-up password fields remain masked while typing.

Validation rules:

- Username length must be 3–32 characters.
- Username characters may be letters, numbers, underscores, or hyphens.
- Password length must be at least 8 characters.
- Password confirmation must match the password.
- Duplicate usernames must be rejected.
- Invalid input must show a clear validation message without creating an
  account.

Successful sign-up must:

- Store only a secure one-way salted password hash.
- Never persist or display the plaintext password.
- Sign the new user in automatically.
- Preserve per-user task isolation.

## Workspace layout

After authentication, the user must see a task workspace containing:

- A left-side navigation area.
- A right-side area for the selected workflow.
- A conversation panel showing user commands and Bao responses.
- A `Command` input.
- `Submit` and `Clear` controls immediately below the Command input.
- A `Close Bao` control.

The navigation must expose these workflows:

- `🐱💬 Chat about task`
- `✎ Create task`
- `👁️ View task`
- `🔍 Search and update task`
- `🤖 Enable LLM`

The `Enable LLM` workflow is separate from task chat. It shows whether the
configured OpenAI-compatible endpoint is available, displays the endpoint and
model without exposing the API key, and lets the user enable or disable the
`Ask Bao AI` control in `Chat about task`. AI assistance remains read-only and
does not directly modify tasks.

The View task workflow must support the task types `todo`, `deadline`,
`event`, and `recurring`.

Only the selected workflow should be active or visible at a time. Opening one
workflow must hide or deactivate the others. The layout must remain usable on
smaller screens.

## Command conversation

The application must preserve existing command behavior.

Supported direct commands include, but are not limited to:

- `todo buy groceries`
- `deadline submit report /by 2026-10-10 1700`
- `event meeting /from 2026-10-10 0900 /to 2026-10-10 1000`
- `recurring exercise /every monday`
- `list`
- `mark <number>`
- `unmark <number>`
- `note <number> <note>`
- `delete <number>`
- `find <text>`
- `filter <type>`

When a command is submitted:

- The user's command is added to the conversation panel.
- Bao's existing response is added after it.
- The command operates on the authenticated user's task store.

`Clear` must remove only the displayed conversation and Command input. It must
not delete or alter persisted tasks.

### LLM task assistance

The Chat about task workflow must provide an optional `Ask Bao AI` action for
natural-language task assistance. It must use these environment variables:

- `BAO_LLM_API_STYLE`, currently `openai`.
- `BAO_LLM_BASE_URL`, the OpenAI-compatible LiteLLM endpoint.
- `BAO_LLM_API_KEY`, kept server-side and never shown in the browser.
- `BAO_LLM_MODEL`, such as `FW-DeepSeek-V4.1-Flash`.

When Ask Bao AI is selected:

- Send only the authenticated user's task context and relevant conversation
  history to the configured endpoint.
- Preserve direct Bao commands through the deterministic command handlers.
- Keep the assistant read-only in the first version.
- Allow the assistant to suggest exact Bao commands for requested actions, but
  do not let it directly create, update, complete, or delete tasks.
- Show a clear configuration or connection error without exposing the API key.

## Task filters

The View task workflow must provide filters for:

- `todo`
- `deadline`
- `event`
- `recurring`

Selecting a filter must:

- Show only the authenticated user's matching tasks.
- Read fresh data from the current task store.
- Avoid creating, updating, or deleting tasks.
- Preserve the existing empty-result behavior when no tasks match.

## Guided task creation

Selecting Create task opens a guided form that asks:

> Which task type?

The type selector must immediately control which fields are displayed.

### Todo

Show:

- Description.
- Clickable date picker for the task date.

### Deadline

Show:

- Description.
- Clickable date picker.
- Clickable time picker.

### Event

Show:

- Description.
- Start date picker.
- Start time picker.
- End date picker.
- End time picker.

### Recurring

Show:

- Description.
- Day-of-week selector, such as Monday through Sunday.
- Clickable time picker.
- The recurrence summary should clearly represent the selected schedule, for
  example `every Wednesday at 21:00`.

The creation form must use the button label `Save created task`.

Creation behavior:

- No task is created before a type is selected and submitted.
- Only fields relevant to the selected type are shown.
- Date and time values are converted to Bao's existing `YYYY-MM-DD HHMM`
  command format.
- Todo dates are persisted with the task and shown when the task is viewed or
  searched.
- Recurring day and time selections are converted into the existing recurrence
  command format and persisted as the recurrence rule.
- Valid input creates and persists the task through existing Bao command
  behavior.
- Bao's normal creation response appears in the conversation panel.
- The creation workflow closes after successful creation.
- Invalid or incomplete input creates nothing, shows the existing validation or
  usage response, and keeps the form open.

## Search and task selection

The Search and update workflow must provide:

- Search input.
- Attribute selector.
- Search action.
- Selectable search results.

Supported search attributes are:

- `any`
- `task`
- `description`
- `type`
- `status`
- `note`
- `date`
- `recurrence`

Search must:

- Search only the authenticated user's tasks.
- Identify results clearly.
- Display each task's stable `task_id`.
- Refresh from current storage.
- Permit searching with an empty query to show all matching tasks.

Selecting a result must immediately open its update form and populate it with
the selected task's current values.

## Task update

The update form must be scoped to the selected task and display editable
fields for its task type.

Supported controls include:

- Description.
- Note.
- Relevant clickable date/time fields.
- Relevant recurrence field.
- Completion selector with `Leave unchanged`, `Mark done`, and `Mark undone`.
- `Save updated task`.
- `Delete`.

Update behavior:

- Saving field changes must not require changing completion state.
- Valid changes update only the selected task owned by the authenticated user.
- Changes are persisted and remain available after a later sign-in.
- Successful updates refresh the conversation and search results.
- The update form closes after a successful save.
- Invalid input leaves stored data unchanged and keeps the form open with a
  clear validation or command-usage response.
- Create and Search/Update workflows remain mutually exclusive.

## Task deletion

Delete must require confirmation before removing a task.

After confirmation:

- Only the selected authenticated user's task is removed.
- The task is removed from persistent storage.
- The task disappears from search results and conversation views.
- Later filters and searches are rebuilt from current storage.
- The old search result can no longer update the deleted task.
- The update form closes.

Cancelling deletion must leave the task unchanged.

## Stable task identity

Todo, deadline, event, and recurring tasks must share one persisted integer
`task_id` sequence per user.

Task IDs must:

- Be assigned when a task is created.
- Be persisted and restored.
- Be displayed in search results.
- Remain stable after other tasks are deleted.
- Never be reused.
- Not renumber remaining tasks.

Existing CLI display numbering remains unchanged. Stable IDs are used for UI
selection and persistence.

## Close Bao

The authenticated workspace must provide a clearly labelled `× Close Bao`
control.

Close behavior:

- The user must confirm before shutdown.
- Cancelling leaves Bao running.
- The action requires an authenticated session.
- No task or account data is modified.
- Only the current local Bao process is stopped.
- Unrelated processes are never terminated.
- The listening port is released.
- The browser displays that Bao has been closed and explains that Bao must be
  restarted from the terminal.

## Privacy and compatibility

- Alice can see and modify only Alice's tasks.
- Bob's tasks must remain unavailable to Alice.
- All workspace actions must use the authenticated user's task store.
- The CLI continues to use its existing shared task behavior.
- Existing command parsing and response formats remain compatible.
- Sensitive authentication values must not be exposed in UI output or logs.
- The application must not require a database for the first version.

## Implementation locations

- `src/bao/streamlit_app.py` — Streamlit pages, session state, workflows, and
  UI actions.
- `src/bao/ui.py` — compatibility launcher for the Streamlit application.
- `src/bao/tasks.py` and `src/bao/task.py` — task persistence and stable task
  identity.
- `src/bao/users.py` — local accounts and password hashes.
- `tests/test_streamlit_app.py` — Streamlit helper, authentication, command,
  task-isolation, and search tests.
- `tests/test_bao.py` — existing command and task behavior tests.

## Verification requirements

Before considering the Streamlit application complete, run:

```bash
uv sync --frozen
uv run ruff format --check .
uv run ruff check src tests
uv run mypy src tests
uv run pytest
```

The maintained application must pass all configured checks, and the Streamlit
server must boot successfully on the documented local address.
