# Kill Team Tracker

A mobile app for tracking scores in Warhammer 40k Kill Team games, built with Kivy for cross-platform deployment.

## Overview

This project uses a multi-agent development workflow to manage development tasks across specialized agents:
- **Supervisor**: Orchestrates development workflow
- **UI Agent**: Manages Kivy interface and layouts
- **State Agent**: Handles game scoring logic and data persistence
- **Packaging Agent**: Manages Buildozer configuration for Android builds
- **QA Agent**: Runs tests and quality checks

## Setup

This project uses UV for Python dependency management.

1. Install UV: `curl -LsSf https://astral.sh/uv/install.sh | sh`
2. Install Python dependencies: `uv sync`
3. Run the app: `uv run python main.py`

## Development

### Code Quality
- **Linting**: `uv run flake8`
- **Formatting**: `uv run black .` and `uv run isort .`
- **Type checking**: `uv run mypy`
- **Pre-commit**: Runs automatically on commits

### Testing
- Run tests: `uv run pytest`
- With coverage: `uv run pytest --cov`

### CI/CD
- GitHub Actions runs linting and tests on pushes/PRs
- Pre-commit hooks ensure code quality locally

## Development Workflow

See [docs/WORKFLOW.md](docs/WORKFLOW.md) for the multi-agent development process.
See [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) for coding guidelines.

## Project Structure

- `agents/`: Agent definitions and responsibilities
- `app/`: Application source code
- `docs/`: Documentation
- `tasks/`: Task tracking and backlog
- `tests/`: Test suite
- `pyproject.toml`: Project configuration (UV)
- `.pre-commit-config.yaml`: Pre-commit hooks configuration
