"""Provide Bao's alternative local Streamlit user interface."""

from __future__ import annotations

import os
import re
import signal
import threading
from datetime import UTC, date, datetime, time
from pathlib import Path
from typing import Any, cast

import streamlit as st

from bao.llm import (
    LLM_API_KEY_VARIABLE,
    LLM_BASE_URL_VARIABLE,
    LLM_MODEL_VARIABLE,
    ask_task_assistant,
    llm_configuration_error,
)
from bao.parser import _parse_datetime_parts
from bao.read_task_commands import TASK_TYPES, Command
from bao.task import Task
from bao.tasks import Tasks
from bao.users import authenticate_account, create_account, load_accounts

USERS_ENVIRONMENT_VARIABLE = "BAO_USERS"
CAT_ASSET_DIRECTORY = Path(__file__).resolve().parents[2] / "assets" / "cats"
CAT_ASSETS = {
    "chat": "chat-cat.png",
    "create": "create-cat.png",
    "search": "search-cat.png",
    "deadline": "deadline-cat.png",
    "recurring": "recurring-cat.png",
    "todo": "todo-cat.png",
    "event": "event-cat.png",
    "close": "close-cat.png",
}
WEEKDAYS = (
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
)
CAT_THEME_CSS = """
<style>
:root {
    --bao-cream: #fff8ee;
    --bao-ivory: #fffcf7;
    --bao-charcoal: #292522;
    --bao-ginger: #d97745;
    --bao-sage: #7b9a82;
    --bao-rose: #c96b68;
    --bao-lavender: #a99bc7;
}

body,
[data-testid="stAppViewContainer"] {
    background: var(--bao-cream);
    color: var(--bao-charcoal);
}

[data-testid="stSidebar"] {
    background: var(--bao-ivory);
    border-right: 1px solid color-mix(in srgb, var(--bao-ginger) 22%, transparent);
}

[data-testid="stChatMessage"] {
    border-radius: 0.8rem;
    border: 1px solid color-mix(in srgb, var(--bao-ginger) 18%, transparent);
}

button[kind="primary"] {
    background: var(--bao-ginger);
    border-color: var(--bao-ginger);
}

button[kind="primary"]:hover {
    background: #bd5e31;
    border-color: #bd5e31;
}

@media (prefers-color-scheme: dark) {
    :root {
        --bao-cream: #211d1a;
        --bao-ivory: #2b2622;
        --bao-charcoal: #fff8ee;
    }
}
</style>
"""


def _configured_users() -> dict[str, str]:
    configured = os.environ.get(USERS_ENVIRONMENT_VARIABLE, "")
    return {
        username: password
        for item in configured.split(",")
        for username, separator, password in [item.partition(":")]
        if separator
    }


def _authenticate(username: str, password: str) -> bool:
    configured = _configured_users()
    if username in configured and configured[username] == password:
        return True
    return authenticate_account(username, password)


def _username_available(username: str) -> bool:
    return username not in _configured_users() and username not in load_accounts()


def _valid_username(username: str) -> bool:
    return (
        3 <= len(username) <= 32
        and username.replace("_", "").replace("-", "").isalnum()
    )


def _run_command(username: str, command_text: str) -> str:
    command = Command.parse_user_response_with_command_pattern(command_text)
    if isinstance(command, str):
        return command
    if command is None:
        return ""
    return command.execute_command(Tasks(username))


def _append_exchange(command_text: str, response: str) -> None:
    st.session_state.messages.extend([("user", command_text), ("assistant", response)])


def _apply_cat_theme() -> None:
    """Apply Bao's shared visual theme to the Streamlit application."""
    st.markdown(CAT_THEME_CSS, unsafe_allow_html=True)


def _render_cat_header(asset_key: str, title: str, caption: str) -> None:
    """Render a cat illustration beside a workflow heading."""
    image_column, text_column = st.columns([1, 3], vertical_alignment="center")
    with image_column:
        asset_path = CAT_ASSET_DIRECTORY / CAT_ASSETS[asset_key]
        if asset_path.exists():
            st.image(str(asset_path), width=180)
    with text_column:
        st.header(title)
        st.caption(caption)


def _save_llm_enabled_state() -> None:
    st.session_state.llm_enabled = st.session_state.llm_enabled_checkbox


def _init_state() -> None:
    defaults: dict[str, Any] = {
        "username": None,
        "auth_page": "login",
        "workflow": "chat",
        "messages": [],
        "llm_enabled": False,
        "selected_task_id": None,
        "search_results": [],
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def _render_login() -> None:
    st.title("Bao 🐾")
    st.subheader("Sign in")
    with st.form("login_form"):
        username = st.text_input("Username", autocomplete="username")
        password = st.text_input(
            "Password", type="default", autocomplete="current-password"
        )
        submitted = st.form_submit_button("Login", type="primary")
    if submitted:
        if _authenticate(username, password):
            st.session_state.username = username
            st.session_state.auth_page = "login"
            st.rerun()
        st.error("Invalid username or password.")
    if st.button("Sign up"):
        st.session_state.auth_page = "signup"
        st.rerun()


def _render_signup() -> None:
    st.title("Bao 🐾")
    st.subheader("Sign up")
    with st.form("signup_form"):
        username = st.text_input("Username", autocomplete="username")
        password = st.text_input("Password", type="password")
        confirmation = st.text_input("Confirm password", type="password")
        submitted = st.form_submit_button("Create account", type="primary")
    if submitted:
        if not _valid_username(username):
            st.error(
                "Username must be 3–32 characters using letters, numbers, "
                "underscores, or hyphens."
            )
        elif len(password) < 8:
            st.error("Password must be at least 8 characters.")
        elif password != confirmation:
            st.error("Passwords do not match.")
        elif not _username_available(username):
            st.error("Username is already in use.")
        else:
            create_account(username, password)
            st.session_state.username = username
            st.session_state.auth_page = "login"
            st.rerun()
    if st.button("Return to sign in"):
        st.session_state.auth_page = "login"
        st.rerun()


def _render_navigation() -> None:
    st.sidebar.title("Bao 🐾")
    st.sidebar.caption(f"Signed in as {st.session_state.username}")
    if st.sidebar.button("🐱💬 Chat about task", use_container_width=True):
        st.session_state.workflow = "chat"
    if st.sidebar.button("🐾 Create task", use_container_width=True):
        st.session_state.workflow = "create"
    if st.sidebar.button("👀 View task", use_container_width=True):
        st.session_state.workflow = "view"
    if st.sidebar.button("🔍 Search and update task", use_container_width=True):
        st.session_state.workflow = "search"
    if st.sidebar.button("🤖 Enable LLM", use_container_width=True):
        st.session_state.workflow = "llm"

    if st.sidebar.button("× Close Bao", use_container_width=True):
        st.session_state.close_requested = True
    if st.session_state.get("close_requested", False):
        st.sidebar.warning("Close Bao and stop the local server?")
        confirmed = st.sidebar.checkbox("I confirm", key="close_confirmation")
        if confirmed and st.sidebar.button("Confirm close", type="primary"):
            st.session_state.closed = True
            st.rerun()


def _render_conversation() -> None:
    for role, content in st.session_state.messages:
        with st.chat_message(role):
            if role == "assistant":
                st.markdown(content)
            else:
                st.markdown(f"```text\n{content}\n```")


def _render_chat() -> None:
    _render_cat_header(
        "chat",
        "Chat about task",
        "Your friendly Bao cat is ready to talk through your task nook.",
    )
    if not st.session_state.messages:
        st.info("What should we pounce on first?")
    _render_conversation()
    with st.form("command_form", clear_on_submit=True):
        command = st.text_input("Command or question")
        submitted = st.form_submit_button("Submit", type="primary")
        ask_ai = st.form_submit_button(
            "Ask Bao AI", disabled=not st.session_state.llm_enabled
        )
    if not st.session_state.llm_enabled:
        st.caption("Enable LLM in the sidebar to use Ask Bao AI.")
    if submitted and command.strip():
        _append_exchange(command, _run_command(st.session_state.username, command))
        st.rerun()
    if ask_ai and command.strip():
        with st.spinner("Asking Bao AI..."):
            response = ask_task_assistant(
                st.session_state.username,
                command,
                st.session_state.messages,
            )
        _append_exchange(command, response)
        st.rerun()
    if st.button("Clear"):
        st.session_state.messages = []
        st.rerun()


def _render_llm() -> None:
    """Configure and enable optional task-assistance chat."""
    st.header("Enable LLM")
    st.write("Enable AI assistance separately from normal task commands.")

    configuration_error = llm_configuration_error()
    if configuration_error is not None:
        st.error(configuration_error)
        st.info(
            "Set the LLM environment variables before starting Bao. "
            f"The API key is read from {LLM_API_KEY_VARIABLE} and is never "
            "displayed here."
        )
        st.session_state.llm_enabled = False
        return

    st.success("LLM configuration detected.")
    st.caption(f"Endpoint: {os.environ[LLM_BASE_URL_VARIABLE]}")
    st.caption(f"Model: {os.environ[LLM_MODEL_VARIABLE]}")
    st.session_state.setdefault("llm_enabled_checkbox", st.session_state.llm_enabled)
    st.checkbox(
        "Enable Ask Bao AI in Chat about task",
        key="llm_enabled_checkbox",
        on_change=_save_llm_enabled_state,
    )


def _datetime_text(selected_date: date, selected_time: time) -> str:
    return f"{selected_date:%Y-%m-%d} {selected_time:%H%M}"


def _recurrence_rule(day: str, selected_time: time) -> str:
    """Build the normalized recurrence rule stored by the Streamlit UI."""
    return f"{day} at {selected_time:%H:%M}"


def _split_recurrence_rule(rule: str | None) -> tuple[str, time]:
    """Load a normalized or legacy recurrence rule into picker values."""
    if rule:
        matched = re.fullmatch(
            r"(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)"
            r"(?:\s+at\s+(\d{2}):(\d{2}))?",
            rule,
            re.IGNORECASE,
        )
        if matched:
            day = matched.group(1).capitalize()
            hour = int(matched.group(2) or 0)
            minute = int(matched.group(3) or 0)
            return day, time(hour=hour, minute=minute)
    return "Monday", time.min


def _render_datetime_fields(prefix: str, include_end: bool = False) -> tuple[str, ...]:
    date_label = "Event start date" if prefix == "event" else f"{prefix} date"
    time_label = "Event start time" if prefix == "event" else f"{prefix} time"
    start_date = st.date_input(date_label, key=f"{prefix}_date")
    start_time = st.time_input(time_label, key=f"{prefix}_time")
    values = [_datetime_text(start_date, start_time)]
    if include_end:
        end_date = st.date_input("Event end date", key=f"{prefix}_end_date")
        end_time = st.time_input("Event end time", key=f"{prefix}_end_time")
        values.append(_datetime_text(end_date, end_time))
    return tuple(values)


def _render_create() -> None:
    _render_cat_header(
        "create",
        "Create task",
        "Paint a new task into your day.",
    )
    # Keep this selector outside the form so changing it reruns Streamlit and
    # immediately redraws only the fields for the selected task type.
    task_type = st.selectbox("Which task type?", TASK_TYPES, key="create_type")
    deadline = ""
    todo_date = datetime.now(UTC).date()
    event_start = ""
    event_end = ""
    recurrence = ""
    with st.form("create_task_form"):
        description = st.text_input("Description", key="create_description")
        if task_type == "todo":
            todo_date = st.date_input("Task date", key="create_todo_date")
        elif task_type == "deadline":
            deadline = _render_datetime_fields("deadline")[0]
        elif task_type == "event":
            event_start, event_end = _render_datetime_fields("event", include_end=True)
        elif task_type == "recurring":
            recurrence_day = st.selectbox(
                "Day of week", WEEKDAYS, key="create_recurrence_day"
            )
            recurrence_time = st.time_input("Time", key="create_recurrence_time")
            recurrence = _recurrence_rule(recurrence_day, recurrence_time)
        submitted = st.form_submit_button("Save created task", type="primary")
    if submitted:
        if task_type == "deadline":
            command = f"deadline {description} /by {deadline}".strip()
        elif task_type == "event":
            command = (
                f"event {description} /from {event_start} /to {event_end}"
            ).strip()
        elif task_type == "recurring":
            command = f"recurring {description} /every {recurrence}".strip()
        else:
            command = f"todo {description} /on {todo_date:%Y-%m-%d}".strip()
        response = _run_command(st.session_state.username, command)
        _append_exchange(command, response)
        if response.startswith("Added:"):
            st.session_state.workflow = "search"
        st.rerun()


def _task_matches(task: Task, query: str, attribute: str) -> bool:
    query = query.casefold().strip()
    if not query:
        return True
    values = {
        "task": str(task),
        "description": task.description,
        "type": task.task_type,
        "status": "done" if task.done else "incomplete",
        "note": task.note or "",
        "date": " ".join(
            value.isoformat()
            for value in (
                getattr(task, "due_date", None),
                getattr(task, "due_datetime", None),
                getattr(task, "start_datetime", None),
                getattr(task, "end_datetime", None),
            )
            if value is not None
        ),
        "recurrence": getattr(task, "recurrence_rule", None) or "",
    }
    if attribute == "any":
        return any(query in str(value).casefold() for value in values.values())
    return query in str(values.get(attribute, "")).casefold()


def _search_tasks(query: str, attribute: str) -> list[Task]:
    return [
        task
        for task in Tasks(st.session_state.username)
        if _task_matches(task, query, attribute)
    ]


def _render_view() -> None:
    task_type = st.selectbox("Task type", TASK_TYPES)
    _render_cat_header(
        task_type,
        f"{task_type.title()} tasks",
        {
            "deadline": "Keep an eye on the clock.",
            "recurring": "Play with the rhythm of repeating tasks.",
            "todo": "A little homework at a time.",
            "event": "Dress up your plans for the occasion.",
        }[task_type],
    )
    tasks = [
        task for task in Tasks(st.session_state.username) if task.task_type == task_type
    ]
    if tasks:
        for task in tasks:
            st.write(f"**#{task.task_id}** — {task}")
    else:
        st.info("No tasks yet — your task nook is pleasantly quiet.")


def _parse_form_datetime(value: str) -> datetime | None:
    parsed = _parse_datetime_parts(value)
    if parsed is None:
        return None
    parsed_date, parsed_time = parsed
    return datetime.combine(parsed_date, parsed_time or time.min)


def _render_update(task: Task) -> None:
    st.subheader(f"Update task #{task.task_id}")
    task_fields = cast(Any, task)
    with st.form("update_task_form"):
        description = st.text_input("Description", value=task.description)
        note = st.text_input("Note", value=task.note or "")
        completion = st.selectbox(
            "Completion",
            ["Leave unchanged", "Mark done", "Mark undone"],
        )
        deadline = ""
        todo_date = datetime.now(UTC).date()
        event_start = ""
        event_end = ""
        recurrence = ""
        if task.task_type == "deadline":
            stored_deadline = task_fields.due_datetime
            deadline_date = st.date_input(
                "Deadline date",
                value=(
                    stored_deadline.date()
                    if stored_deadline
                    else datetime.now(UTC).date()
                ),
                key=f"update_deadline_date_{task.task_id}",
            )
            deadline_time = st.time_input(
                "Deadline time",
                value=(
                    (stored_deadline or datetime.min.replace(tzinfo=UTC))
                    .time()
                    .replace(tzinfo=None)
                ),
                key=f"update_deadline_time_{task.task_id}",
            )
            deadline = _datetime_text(deadline_date, deadline_time)
        elif task.task_type == "todo":
            stored_date = task_fields.due_date
            todo_date = st.date_input(
                "Task date",
                value=stored_date or datetime.now(UTC).date(),
                key=f"update_todo_date_{task.task_id}",
            )
        elif task.task_type == "event":
            stored_start = task_fields.start_datetime
            event_start_date = st.date_input(
                "Event start date",
                value=(
                    stored_start.date() if stored_start else datetime.now(UTC).date()
                ),
                key=f"update_event_start_date_{task.task_id}",
            )
            event_start_time = st.time_input(
                "Event start time",
                value=(
                    (stored_start or datetime.min.replace(tzinfo=UTC))
                    .time()
                    .replace(tzinfo=None)
                ),
                key=f"update_event_start_time_{task.task_id}",
            )
            event_start = _datetime_text(event_start_date, event_start_time)
            stored_end = task_fields.end_datetime
            event_end_date = st.date_input(
                "Event end date",
                value=(stored_end.date() if stored_end else datetime.now(UTC).date()),
                key=f"update_event_end_date_{task.task_id}",
            )
            event_end_time = st.time_input(
                "Event end time",
                value=(
                    (stored_end or datetime.min.replace(tzinfo=UTC))
                    .time()
                    .replace(tzinfo=None)
                ),
                key=f"update_event_end_time_{task.task_id}",
            )
            event_end = _datetime_text(event_end_date, event_end_time)
        elif task.task_type == "recurring":
            recurrence_day, recurrence_time = _split_recurrence_rule(
                task_fields.recurrence_rule
            )
            selected_day = st.selectbox(
                "Day of week",
                WEEKDAYS,
                index=WEEKDAYS.index(recurrence_day),
                key=f"update_recurrence_day_{task.task_id}",
            )
            selected_time = st.time_input(
                "Time",
                value=recurrence_time,
                key=f"update_recurrence_time_{task.task_id}",
            )
            recurrence = _recurrence_rule(selected_day, selected_time)
        save = st.form_submit_button("Save updated task", type="primary")
    if save:
        parsed_deadline = _parse_form_datetime(deadline) if deadline else None
        parsed_start = _parse_form_datetime(event_start) if event_start else None
        parsed_end = _parse_form_datetime(event_end) if event_end else None
        if (
            (deadline and parsed_deadline is None)
            or (event_start and parsed_start is None)
            or (event_end and parsed_end is None)
        ):
            st.error("Invalid date or time. Use YYYY-MM-DD HHMM.")
            return
        task_fields = cast(Any, task)
        task_fields.description = description
        task_fields.note = note or None
        if completion == "Mark done":
            task_fields.done = True
        elif completion == "Mark undone":
            task_fields.done = False
        if task.task_type == "deadline":
            task_fields.due_datetime = parsed_deadline
        elif task.task_type == "todo":
            task_fields.due_date = todo_date
        elif task.task_type == "event":
            task_fields.start_datetime = parsed_start
            task_fields.end_datetime = parsed_end
        elif task.task_type == "recurring":
            task_fields.recurrence_rule = recurrence or None
        tasks = Tasks(st.session_state.username)
        stored_task = next(stored for stored in tasks if stored.task_id == task.task_id)
        stored_fields = cast(Any, stored_task)
        stored_fields.description = task.description
        stored_fields.note = task.note
        stored_fields.done = task.done
        if task.task_type == "deadline":
            stored_fields.due_datetime = task_fields.due_datetime
        elif task.task_type == "todo":
            stored_fields.due_date = task_fields.due_date
        elif task.task_type == "event":
            stored_fields.start_datetime = task_fields.start_datetime
            stored_fields.end_datetime = task_fields.end_datetime
        elif task.task_type == "recurring":
            stored_fields.recurrence_rule = task_fields.recurrence_rule
        tasks.save()
        st.session_state.messages.append(("assistant", f"Updated:\n{task}"))
        st.session_state.selected_task_id = None
        st.rerun()

    confirm_delete = st.checkbox(
        "Confirm deletion", key=f"confirm_delete_{task.task_id}"
    )
    if confirm_delete and st.button("Delete", type="secondary"):
        tasks = Tasks(st.session_state.username)
        for index, stored_task in enumerate(tasks):
            if stored_task.task_id == task.task_id:
                tasks.pop(index)
                tasks.save()
                break
        description = task.description.casefold()
        st.session_state.messages = [
            (role, content)
            for role, content in st.session_state.messages
            if description not in content.casefold()
        ]
        st.session_state.search_results = [
            result
            for result in st.session_state.search_results
            if result.task_id != task.task_id
        ]
        st.session_state.clear_search_selection = True
        st.session_state.messages.append(("assistant", "Done — neatly tucked away."))
        st.session_state.selected_task_id = None
        st.rerun()


def _render_search() -> None:
    _render_cat_header(
        "search",
        "Search and update task",
        "Your detective cat will sniff out the right task.",
    )
    if st.session_state.pop("clear_search_selection", False):
        st.session_state.pop("search_result_selector", None)
    with st.form("search_tasks_form"):
        attribute = st.selectbox(
            "Search by",
            [
                "any",
                "task",
                "description",
                "type",
                "status",
                "note",
                "date",
                "recurrence",
            ],
        )
        query = st.text_input("Search tasks")
        submitted = st.form_submit_button(
            "",
            icon=":material/search:",
            help="Search tasks",
            type="primary",
        )
    if submitted:
        st.session_state.search_results = _search_tasks(query, attribute)

    results = st.session_state.search_results
    if not submitted and not results:
        st.info("Search your task nook with the search icon.")
        return
    if not results:
        st.info("No matching tasks — this nook is quiet for now.")
        return
    labels = [f"#{task.task_id} — {task}" for task in results]
    selected_label = st.radio("Search results", labels, key="search_result_selector")
    selected_id = int(selected_label.split("#", 1)[1].split(" ", 1)[0])
    st.session_state.selected_task_id = selected_id
    selected = next(task for task in results if task.task_id == selected_id)
    _render_update(selected)


def _render_workspace() -> None:
    if st.session_state.get("closed", False):
        _render_cat_header(
            "close",
            "Bao has been closed",
            "Bao is heading out for now — see you next time.",
        )
        st.write("Restart Bao from the terminal to use it again.")
        threading.Timer(0.5, lambda: os.kill(os.getpid(), signal.SIGTERM)).start()
        return
    _render_navigation()
    workflow = st.session_state.workflow
    if workflow == "chat":
        _render_chat()
    elif workflow == "llm":
        _render_llm()
    elif workflow == "create":
        _render_create()
    elif workflow == "view":
        _render_view()
    else:
        _render_search()


def main() -> None:
    """Run the Streamlit Bao application."""
    st.set_page_config(page_title="Bao", page_icon="🐱", layout="wide")
    _apply_cat_theme()
    _init_state()
    if st.session_state.username is None:
        if st.session_state.auth_page == "signup":
            _render_signup()
        else:
            _render_login()
        return
    _render_workspace()


if __name__ == "__main__":
    main()
