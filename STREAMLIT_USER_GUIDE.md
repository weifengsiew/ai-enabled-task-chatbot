# Bao Streamlit User Guide

Bao is a local task manager with a browser interface.

## Start Bao

From the project directory, run:

```bash
uv run streamlit run src/bao/streamlit_app.py \
  --server.address 127.0.0.1 \
  --server.port 7860
```

Open [http://127.0.0.1:7860](http://127.0.0.1:7860). If port `7860` is busy,
replace the port with `7861` in the command and URL.

Bao is intended for local use. Do not expose it publicly.

## Sign in or sign up

On the sign-in page:

- Enter your username and password.
- The sign-in password is visible while typing.
- Select **Sign up** to create a new account.

Sign-up usernames must be 3–32 characters and use only letters, numbers,
underscores, or hyphens. Passwords must contain at least 8 characters and
match their confirmation. New accounts are signed in automatically, and each
user has a private task list.

Configured users can be supplied before startup:

```bash
export BAO_USERS="alice:choose-a-password,bob:choose-another-password"
```

To enable AI assistance, configure the OpenAI-compatible LiteLLM endpoint
before starting Bao:

```bash
export BAO_LLM_API_STYLE="openai"
export BAO_LLM_BASE_URL="https://litellm.aiap23a-<your-project-id>-aut0.aisingapore.net/v1"
export BAO_LLM_API_KEY="your-api-key"
export BAO_LLM_MODEL="FW-DeepSeek-V4.1-Flash"
```

### Configure the API key and start Bao with LLM assistance

Bao reads the LLM settings from environment variables. On macOS with the
default Zsh shell, add them to `~/.zshrc` so they remain available in future
Terminal sessions:

```bash
nano ~/.zshrc
```

Add the following lines, replacing the API-key placeholder with your key and
using your assigned project ID. For the `acai` project, use this exact base
URL:

```bash
export BAO_LLM_API_STYLE="openai"
export BAO_LLM_BASE_URL="https://litellm.aiap23a-acai-aut0.aisingapore.net/v1"
export BAO_LLM_MODEL="FW-DeepSeek-V4.1-Flash"
export BAO_LLM_API_KEY="your-api-key"
```

In Nano, press **Ctrl+O**, press **Enter** to save, then press **Ctrl+X** to
exit. If this Terminal window was already open before you edited `~/.zshrc`,
reload the configuration:

```bash
source ~/.zshrc
test -n "$BAO_LLM_API_KEY" && echo "API key is set"
```

When you open a new Terminal window, macOS loads `~/.zshrc` automatically.
Start Bao from the project directory:

```bash
cd /Users/Hardisk_WeiFeng/AIAP/bao
uv run streamlit run src/bao/streamlit_app.py --server.port 7860
```

Open [http://127.0.0.1:7860](http://127.0.0.1:7860), sign in, select
**Enable LLM**, and enable **Ask Bao AI in Chat about task**. Then go to
**Chat about task** and use **Ask Bao AI**.

Do not commit `~/.zshrc` or the API key to the repository. If the key is ever
exposed, rotate it and update the value in `~/.zshrc`.

Keep the API key out of source control. Bao sends the signed-in user's task
context to the configured endpoint only when **Ask Bao AI** is selected.

## Workspace

After signing in, use the left navigation to select:

- **Chat about task** — enter direct Bao commands.
- **Enable LLM** — check the LLM configuration and enable AI assistance for
  task chat.
- **Create task** — create a task with a guided form.
- **View task** — filter tasks by type.
- **Search and update task** — find, edit, complete, or delete a task.

The conversation panel shows your commands and Bao's responses. **Clear**
removes the displayed conversation without deleting saved tasks.

In **Enable LLM**, confirm that the configured endpoint and model are detected,
then enable **Ask Bao AI in Chat about task**. In **Chat about task**, use
**Submit** for normal Bao commands and **Ask Bao AI** for natural-language help
such as “Which task should I do next?” The AI assistant is read-only; it can
suggest a Bao command but does not directly modify tasks.

When Bao AI suggests an action, it places the exact Bao command in a
copyable code block. Copy it, paste it into the Command box, and select
**Submit** to execute it.

The LLM enablement choice is retained while navigating within the current Bao
session. After restarting Bao, open **Enable LLM** and enable it again.

## Create tasks

Select **Create task**, choose a type, and complete the fields shown for that
type:

- **Todo** — description and date.
- **Deadline** — description, date, and time.
- **Event** — description, start date/time, and end date/time.
- **Recurring** — description, day of week, and time. For example, choose
  Wednesday and 9:00 PM to create `every Wednesday at 21:00`.

Select **Save created task**. Only fields relevant to the selected task type
are displayed.

## View, search, and update tasks

Use **View task** to show only `todo`, `deadline`, `event`, or `recurring`
tasks.

Use **Search and update task** to search by:

`any`, `task`, `description`, `type`, `status`, `note`, `date`, or `recurrence`.

Select a result to open its update form. You can edit its fields, choose
**Mark done** or **Mark undone**, and select **Save updated task**. Date and
time fields use clickable pickers.

Every task has a stable ID shown in search results. Deleting another task does
not renumber or reuse existing IDs.

To delete a selected task, confirm the deletion and select **Delete**. The task
is removed from your saved task list and search results.

## Direct commands

The **Command** box supports these commands:

```text
todo buy groceries /on 2026-10-10
deadline submit report /by 2026-10-10 1700
event project meeting /from 2026-10-10 0900 /to 2026-10-10 1000
recurring exercise /every Wednesday at 21:00
list
find report
filter todo
mark 1
unmark 1
note 1 include receipts
delete 1
```

Use `YYYY-MM-DD` for dates and four-digit `HHMM` for times. Use `/by` for
deadline commands; Bao also accepts `/due` as an alias.

## Stop Bao

Select **Close Bao**, confirm the action, and Bao will stop the current local
server. Restart it from the terminal to use it again.

## Troubleshooting

- If the page does not load, confirm that the Streamlit process is still
  running in the terminal.
- If port `7860` is occupied, start Bao on another local port.
- If tasks appear missing, sign in with the same username and start Bao from
  the same project directory where `data/users/` is stored.
- Stop the server with `Ctrl+C` in the terminal when necessary.
