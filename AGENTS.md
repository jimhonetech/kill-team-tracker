# Multi-Agent Development System

This project uses a hierarchical multi-agent system for development:

## Agent Hierarchy

- **Supervisor Agent**: Top-level coordinator that assigns tasks and manages workflow
- **Specialist Agents**:
  - UI Agent: Kivy interface development
  - State Agent: Game logic and data management
  - Packaging Agent: Build and deployment configuration
  - QA Agent: Testing and quality assurance

## Agent Responsibilities

Each agent has defined:
- Purpose and scope
- Input/output interfaces
- Handoff rules
- Done criteria

See individual agent files in `.github/agents/` for details.

## Ownership Rules

- Agents work only within their owned files/folders unless a task explicitly allows broader edits.
- Supervisor coordinates and validates. Supervisor does not implement product code.
- QA can add or update tests and quality tooling, but does not implement feature logic.
- Packaging can change build/dependency configuration, but does not change feature behavior.

## Required Artifacts

- Task definitions use `docs/TASK_TEMPLATE.md`.
- Handoffs use `docs/HANDOFF_TEMPLATE.md`.
- Agent replies follow the standard output block defined in `docs/HANDOFF_TEMPLATE.md`.

## Workflow

1. Supervisor reviews current tasks and assigns work
2. Specialist agent confirms scope, executes, and self-checks
3. Specialist hands off to QA with required evidence
4. QA validates and hands off to supervisor
5. Supervisor accepts, requests fixes, or reassigns

## Communication

Agents communicate through:
- Task assignments in `tasks/TASKS.md`
- Code changes in repository
- Documentation updates in `docs/`
- Structured handoff notes using `docs/HANDOFF_TEMPLATE.md`