# Development Workflow

## Multi-Agent Process

1. **Task Identification**: Supervisor reviews `tasks/TASKS.md` and identifies next work item
2. **Agent Assignment**: Supervisor assigns task to appropriate specialist agent
3. **Task Execution**: Agent completes work on a feature branch
4. **Pull Request**: Agent creates PR with changes for supervisor review
5. **Review & Merge**: Supervisor reviews PR, runs tests, then merges to main
6. **Iteration**: Process repeats with next task

## Branch Strategy

- **Main Branch**: Protected, only accepts merges via approved PRs
- **Feature Branches**: Named `agent/[type]-[task]` (e.g., `agent/ui-turn-display`)
- **Pre-commit Hooks**: Prevent direct commits to main branch

## Review Process

### Review Frequency
- **Per Task**: Not required - trust agents to complete assigned work
- **Per PR**: Supervisor reviews all code changes before merge
- **Milestone Review**: Weekly review of overall progress and architecture

### Review Types
- **Low Risk**: Documentation, formatting, basic tests → Quick approval
- **Medium Risk**: New features, UI changes → Code review + testing
- **High Risk**: Architecture changes, data model updates → Thorough review

### PR Requirements
- Clear description of changes
- Updated TASKS.md with completion status
- Passing tests (if applicable)
- No direct commits to main

## Task States

- **Backlog**: Unassigned tasks
- **Assigned**: Currently being worked by an agent
- **In Review**: Completed, awaiting supervisor validation
- **Done**: Approved and integrated

## Communication Protocol

- Tasks defined in `tasks/TASKS.md`
- Code changes committed with descriptive messages
- Documentation updated as needed
- Status communicated via task state changes

## Quality Gates

- All changes must pass QA agent's tests
- UI changes validated for usability
- State changes tested for correctness
- Packaging changes verified for build success

## Escalation

If an agent encounters blocking issues:
1. Document the issue in task description
2. Mark task as blocked
3. Supervisor reviews and either reassigns or breaks down the task