# Development Guidelines

## Code Quality

- Use type hints for all function parameters and return values
- Follow PEP 8 style guidelines
- Use descriptive variable and function names
- Add docstrings to all public functions and classes

## Testing

- Write unit tests for all business logic
- Aim for >80% code coverage
- Use descriptive test names
- Test both success and failure cases

## Git Workflow

- Use descriptive commit messages
- Keep commits focused on single changes
- Use feature branches for new work
- Rebase before merging to main

## Agent Workflow

- Agents must stay within their defined scope
- Document all changes in commit messages
- Update task status in TASKS.md
- Request supervisor review for scope changes

## Performance

- Profile code before optimizing
- Prefer readable code over micro-optimizations
- Test on target platforms (Android/desktop)

## Security

- Never commit secrets or API keys
- Validate all user inputs
- Use secure defaults for file permissions