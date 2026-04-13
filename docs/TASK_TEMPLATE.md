# Task Template

Use this template when creating or refining tasks in `tasks/TASKS.md`.

```text
Task ID: T-<number>
Title: <short action-oriented title>
Owner: <Supervisor | UI Agent | State Agent | Packaging Agent | QA Agent>
State: <Backlog | Assigned | In QA | In Review | Done | Blocked>
Depends on: <optional task IDs>
Scope:
- <what is included>
Out of Scope:
- <what is explicitly excluded>
Acceptance Checks:
- <check 1>
- <check 2>
Deliverables:
- <files/artifacts expected>
Handoff Target:
- <next agent>
Notes:
- <constraints or assumptions>
```

## Task Writing Rules

- One primary owner at a time.
- Keep tasks small enough for one implementation pass and one QA pass.
- Write measurable acceptance checks.
- Explicitly list out-of-scope items to prevent creep.
- For code-impacting tasks, include a pre-commit check in Acceptance Checks (default: `uv run pre-commit run --all-files`).
