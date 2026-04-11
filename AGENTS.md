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

See individual agent files in `agents/` for details.

## Workflow

1. Supervisor reviews current tasks and assigns work
2. Specialist agents complete assigned tasks
3. Agents hand off completed work back to supervisor
4. Supervisor validates and assigns next tasks

## Communication

Agents communicate through:
- Task assignments in `tasks/TASKS.md`
- Code changes in repository
- Documentation updates in `docs/`
- Status reports via commit messages