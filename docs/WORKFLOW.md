# Development Workflow

## Multi-Agent Process

1. **Task Identification**: Supervisor reviews `tasks/TASKS.md` and identifies next work item
2. **Agent Assignment**: Supervisor assigns task to appropriate specialist agent
3. **Task Execution**: Agent completes work according to their defined scope
4. **Handoff**: Agent updates relevant files and notifies supervisor of completion
5. **Validation**: Supervisor reviews changes and either approves or requests revisions
6. **Iteration**: Process repeats with next task

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