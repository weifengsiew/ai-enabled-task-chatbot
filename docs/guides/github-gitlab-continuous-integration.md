# Continuous Integration (CI) — 1-Page Guide

## What is CI?

**Continuous Integration (CI)** means integrating small code changes into a shared repository frequently and automatically checking each change.

The goal is simple:

> **Every push is verified by the same repeatable checks on a clean machine.**

This gives the team fast, consistent feedback before broken changes spread.

---

## Why do we need CI?

### Without CI

- Someone has to **remember every check** before merging.
- Different developers may run different checks.
- “**Works on my laptop**” can hide missing files, packages, or machine-specific setup.
- Large batches of changes meet late, so failures become **harder to trace**.
- A shared branch can break without everyone noticing immediately.

### With CI

- Every push runs the **same checks automatically**.
- Checks run on a **clean machine**, reducing hidden local dependencies.
- Small changes are validated often.
- Failures are found **close to the change that caused them**.
- A green pipeline gives the team shared evidence that the current code passes the agreed checks.

---

## How CI works

1. A developer **pushes a change**.
2. The CI platform reads the project’s **pipeline configuration**.
3. A fresh **runner** starts in a clean environment.
4. The runner installs what the project needs.
5. The runner executes the project’s automated checks.
6. The commit or pipeline **passes or fails**.

Typical checks include:

- dependency consistency
- runtime/version checks
- linting
- formatting
- type checking
- automated tests

---

## What CI gives a team

**Consistency**  
Everyone’s changes are checked the same way.

**Fast feedback**  
Problems appear soon after the change that introduced them.

**Confidence**  
A passing pipeline shows that the latest code still satisfies the team’s automated checks.

**Safer collaboration**  
Frequent integration reduces painful late-stage surprises.

---

## Important idea

**CI is not a new kind of test.**

CI is the automation layer that runs the checks you already trust, repeatedly and consistently, on a clean machine.

A useful mental model is:

> **Local checks prove it works for you. CI checks whether it works for the shared project.**

---

# File & Code Examples

## Example project structure

```text
my-project/
├── .github/
│   └── workflows/
│       └── ci.yml
├── pyproject.toml
├── uv.lock
├── src/
└── tests/
```

## GitLab CI/CD setup

Create this file in your repository:

```text
.github/workflows/ci.yml
```

GitHub automatically detects workflow files inside `.github/workflows/`.

The workflow below runs CI on **every push**.

## Example `.github/workflows/ci.yml`

```yaml
name: CI

on:
  push:

jobs:
  checks:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v6

      - name: Set up Python
        run: uv python install 3.13

      - name: Install dependencies
        run: uv sync --frozen

      - name: Ruff lint
        run: uv run ruff check .

      - name: Ruff format check
        run: uv run ruff format --check .

      - name: Type check
        run: uv run mypy .

      - name: Run tests
        run: uv run pytest
```

The key part is:

```yaml
on:
  push:
```

This tells GitHub Actions to run the workflow whenever a commit is pushed to the repository.

After adding the file:

1. Commit `.github/workflows/ci.yml`.
2. Push the commit to GitHub.
3. Open the repository on GitHub.
4. Select the **Actions** tab.
5. Open the **CI** workflow run to see whether the checks passed or failed.

The flow is:

```text
git push
   ↓
GitHub detects .github/workflows/ci.yml
   ↓
GitHub starts a clean Ubuntu runner
   ↓
The repository is checked out
   ↓
Python and dependencies are installed
   ↓
Ruff → mypy → pytest
   ↓
PASS or FAIL
```
