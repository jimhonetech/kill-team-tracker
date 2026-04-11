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
- Handles persistence requirements
- Validates business rules

### Packaging Agent
- Configures Buildozer for Android builds
- Manages dependencies and build settings
- Handles platform-specific requirements
- Optimizes for mobile deployment

### QA Agent
- Runs automated tests
- Performs smoke tests on desktop
- Validates functionality
- Checks code quality

## Data Flow

1. User interactions → UI components
2. UI events → State management
3. State changes → JSON persistence
4. State updates → UI refresh

## Development Tools

- **UV**: Python project management and dependency resolution
- **Kivy**: Cross-platform UI framework
- **Buildozer**: Android packaging and deployment
- **pytest**: Test framework
3. State changes → Data persistence
4. State updates → UI refresh

## Development Principles

- Separation of concerns between agents
- Testable, reversible changes
- Minimal dependencies
- Platform-agnostic core logic