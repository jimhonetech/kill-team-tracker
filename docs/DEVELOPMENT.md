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

## Desktop Setup and Run

Use these commands for local desktop development with Kivy:

```bash
uv sync --dev
uv run python -c "import kivy; print(kivy.__version__)"
uv run python -c "from app.state import GameState; from app.ui.main_screen import MainGameScreen; screen = MainGameScreen(GameState()); print(screen.turning_point_label.text)"
uv run python -m app.main
```

Expected smoke output before full app run:

- `kivy` version prints successfully.
- Turning point smoke check prints `Turning Point 1`.

If running on a headless environment, use only the smoke commands and skip `uv run python -m app.main`.

## Performance

- Profile code before optimizing
- Prefer readable code over micro-optimizations
- Test on target platforms (Android/desktop)

## Security

- Never commit secrets or API keys
- Validate all user inputs
- Use secure defaults for file permissions
