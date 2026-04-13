# Development Workflow

## Multi-Agent Process

1. **Task Definition**: Supervisor creates or updates a task using `docs/TASK_TEMPLATE.md`.
2. **Task Assignment**: Supervisor assigns exactly one primary owner (specialist agent).
3. **Specialist Execution**: Specialist implements scoped changes and self-checks.
4. **QA Validation**: Specialist hands off to QA using `docs/HANDOFF_TEMPLATE.md`.
5. **Supervisor Decision**: QA hands off pass/fail recommendation to supervisor.
6. **Close or Rework**: Supervisor marks Done, requests changes, or reassigns.

## Branch Strategy

- **Main Branch**: Protected, only accepts merges via approved PRs
- **Feature Branches**: Named `agent/[type]-[task]` (e.g., `agent/ui-turn-display`)
- **Pre-commit Hooks**: Prevent direct commits to main branch

## Ownership Enforcement

- One task has one active owner at a time.
- Agents edit only files in their ownership scope unless the task explicitly grants exceptions.
- Cross-scope edits must be listed in the assignment before implementation.
- QA may change tests/tooling but not app feature behavior.

## Process Enforcement

The workflow is mandatory for code-impacting tasks.

- A task cannot move to `Assigned` without a full task card (owner, scope, out-of-scope, acceptance checks, handoff target).
- A task cannot move to `In QA` without a specialist handoff using `docs/HANDOFF_TEMPLATE.md`.
- A task cannot move to `In Review` without QA pass/fail recommendation and evidence.
- A task cannot move to `Done` without supervisor acceptance recorded in task notes.
- Handoffs missing checks run, evidence, or risk notes must be rejected.

## Review Process

### Review Frequency
- **Per Task**: Required handoff from specialist to QA, then QA to supervisor
- **Per PR**: Supervisor validates scope, evidence, and risk notes
- **Milestone Review**: Optional checkpoint for architecture/process adjustments

### Review Types
- **Low Risk**: Documentation, formatting, basic tests → Quick approval
- **Medium Risk**: New features, UI changes → Code review + testing
- **High Risk**: Architecture changes, data model updates → Thorough review

### PR Requirements
- Clear description of changes
- Updated TASKS.md with owner and completion status
- Handoff evidence from `docs/HANDOFF_TEMPLATE.md`
- Passing tests (or explicit failing checks with rationale)
- No direct commits to main

## Task States

- **Backlog**: Unassigned tasks
- **Assigned**: Currently being worked by an agent
- **In QA**: Awaiting QA validation
- **In Review**: QA complete, awaiting supervisor decision
- **Done**: Approved and integrated
- **Blocked**: Cannot proceed without external decision/input

## Communication Protocol

- Tasks defined in `tasks/TASKS.md`
- Assignments and updates use task IDs
- Handoffs use `docs/HANDOFF_TEMPLATE.md`
- Status communicated via task state and supervisor decision

## Quality Gates

- Specialist self-check completed
- QA validation executed (pass/fail with evidence)
- Risks and follow-ups documented
- Supervisor acceptance recorded

## QA Severity Decision Policy

Use this policy for supervisor acceptance decisions:

- `Critical`: Always block. Task state remains `Blocked` or returns to `Assigned` for fix.
- `Major`: Block by default. Exception allowed only if supervisor creates a follow-up task with owner and due milestone before acceptance.
- `Minor`: Non-blocking. Must be tracked as follow-up task when not fixed immediately.

If a task has mixed severities, the highest severity controls the decision.

## Escalation

If an agent encounters blocking issues:
1. Document blocker and attempted resolution in handoff format
2. Mark task as Blocked in `tasks/TASKS.md`
3. Supervisor decides: clarify, split task, or reassign owner
