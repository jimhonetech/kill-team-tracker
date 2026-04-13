# Architecture Overview

## Application Structure

```
kill-team-tracker/
├── main.py              # Application entry point (UV-generated)
├── pyproject.toml       # Project configuration and dependencies (UV)
├── app/
│   ├── ui/              # Kivy screens and layouts
│   ├── state/           # Game logic and data models
│   └── storage/         # Data persistence layer
├── tests/               # Test suite
└── docs/                # Documentation
```

## V1 Scope

Version 1 focuses on essential score tracking without full game rule implementation:

- **Game State**: Turn number, player scores (Command Points, VP categories), selected operation
- **Operations**: Simple selection for end-game bonus calculation
- **Persistence**: Local JSON files for save/resume
- **UI**: Single screen with score controls and game management buttons

## Multi-Agent Development Pattern

The development process is managed by specialized agents:

### Supervisor Agent
- Coordinates overall development workflow
- Assigns tasks to specialist agents
- Validates completed work
- Manages task dependencies

### UI Agent
- Manages Kivy interface components
- Creates screens, layouts, and widgets
- Handles user interaction patterns
- Ensures responsive design

### State Agent
- Implements game scoring logic
- Manages data models and state transitions
- Defines serialization contracts for persistence
- Does not own storage adapter implementation
- Validates business rules

### Packaging Agent
- Configures Buildozer for Android builds
- Manages dependencies and build settings
- Handles platform-specific requirements
- Optimizes for mobile deployment
- Does not implement app feature behavior

### QA Agent
- Runs automated tests
- Performs smoke tests on desktop
- Validates functionality
- Checks code quality
- Owns pass/fail recommendation only (no feature implementation)

## Data Flow

1. User interactions → UI components
2. UI events → State management
3. State changes → JSON persistence
4. State updates → UI refresh

## Development Tools

- **UV**: Python project management and dependency resolution
- **Kivy**: Cross-platform UI framework
- **Buildozer**: Android packaging and deployment
- **pytest**: Test framework with coverage reporting
- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Type checking
- **pre-commit**: Automated code quality checks
- **GitHub Actions**: CI/CD pipeline

## Development Principles

- Separation of concerns between agents
- Testable, reversible changes
- Minimal dependencies
- Platform-agnostic core logic
