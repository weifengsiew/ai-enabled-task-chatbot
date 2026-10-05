# Bao Cat Theme

## Status

Complete

## User story

As a Bao task-manager user, I want a warm and friendly cat-themed interface,
so that managing everyday tasks feels more inviting without reducing clarity,
accessibility, or focus.

## Acceptance examples

### Example 1: Consistent cat branding

- Given the user opens the login page or authenticated workspace
- When the page renders
- Then it uses the `Bao 🐾` brand treatment consistently in the title,
  sidebar, and main workspace

### Example 2: Cat-themed navigation

- Given the user is authenticated
- When the sidebar navigation is displayed
- Then each workflow has a supporting cat-themed icon and an explicit text
  label that remains understandable without the emoji

### Example 3: Warm visual theme

- Given the user views any main Streamlit workflow
- When the interface renders in light or dark display mode
- Then it uses the shared cat-theme styling while keeping text and task status
  readable with sufficient contrast

### Example 4: Friendly empty states

- Given the user has no tasks, search results, or conversation messages
- When the relevant workflow is opened
- Then Bao shows a friendly cat-themed empty state without changing stored data

### Example 5: Clear task status

- Given a task is active, completed, overdue, or about to be deleted
- When the task is displayed
- Then its state is distinguishable through text or an icon as well as colour

### Example 6: Preserved behaviour

- Given the user uses task commands, authentication, persistence, or LLM
  assistance
- When the cat theme is enabled
- Then existing command syntax, task data, account handling, and read-only LLM
  behaviour remain unchanged

## Tests covered

- `tests/test_streamlit_app.py::test_cat_theme_defines_shared_light_and_dark_palette`
  — verifies the approved palette and dark-mode support.
- `tests/test_streamlit_app.py::test_cat_theme_has_an_illustration_for_each_workflow_and_task_type`
  — verifies that every workflow and task type maps to a local illustration.
- Existing task-management, authentication, and LLM tests — verify that the
  visual refresh does not change application behaviour; all 24 tests pass.

## Changes made

### Visual design

- **Primary background:** warm cream (`#FFF8EE`).
- **Surface/card background:** soft ivory (`#FFFCF7`).
- **Primary text:** charcoal (`#292522`).
- **Primary accent:** ginger orange (`#D97745`) for buttons, active states,
  and highlights.
- **Secondary accent:** muted sage (`#7B9A82`) for completed or positive
  states.
- **Attention accent:** muted rose (`#C96B68`) for destructive actions and
  validation errors.
- **Decorative accent:** soft lavender (`#A99BC7`) for optional AI-related
  details.
- **Style:** rounded cards, generous spacing, subtle borders, and restrained
  shadows. Avoid busy illustrations behind task content.

Use cat emojis such as `🐱`, `🐾`, and `😺` sparingly as supporting cues,
never as the only label for an action. Do not encode task status using colour
alone.

### Voice and copy

Use friendly cat-themed language for framing and empty states, while keeping
commands, errors, dates, and task status explicit.

| Current context | Cat-themed direction |
| --- | --- |
| App title | `Bao 🐾` |
| Signed-in caption | `Your task nook` or `Signed in as <username>` |
| Empty task list | `No tasks yet — your task nook is pleasantly quiet.` |
| Empty conversation | `What should we pounce on first?` |
| Completed task | `Done — neatly tucked away.` |
| AI assistant | `Bao's helper cat` or `Ask Bao AI` |
| Delete confirmation | `Remove this task from the nook?` |

Cat wording must not appear in security messages, authentication errors,
validation errors, or dates and times. Those messages remain direct.

### Implementation scope

MVP:

- Add a shared Streamlit CSS/theme layer using the palette above.
- Apply the `Bao 🐾` title and cat-themed navigation labels.
- Add cat-themed empty states and success/confirmation copy.
- Add local illustrations for chat, create, search, deadline, recurring, todo,
  event, and close workflows.
- Keep all task data, command syntax, account handling, and LLM behaviour
  unchanged.
- Add or update tests for user-visible helper text where practical.

Later enhancements:

- Add alternate locally stored Bao mascot poses for completed and overdue states.
- Let users choose between a subtle theme and a more playful theme.
- Add optional cat sounds or animations only if they can be disabled and do not
  affect accessibility or performance.

### Illustration mapping

- Chat about task — a cute cat holding a blank speech bubble.
- Create task — a cat painting with a brush and palette.
- Search and update task — a detective cat with a magnifying glass.
- Deadline task — a cat holding a friendly clock.
- Recurring task — a cat playing with a hanging yarn ball.
- Todo task — a cat doing homework with glasses and a pencil.
- Event task — a cat in a suit and tie with an invitation and teacup.
- Close Bao — a cat walking out through an open door.

The illustrations are transparent local PNG assets with no embedded text. Each
workflow keeps an explicit text heading and caption so the artwork is
decorative support rather than the only meaning conveyed to the user.

### Non-goals

- Renaming task types or changing command syntax to cat puns.
- Requiring external image, font, or animation services.
- Making the interface childish, noisy, or dependent on emoji rendering.
- Changing authentication, task storage, or LLM permissions as part of the
  visual refresh.

## Code locations

List only the files where the proposed changes will be added or made.

- `src/bao/streamlit_app.py` — shared theme styling, branding, navigation,
  cat-themed empty states, and illustration mapping.
- `assets/cats/*.png` — local transparent workflow, task-type, and close-state
  illustrations.
- `tests/test_streamlit_app.py` — tests for extracted UI helpers or
  user-visible theme copy and local illustration coverage.

## CI check results

- Pytest: [x] `uv run pytest` — 24 passed.
- Ruff lint: [x] `uv run ruff check src tests` — all checks passed.
- Ruff format: [x] `uv run ruff format --check .` — 28 files already formatted.
- Mypy: [x] `uv run mypy src tests` — no issues found in 15 source files.
- Shared CI pipeline: [ ]

The shared GitLab pipeline was not triggered from this workspace.
The Streamlit app booted successfully on fallback port `7861`; port `7860` was
occupied during verification.
