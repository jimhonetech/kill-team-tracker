# Task Backlog

Use `docs/TASK_TEMPLATE.md` for new tasks. Keep each task small enough for one specialist owner and one QA pass.

## Task State Legend

- `[ ]` Backlog
- `[~]` Assigned/In Progress
- `[Q]` In QA
- `[R]` In Review (Supervisor)
- `[x]` Done
- `[!]` Blocked

## Current Tasks

### Queue
- [x] T-001 Supervisor: Review v1 requirements and assign initial implementation task
- [x] T-201 State Agent: Define GameState model with turn, players, scores
- [ ] T-401 QA Agent: Create unit tests for state models and calculations
- [ ] T-101 UI Agent: Create main game screen with turn display
- [ ] T-301 Packaging Agent: Configure pyproject.toml with Kivy dependencies
- [ ] T-202 State Agent: Implement score update methods (increment/decrement)
- [ ] T-203 State Agent: Add operation selection and bonus calculation logic
- [ ] T-204 State Agent: Implement new game reset behavior
- [ ] T-205 State Agent: Add JSON serialization contracts for save/load
- [x] T-206 State Agent: Add schema migration guard for future versions
- [ ] T-102 UI Agent: Implement player score sections (CP, Tac/Kill/Main VP)
- [ ] T-103 UI Agent: Add operation selection control for end-game bonus
- [ ] T-104 UI Agent: Add new game/reset action and confirmation flow
- [ ] T-105 UI Agent: Add save/resume controls and status feedback
- [ ] T-302 Packaging Agent: Set up buildozer.spec for Android build
- [ ] T-303 Packaging Agent: Add local storage permissions
- [ ] T-304 Packaging Agent: Verify desktop run path with UV
- [ ] T-402 QA Agent: Implement UI smoke tests for screen loading
- [ ] T-403 QA Agent: Add integration tests for save/load functionality
- [ ] T-404 QA Agent: Set up pytest automation baseline

### Task Cards

#### T-001
Task ID: T-001
Title: Review v1 requirements and assign first implementation task
Owner: Supervisor Agent
State: Done
Depends on: none
Scope:
- Confirm first implementation slice and ownership sequence.
Out of Scope:
- Feature implementation.
Acceptance Checks:
- First task card updated to Assigned with owner and acceptance checks.
- Next handoff target is explicit.
Deliverables:
- Updated task state and assignment notes in this file.
Handoff Target:
- State Agent (T-201)
Notes:
- Must enforce supervisor -> specialist -> QA -> supervisor flow.
- Assignment confirmed: next implementation task is T-201.
- Acceptance checks confirmed: task card state/owner/checks present and next handoff target explicit.
- Supervisor closeout: T-001 acceptance checks passed; T-201 assigned to State Agent.

#### T-201
Task ID: T-201
Title: Define GameState model with turn, players, scores
Owner: State Agent
State: Done
Depends on: T-001
Scope:
- Define model structure for turn, two players, and score categories.
- Define serialization contract used by save/load.
Out of Scope:
- UI rendering and file I/O adapter details.
- Build or packaging configuration changes.
Acceptance Checks:
- Model supports turn 1-4 and score fields required by PRODUCT.md.
- Unit tests cover valid and invalid state initialization.
Deliverables:
- State model code and tests.
Handoff Target:
- QA Agent (T-401)
Notes:
- Keep schema stable for downstream UI wiring.
- Assignment confirmed by Supervisor under T-001.
- Dependency lock: begin implementation after T-001 is marked Done.
- Boundary reminder: edit only state-owned files and state-focused tests.
- QA handoff result: qa-pass with Minor finding only.
- Supervisor decision: accepted per QA severity policy (Minor is non-blocking).
- Follow-up created: T-206 to track schema migration guard.

#### T-206
Task ID: T-206
Title: Add schema migration guard for future versions
Owner: State Agent
State: Done
Depends on: T-201
Scope:
- Add explicit schema_version validation and a clear error path for unsupported versions.
- Document expected behavior for version mismatch in code comments/tests.
Out of Scope:
- Full migration engine or automatic upgrade logic.
Acceptance Checks:
- Loading payloads with unsupported schema_version fails with deterministic error.
- Unit tests cover supported and unsupported schema versions.
Deliverables:
- State code update and unit tests.
Handoff Target:
- QA Agent
Notes:
- Created from T-201 QA minor risk.
- QA handoff result: qa-pass with Minor finding only.
- Supervisor decision: accepted per QA severity policy (Minor is non-blocking).
- No additional follow-up required in current V1 scope.

#### T-401
Task ID: T-401
Title: Create unit tests for state models and calculations
Owner: QA Agent
State: Backlog
Depends on: T-201
Scope:
- Add deterministic tests for GameState and core scoring behavior.
Out of Scope:
- Implementing missing feature logic in app code.
Acceptance Checks:
- Tests fail on known bad inputs and pass on valid scenarios.
- Test run command and results are included in handoff.
Deliverables:
- Unit tests under tests/.
Handoff Target:
- Supervisor Agent
Notes:
- Use severity labels if defects are found.

#### T-101
Task ID: T-101
Title: Create main game screen with turn display
Owner: UI Agent
State: Backlog
Depends on: T-201
Scope:
- Build base screen and visible turning point display.
Out of Scope:
- Scoring/business logic changes.
Acceptance Checks:
- Screen loads without runtime UI errors.
- Turn value is rendered from state interface.
Deliverables:
- UI layout/controller updates and optional smoke test.
Handoff Target:
- QA Agent (T-402)
Notes:
- Must not bypass state interfaces.

#### T-301
Task ID: T-301
Title: Configure pyproject.toml with Kivy dependencies
Owner: Packaging Agent
State: Backlog
Depends on: none
Scope:
- Add/verify runtime dependencies for desktop development path.
Out of Scope:
- App feature behavior changes.
Acceptance Checks:
- Dependency configuration is reproducible on clean environment.
- Desktop run instructions are documented and validated.
Deliverables:
- Updated pyproject.toml and packaging notes.
Handoff Target:
- QA Agent (T-404)
Notes:
- Minimize dependency footprint.

#### T-202
Task ID: T-202
Title: Implement score update methods (increment/decrement)
Owner: State Agent
State: Backlog
Depends on: T-201
Scope:
- Add bounded increment/decrement methods for score categories and CP.
Out of Scope:
- UI event wiring.
Acceptance Checks:
- Methods enforce min/max bounds from product constraints.
- Tests cover boundary conditions.
Deliverables:
- State logic and tests.
Handoff Target:
- QA Agent
Notes:
- Keep methods deterministic and side-effect limited.

#### T-203
Task ID: T-203
Title: Add operation selection and bonus calculation logic
Owner: State Agent
State: Backlog
Depends on: T-201
Scope:
- Add operation selection field and bonus computation behavior.
Out of Scope:
- Operation-specific rule engine beyond V1 scope.
Acceptance Checks:
- Bonus total is included in final score output.
- Tests cover operation selection and bonus calculations.
Deliverables:
- State logic and tests.
Handoff Target:
- QA Agent
Notes:
- Keep rules minimal and configurable.

#### T-204
Task ID: T-204
Title: Implement new game reset behavior
Owner: State Agent
State: Backlog
Depends on: T-201
Scope:
- Reset all tracked values to valid initial state.
Out of Scope:
- UI confirmation flow.
Acceptance Checks:
- Reset produces canonical initial GameState.
- Tests verify all fields reset correctly.
Deliverables:
- Reset logic and tests.
Handoff Target:
- QA Agent
Notes:
- Ensure reset does not leave stale values.

#### T-205
Task ID: T-205
Title: Add JSON serialization contracts for save/load
Owner: State Agent
State: Backlog
Depends on: T-201
Scope:
- Define stable to_json/from_json contract for GameState.
Out of Scope:
- File path or device storage policy implementation.
Acceptance Checks:
- Round-trip serialization preserves all required fields.
- Invalid payload handling is tested.
Deliverables:
- Serialization code and tests.
Handoff Target:
- QA Agent (T-403)
Notes:
- Backward-compatible key naming preferred.

#### T-102
Task ID: T-102
Title: Implement player score sections (CP, Tac/Kill/Main VP)
Owner: UI Agent
State: Backlog
Depends on: T-101, T-202
Scope:
- Add score controls/display for both players and categories.
Out of Scope:
- Score rule calculations.
Acceptance Checks:
- Controls invoke state interfaces and update visible values.
- Layout remains usable on mobile and desktop.
Deliverables:
- UI layout/controller updates.
Handoff Target:
- QA Agent (T-402)
Notes:
- Keep controls symmetric for both players.

#### T-103
Task ID: T-103
Title: Add operation selection control for end-game bonus
Owner: UI Agent
State: Backlog
Depends on: T-101, T-203
Scope:
- Add operation selector and bind to state operation field.
Out of Scope:
- Defining new operation rules.
Acceptance Checks:
- Selection persists in in-memory state for active session.
- Selected operation affects displayed totals via state outputs.
Deliverables:
- UI updates and interaction notes.
Handoff Target:
- QA Agent (T-402)
Notes:
- Include safe default selection behavior.

#### T-104
Task ID: T-104
Title: Add new game/reset action and confirmation flow
Owner: UI Agent
State: Backlog
Depends on: T-101, T-204
Scope:
- Add reset action and confirmation UX.
Out of Scope:
- Reset business logic internals.
Acceptance Checks:
- Confirmed reset calls state reset and updates screen values.
- Cancel path does not mutate state.
Deliverables:
- UI updates and interaction notes.
Handoff Target:
- QA Agent (T-402)
Notes:
- Favor low-friction confirmation UX.

#### T-105
Task ID: T-105
Title: Add save/resume controls and status feedback
Owner: UI Agent
State: Backlog
Depends on: T-101, T-205
Scope:
- Add save/resume UI actions and success/failure status messaging.
Out of Scope:
- Storage backend implementation details.
Acceptance Checks:
- Save and resume actions trigger expected state/storage interfaces.
- Failure states are surfaced clearly to user.
Deliverables:
- UI updates and interaction notes.
Handoff Target:
- QA Agent (T-403)
Notes:
- Ensure non-blocking feedback on mobile.

#### T-302
Task ID: T-302
Title: Set up buildozer.spec for Android build
Owner: Packaging Agent
State: Backlog
Depends on: T-301
Scope:
- Create/update buildozer.spec with app metadata and baseline config.
Out of Scope:
- App feature changes.
Acceptance Checks:
- Config can produce a build attempt without configuration errors.
- Required package metadata fields are set.
Deliverables:
- buildozer.spec and build notes.
Handoff Target:
- QA Agent
Notes:
- Keep config minimal for V1.

#### T-303
Task ID: T-303
Title: Add local storage permissions
Owner: Packaging Agent
State: Backlog
Depends on: T-302
Scope:
- Add only permissions needed for local save/load behavior.
Out of Scope:
- Network or cloud permissions.
Acceptance Checks:
- Permissions match persistence requirements only.
- Permission rationale documented.
Deliverables:
- buildozer.spec updates and notes.
Handoff Target:
- QA Agent
Notes:
- Apply least-privilege approach.

#### T-304
Task ID: T-304
Title: Verify desktop run path with UV
Owner: Packaging Agent
State: Backlog
Depends on: T-301
Scope:
- Validate local install/run commands on clean checkout.
Out of Scope:
- Android packaging steps.
Acceptance Checks:
- Setup command list is reproducible.
- Main app entry command starts app without missing dependency error.
Deliverables:
- Runbook notes in docs and/or handoff evidence.
Handoff Target:
- QA Agent (T-404)
Notes:
- Keep instructions concise.

#### T-402
Task ID: T-402
Title: Implement UI smoke tests for screen loading
Owner: QA Agent
State: Backlog
Depends on: T-101, T-102
Scope:
- Add smoke checks for app startup and main screen render path.
Out of Scope:
- Full UI interaction automation.
Acceptance Checks:
- Test catches startup/screen-load regressions.
- Test execution command and result are documented.
Deliverables:
- Smoke tests and QA report.
Handoff Target:
- Supervisor Agent
Notes:
- Keep tests stable and low maintenance.

#### T-403
Task ID: T-403
Title: Add integration tests for save/load functionality
Owner: QA Agent
State: Backlog
Depends on: T-205, T-105
Scope:
- Verify end-to-end state save and restore behavior.
Out of Scope:
- UI styling validation.
Acceptance Checks:
- Integration tests validate round-trip correctness.
- Error handling path is covered.
Deliverables:
- Integration tests and QA report.
Handoff Target:
- Supervisor Agent
Notes:
- Use deterministic fixtures.

#### T-404
Task ID: T-404
Title: Set up pytest automation baseline
Owner: QA Agent
State: Backlog
Depends on: T-301
Scope:
- Define baseline pytest commands and minimal CI-ready expectations.
Out of Scope:
- Introducing heavy new tooling.
Acceptance Checks:
- Default test command is documented and runnable.
- Failing tests return non-zero exit status in automation context.
Deliverables:
- QA tooling/config notes and optional config updates.
Handoff Target:
- Supervisor Agent
Notes:
- Keep setup lightweight.

## Completed Tasks

- [x] Create initial repository scaffold
- [x] Define multi-agent workflow structure
- [x] Document agent responsibilities
- [x] Specify v1 score-tracking requirements
- [x] Implement git branch protection hooks

## Task Format

For each active task, track:
- Task ID
- Title
- Owner (one active owner)
- State (from legend)
- Depends on (optional)
- Acceptance checks
- Handoff link/reference

## Branch Workflow

When working on tasks:
1. Create feature branch: `git checkout -b agent/[type]-[task]`
2. Make changes and commit to branch
3. Create PR for supervisor review
4. Supervisor reviews and merges to main