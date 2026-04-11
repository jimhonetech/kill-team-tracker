# Task Backlog

## Current Tasks

### Supervisor Tasks
- [ ] Review v1 requirements and assign initial development tasks
- [ ] Define data models for game state (players, scores, turn)

### UI Agent Tasks
- [ ] Create main game screen with turn display
- [ ] Implement player score sections (Command Points, Tac/Kill/Main VP)
- [ ] Add operation selection dropdown for end-game bonus
- [ ] Create new game/reset button
- [ ] Add save/resume buttons

### State Agent Tasks
- [ ] Define GameState model with turn, players, scores
- [ ] Implement score update methods (increment/decrement)
- [ ] Add operation selection and bonus calculation logic
- [ ] Implement new game reset functionality
- [ ] Add JSON serialization for save/load

### Packaging Agent Tasks
- [ ] Configure pyproject.toml with Kivy dependencies
- [ ] Set up Buildozer spec for Android build
- [ ] Add local storage permissions
- [ ] Test desktop build with UV

### QA Agent Tasks
- [ ] Create unit tests for state models and calculations
- [ ] Implement UI smoke tests for screen loading
- [ ] Add integration tests for save/load functionality
- [ ] Set up test automation with pytest

## Completed Tasks

- [x] Create initial repository scaffold
- [x] Define multi-agent workflow structure
- [x] Document agent responsibilities
- [x] Specify v1 score-tracking requirements
- [x] Implement git branch protection hooks

## Task Format

- `[ ]` - Backlog/In Progress
- `[x]` - Completed
- `[!]` - Blocked/Needs Review

## Branch Workflow

When working on tasks:
1. Create feature branch: `git checkout -b agent/[type]-[task]`
2. Make changes and commit to branch
3. Create PR for supervisor review
4. Supervisor reviews and merges to main