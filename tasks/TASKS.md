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
- [x] T-401 QA Agent: Create unit tests for state models and calculations
- [x] T-101 UI Agent: Create main game screen with turn display
- [x] T-301 Packaging Agent: Configure pyproject.toml with Kivy dependencies
- [x] T-202 State Agent: Implement score update methods (increment/decrement)
- [x] T-203 State Agent: Add operation selection and bonus calculation logic
- [x] T-204 State Agent: Implement new game reset behavior
- [x] T-205 State Agent: Add JSON serialization contracts for save/load
- [x] T-206 State Agent: Add schema migration guard for future versions
- [x] T-102 UI Agent: Implement player score sections (CP, Tac/Kill/Main VP)
- [x] T-103 UI Agent: Add operation selection control for end-game bonus
- [x] T-104 UI Agent: Add new game/reset action and confirmation flow
- [x] T-105 UI Agent: Add save/resume controls and status feedback
- [x] T-302 Packaging Agent: Set up buildozer.spec for Android build
- [x] T-303 Packaging Agent: Add local storage permissions
- [x] T-304 Packaging Agent: Verify desktop run path with UV
- [x] T-402 QA Agent: Implement UI smoke tests for screen loading
- [x] T-403 QA Agent: Add integration tests for save/load functionality
- [x] T-404 QA Agent: Set up pytest automation baseline
- [x] T-405 QA Agent: Fix pre-commit mypy hook dependency resolution in CI

## V2 Milestone — Android Phone Testing

- [~] T-502 Packaging Agent: Install JDK and produce a debug APK with Buildozer
- [ ] T-503 Packaging Agent: Sideload and smoke-test APK on a real Android device
- [x] T-501 State Agent: Implement file-backed storage adapter (real JSON persistence)
- [x] T-504 UI Agent: Wire save/resume buttons to storage adapter
- [x] T-505 QA Agent: Add end-to-end persistence tests using real file I/O
- [~] T-506 Supervisor: V2 review — accept Android + persistence delivery

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
State: Done
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
- QA handoff result: qa-pass with no findings.
- Supervisor decision: accepted per QA severity policy.
- Acceptance verified: existing deterministic unit tests in `tests/test_game_state.py` cover valid initialization, invalid inputs, bounds, serialization, reset behavior, operation selection, and scoring calculations.
- Evidence: `uv run pytest tests/test_game_state.py -q` (19 passed), `uv run pre-commit run --all-files` (passed), `uv run pytest` (35 passed).

#### T-101
Task ID: T-101
Title: Create main game screen with turn display
Owner: UI Agent
State: Done
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
- QA handoff result: qa-fail with Major finding.
- Blocker: Kivy is missing in QA environment, so runtime UI load check could not be verified.
- Unblock task assigned: T-301 (Packaging Agent).
- Supervisor update: blocker resolved by T-301 qa-pass; T-101 re-opened for QA runtime screen-load revalidation.
- QA revalidation result: qa-pass.
- Supervisor decision: accepted per QA severity policy.
- Minor non-blocking warning recorded: /dev/input/event5 permission warning observed on Linux host during startup.

#### T-301
Task ID: T-301
Title: Configure pyproject.toml with Kivy dependencies
Owner: Packaging Agent
State: Done
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
- Assigned as unblock task for T-101 runtime UI validation.
- Packaging execution complete; awaiting QA validation.
- QA handoff result: qa-pass with Minor finding only.
- Supervisor decision: accepted; dependency/setup path validated for T-101 revalidation.

#### T-202
Task ID: T-202
Title: Implement score update methods (increment/decrement)
Owner: State Agent
State: Done
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
- Assigned by Supervisor as the next implementation task after T-101 acceptance.
- QA handoff result: qa-pass with Minor finding only.
- Supervisor decision: accepted per QA severity policy (Minor is non-blocking).

#### T-203
Task ID: T-203
Title: Add operation selection and bonus calculation logic
Owner: State Agent
State: Done
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
- QA handoff result: qa-pass with Minor finding only.
- Supervisor decision: accepted per QA severity policy (Minor is non-blocking).
- Acceptance verified: final score outputs include bonus points and tests cover operation selection plus bonus behavior.

#### T-204
Task ID: T-204
Title: Implement new game reset behavior
Owner: State Agent
State: Done
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
- QA handoff result: qa-pass with Minor finding only.
- Supervisor decision: accepted per QA severity policy (Minor is non-blocking).
- Acceptance verified: reset returns canonical initial GameState and tests verify all tracked fields reset.

#### T-205
Task ID: T-205
Title: Add JSON serialization contracts for save/load
Owner: State Agent
State: Done
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
- QA handoff result: qa-pass with Minor finding only.
- Supervisor decision: accepted per QA severity policy (Minor is non-blocking).
- Acceptance verified: round-trip serialization preserved all required fields and invalid payload handling is covered by deterministic tests.

#### T-102
Task ID: T-102
Title: Implement player score sections (CP, Tac/Kill/Main VP)
Owner: UI Agent
State: Done
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
- QA handoff result: qa-pass with Minor finding only.
- Supervisor decision: accepted per QA severity policy (Minor is non-blocking).
- Acceptance verified: controls update state interfaces and rendered values for both players and all required score categories.

#### T-103
Task ID: T-103
Title: Add operation selection control for end-game bonus
Owner: UI Agent
State: Done
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
- QA handoff result: qa-pass with Minor finding only.
- Supervisor decision: accepted per QA severity policy (Minor is non-blocking).
- Acceptance verified: selected operation persists in state and displayed totals update via state final score outputs when bonus is adjusted.

#### T-104
Task ID: T-104
Title: Add new game/reset action and confirmation flow
Owner: UI Agent
State: Done
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
- QA handoff result: qa-pass with Minor finding only.
- Supervisor decision: accepted per QA severity policy (Minor is non-blocking).
- Acceptance verified: confirmed reset triggers state reset and updates displayed values; cancel path leaves state unchanged.

#### T-105
Task ID: T-105
Title: Add save/resume controls and status feedback
Owner: UI Agent
State: Done
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
- QA handoff result: qa-pass with Minor finding only.
- Supervisor decision: accepted per QA severity policy (Minor is non-blocking).
- Acceptance verified: save/resume actions trigger storage interface callbacks and failure messages are surfaced in UI status feedback.

#### T-302
Task ID: T-302
Title: Set up buildozer.spec for Android build
Owner: Packaging Agent
State: Done
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
- QA handoff result: qa-pass with Minor finding only.
- Minor finding: Android host prerequisites are not installed locally, so validation stops at `javac` discovery after config parsing succeeds.
- Supervisor decision: accepted per QA severity policy (Minor is non-blocking).
- Acceptance verified: `buildozer.spec` now sets required app metadata and Buildozer reaches host prerequisite checks without configuration-token errors.
- Verified commands:
- `uv run --with buildozer buildozer init`
- `uv run --with buildozer --with setuptools --with cython buildozer -v android debug`
- `uv run pre-commit run --all-files`
- Evidence: Buildozer accepted the spec, created build layout directories, found `git` and `cython`, and then stopped on missing `javac` rather than configuration errors.

#### T-303
Task ID: T-303
Title: Add local storage permissions
Owner: Packaging Agent
State: Done
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
- QA handoff result: qa-pass with Minor finding only.
- Minor finding: Android save/resume adapter is not implemented yet, so permission rationale is based on the current V1 private-storage architecture rather than a concrete runtime adapter.
- Supervisor decision: accepted per QA severity policy (Minor is non-blocking).
- Acceptance verified: no `android.permissions` entry was added because V1 local JSON save/resume can use `android.private_storage = True` without requesting external storage or network permissions.
- Permission rationale documented directly in `buildozer.spec` next to `android.private_storage = True`.
- Evidence: `uv run pre-commit run --all-files` passed and the Buildozer spec remains valid for the Android debug attempt.

#### T-304
Task ID: T-304
Title: Verify desktop run path with UV
Owner: Packaging Agent
State: Done
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
- QA handoff result: qa-pass with Minor finding only.
- Minor finding: Kivy emits verbose runtime logs during dependency verification, but setup and app initialization succeed.
- Supervisor decision: accepted per QA severity policy (Minor is non-blocking).
- Acceptance verified: reproducible setup commands succeed locally and the app initialization path runs without missing dependency errors.
- Reproducible commands confirmed:
- `uv sync --dev`
- `uv run python -c "import kivy; print(kivy.__version__)"`
- `uv run python -c "from app.state import GameState; from app.ui.main_screen import MainGameScreen; screen = MainGameScreen(GameState()); print(screen.turning_point_label.text)"`
- Evidence: `uv run pre-commit run --all-files` passed; Kivy import reported `2.3.1`; app initialization printed `Turning Point 1`.

#### T-402
Task ID: T-402
Title: Implement UI smoke tests for screen loading
Owner: QA Agent
State: Done
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
- QA handoff result: qa-pass with Minor finding only.
- Minor finding: `app.main` missing-Kivy fallback branch remains untested in pytest and is outside the primary happy-path smoke scope.
- Supervisor decision: accepted per QA severity policy (Minor is non-blocking).
- Acceptance verified: smoke tests cover direct main-screen rendering and app startup builds the main screen when the Kivy run loop is stubbed.
- Evidence: `uv run pytest tests/test_ui_smoke.py -q` (2 passed), `uv run flake8 tests/test_ui_smoke.py` (passed), `uv run pytest` (35 passed).

#### T-403
Task ID: T-403
Title: Add integration tests for save/load functionality
Owner: QA Agent
State: Done
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
- QA handoff result: qa-pass with Minor finding only.
- Minor finding: `app/main.py` runtime bootstrap path remains untested in pytest coverage and is outside T-403 scope.
- Supervisor decision: accepted per QA severity policy (Minor is non-blocking).
- Acceptance verified: integration tests cover save/load round-trip correctness and corrupted resume payload error handling.
- Evidence: `uv run pytest tests/test_save_load_integration.py` (2 passed), `uv run pytest` (31 passed).

#### T-404
Task ID: T-404
Title: Set up pytest automation baseline
Owner: QA Agent
State: Done
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
- QA handoff result: qa-pass with Minor finding only.
- Minor finding: targeted automation baseline test emits a coverage `no-data-collected` warning because it validates pytest subprocess exit codes without importing app modules.
- Supervisor decision: accepted per QA severity policy (Minor is non-blocking).
- Acceptance verified: default `uv run pytest` command is documented in `docs/DEVELOPMENT.md` and deterministic tests verify both zero and non-zero pytest exit-code behavior.
- Evidence: `uv run pytest tests/test_pytest_automation_baseline.py -q` (2 passed), `uv run flake8 tests/test_pytest_automation_baseline.py` (passed), `uv run pytest` (33 passed).

#### T-405
Task ID: T-405
Title: Fix pre-commit mypy hook dependency resolution in CI
Owner: QA Agent
State: Done
Depends on: T-404
Scope:
- Update mypy pre-commit hook configuration to avoid failing `types-all` dependency resolution.
- Keep type-checking behavior practical for this repository.
- Confirmed CI failure scope: mypy hook environment install fails on `types-all` due to missing `types-pkg-resources`.
Out of Scope:
- Refactoring application feature code.
- Introducing heavy new CI tooling.
Acceptance Checks:
- `pre-commit` installs mypy hook environment without dependency resolution errors.
- `uv run pre-commit run mypy --all-files` executes successfully in CI-equivalent environment.
Deliverables:
- Updated `.pre-commit-config.yaml` and any minimal related QA tooling notes.
Handoff Target:
- Supervisor Agent
Notes:
- Triggered by CI failure: `No matching distribution found for types-pkg-resources` from `types-all`.
- Supervisor handoff: QA Agent to apply tooling-only fix in `.pre-commit-config.yaml` and validate with `uv run pre-commit run mypy --all-files`.
- QA handoff result: qa-pass with Minor finding only.
- Supervisor decision: accepted per QA severity policy (Minor is non-blocking).
- CI-equivalent validation command now passes: `uv run pre-commit run mypy --all-files`.

---

#### T-502
Task ID: T-502
Title: Install JDK and produce a debug APK with Buildozer
Owner: Packaging Agent
State: Assigned
Depends on: T-302, T-303
Scope:
- Install openjdk-17-jdk (provides javac required by Buildozer)
- Run `uv run --with buildozer --with setuptools --with cython buildozer android debug`
- Confirm APK produced at bin/killteamtracker-0.1.0-debug.apk
- Document any additional host prerequisites discovered
Out of Scope:
- Signing or release builds
- App feature changes
Acceptance Checks:
- `bin/killteamtracker-0.1.0-debug.apk` exists and is a valid ZIP/APK
- `uv run pre-commit run --all-files` passes
- Build command and prerequisites documented in Notes
Deliverables:
- Produced APK file
- Notes on full prerequisite list
Handoff Target:
- QA Agent (T-503)

#### T-503
Task ID: T-503
Title: Sideload and smoke-test APK on a real Android device
Owner: Packaging Agent
State: Backlog
Depends on: T-502
Scope:
- Provide instructions for sideloading APK to an Android phone
- Verify app launches and main screen is visible on device
- Note any crashes, layout issues, or missing UI elements
Out of Scope:
- Bug fixes (report only — fixes go to UI/State agents)
- Release/Play Store publishing
Acceptance Checks:
- App installs without error on Android
- Main game screen renders and buttons are tappable
- Findings documented in Notes
Deliverables:
- Sideload instructions
- Device test results in Notes
Handoff Target:
- Supervisor (T-506)

#### T-501
Task ID: T-501
Title: Implement file-backed storage adapter (real JSON persistence)
Owner: State Agent
State: Assigned
Depends on: T-205
Scope:
- Create `app/storage/` module with a `StorageAdapter` that reads/writes JSON to a local file path
- Adapter must implement the same save/load interface already used by `MainGameScreen`
- Use `pathlib.Path` for cross-platform paths; on Android, use `App.user_data_dir`
Out of Scope:
- Cloud or network storage
- UI changes
Acceptance Checks:
- `app/storage/adapter.py` exists and implements save/load interface
- `uv run pytest` passes (all existing tests green + new adapter tests)
- `uv run pre-commit run --all-files` passes
Deliverables:
- `app/storage/adapter.py` with unit tests
Handoff Target:
- QA Agent (T-505), then UI Agent (T-504)

#### T-504
Task ID: T-504
Title: Wire save/resume buttons to storage adapter
Owner: UI Agent
State: Backlog
Depends on: T-501
Scope:
- Pass a `StorageAdapter` instance into `MainGameScreen` as `save_handler`/`resume_handler`
- Update `app/main.py` to instantiate adapter and wire it in at startup
Out of Scope:
- Storage adapter implementation
- UI redesign
Acceptance Checks:
- Tapping Save writes a file; tapping Resume reads it back and restores state
- `uv run pytest` passes
- `uv run pre-commit run --all-files` passes
Deliverables:
- Updated `app/main.py` and any needed `MainGameScreen` changes
Handoff Target:
- QA Agent (T-505)

#### T-505
Task ID: T-505
Title: Add end-to-end persistence tests using real file I/O
Owner: QA Agent
State: Backlog
Depends on: T-501, T-504
Scope:
- Write tests that call save/resume through the real `StorageAdapter` using a `tmp_path` fixture
- Verify round-trip restores correct state
- Verify corrupt-file error path surfaces user-facing message
Out of Scope:
- Android-specific file path testing (covered by T-503)
Acceptance Checks:
- At least 2 new E2E tests covering happy path and error path
- `uv run pytest` passes
- `uv run pre-commit run --all-files` passes
Deliverables:
- New test file(s) under `tests/`
Handoff Target:
- Supervisor (T-506)

#### T-506
Task ID: T-506
Title: V2 review — accept Android and persistence delivery
Owner: Supervisor Agent
State: Backlog
Depends on: T-503, T-505
Scope:
- Accept or reject T-503 and T-505 evidence
- Update queue statuses
- Identify any V3 follow-up items
Out of Scope:
- Feature implementation
Acceptance Checks:
- All V2 tasks are Done or carry documented deferrals
- Next milestone or close-out decision is recorded
Deliverables:
- Updated TASKS.md
Handoff Target:
- None (milestone close) or next specialist per V3 scope

---

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
