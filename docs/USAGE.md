# Agent System Usage Guide

## 1. Start in VS Code

1. Open the repository in VS Code.
2. Confirm agent definitions exist in `.github/agents/`.
3. Open `tasks/TASKS.md` and pick or define the next task.
4. Use the Supervisor Agent first to assign owner, scope, and acceptance checks.

## 2. Recommended Workflow

Use this sequence for every code-impacting task:

1. Supervisor assigns a scoped task.
2. Specialist agent implements and self-checks.
3. Specialist runs pre-commit checks and fixes blocking issues.
4. Specialist hands off to QA using `docs/HANDOFF_TEMPLATE.md`.
5. QA validates and returns pass/fail handoff.
6. Supervisor accepts, requests fixes, or reassigns.

## 3. Example Prompts

### Start a Task

```text
Supervisor Agent: Take task T-201 from tasks/TASKS.md. Confirm owner, scope, acceptance checks, and exact next handoff target.
```

### Handoff Between Agents

```text
State Agent: Complete T-201 within your ownership scope, run uv run pre-commit run --all-files and fix blocking failures, then produce a handoff using docs/HANDOFF_TEMPLATE.md to QA Agent.
```

### Ask for Review

```text
QA Agent: Validate task T-201 using its acceptance checks. Return qa-pass or qa-fail with reproducible evidence.
```

### Recover From Errors

```text
Supervisor Agent: Task T-201 is blocked by ambiguous scoring requirements. Break it into smaller tasks, assign owners, and update tasks/TASKS.md states.
```

## 4. Do and Don't

Do:
- Keep one active owner per task.
- Use task IDs in all messages and handoffs.
- Keep handoffs short, reproducible, and evidence-based.
- Escalate blockers early with attempted resolution notes.
- Include pre-commit command output summary in every code-impacting handoff.

Don't:
- Let agents edit outside ownership without explicit scope exception.
- Skip QA for feature changes.
- Mix feature implementation with packaging-only or QA-only tasks.
- Accept vague "works for me" handoffs.

## 5. Efficiency and Control Tips

- Favor smaller tasks over broad feature bundles.
- Require acceptance checks before implementation starts.
- Keep branch names aligned to task IDs (for example, `agent/state-t201`).
- Reuse `docs/TASK_TEMPLATE.md` and `docs/HANDOFF_TEMPLATE.md` to avoid ad-hoc process drift.
- If rework loops exceed two iterations, have supervisor re-scope the task.

## 6. Task Intake Routine (Low Effort)

Use this routine when you are unsure what tasks to create next.

1. Pick 1-2 user outcomes from `docs/PRODUCT.md`.
2. Ask Supervisor to propose the next 3-5 smallest tasks.
3. Approve only tasks that pass the quick checklist below.
4. Move only one implementation task to `Assigned` at a time.

### Prompt to Generate Tasks

```text
Supervisor Agent: Using docs/PRODUCT.md and docs/ARCHITECTURE.md, propose the next 5 smallest tasks in docs/TASK_TEMPLATE.md format with owner, dependencies, acceptance checks, and handoff target.
```

### Prompt to Refine a Task

```text
Supervisor Agent: Refine task T-201 to be completable in one specialist pass and one QA pass. Tighten scope and rewrite acceptance checks to be measurable.
```

### Quick Checklist (Approve/Reject)

- One primary owner is named.
- Scope and out-of-scope are explicit.
- Acceptance checks are measurable.
- Dependency list is clear (or `none`).
- Next handoff target is explicit.

If any checklist item is missing, do not assign the task yet.
