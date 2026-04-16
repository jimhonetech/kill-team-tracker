# Product Vision: Kill Team Tracker

## Overview

Kill Team Tracker is a mobile app for Warhammer 40k Kill Team players to track essential game scores during matches. Version 1 focuses on core score tracking without implementing full game rules.

## V1 Core Features

- **Turn Tracking**: Display current turning point (1-4)
- **Command Points**: Track each player's command points (0-6)
- **Victory Points** (three scoring buckets):
  - Crit Op VP (0-6 per player) — shared mission objective
  - Kill Op VP (0-6 per player) — points for kills
  - Tac Op VP (0-6 per player) — chosen secret objective
- **End-Game Flow**:
  - Before the game, each player privately chooses one Primary Op (Crit / Kill / Tac)
  - Play the full 4 turning points
  - At end (TP 4), reveal chosen Primary Op in the app
  - Automatically calculate bonus: **+50% of Primary Op score (rounded up)**
- **Game Management**:
  - Start new game (reset all scores)
  - Finish a game and optionally keep final scores for future stats/history

## V3 UX Expansion (Planned)

To reduce clutter and improve usability, V3 introduces a guided multi-screen flow.

### Planned Screen Flow

1. **Home Screen**
- Primary CTA: Start Game
- Stats button is intentionally deferred to a later milestone

2. **Team Selection Screen**
- Player 1 selects a Kill Team from a list
- Player 2 selects a Kill Team from a list
- Confirm Teams action advances to gameplay

3. **Gameplay Screen (Turning Point 1-4)**
- Dedicated tracking for each player:
  - Command Points
  - Tac Op VP
  - Kill Op VP
  - Crit Op VP
- Turning point controls remain available
- End Game action available from TP4 with accidental-tap recovery (back path)

4. **End-Game Primary Op Screen**
- Each player selects revealed Primary Op (Tac Op / Kill Op / Crit Op)
- Continue action advances to final scoring

5. **Final Score Screen**
- Display totals including automatic bonus
- Offer Save Final Scores and Discard Game actions
- Allow back navigation to correct accidental end-game progression

### Navigation and Safety Requirements

- Users must be able to navigate back between post-start screens before finalizing outcomes.
- If End Game is triggered accidentally, users can return to gameplay without losing tracked values.
- Save Final Scores/Discard confirmation should be explicit on the final score screen.

## Scoring Rules

### Setup
Before the match starts, each player privately chooses ONE of three operations as their **Primary Op**:
- Crit Op (shared mission objective)
- Kill Op (points for kills)
- Tac Op (chosen secret objective)

### During Match
Track VP earned in all three categories normally:
- Each category: 0–6 VP max
- Command Points: 0–6 (tracked separately)

### End-Game Bonus
At the end of the match:
1. Reveal your chosen Primary Op
2. Calculate bonus: **Bonus VP = ceil(Primary Op VP / 2)**
3. Rounding rule: Always round UP (e.g., 5 VP → +3 bonus, 1 VP → +1 bonus)

### Scoring Examples
| Primary Op Selection | Op Score | Bonus (ceil/2) | Total from Op |
|---|---|---|---|
| Crit Op | 4 VP | 2 | 6 VP |
| Kill Op | 5 VP | 3 | 8 VP |
| Tac Op | 6 VP | 3 | 9 VP |
| Any Op | 1 VP | 1 | 2 VP |

### Final Score Calculation
```
Total VP = Crit Op + Kill Op + Tac Op + Primary Op Bonus + Command Points Bonus (if applicable)
Maximum possible: 6 + 6 + 6 + 3 = 21 VP (from VP categories alone)
```

## Target Platform

- Android (primary via Buildozer)
- Desktop (for development and testing)

## User Stories

- As a player, I want to see the current turn number clearly
- As a player, I want to increment/decrement command points for each player
- As a player, I want to update VP totals for each category (Crit / Kill / Tac Op)
- As a player, I want to secretly select my Primary Op at match start
- As a player, I want to reveal my Primary Op at the end of the game
- As a player, I want the app to automatically calculate my end-game bonus (50% of Primary Op score, rounded up)
- As a player, I want to see my total score including the end-game bonus
- As a player, I want to start a new game with zeroed scores
- As a player, I want a cleaner multi-screen flow so scoring is less cluttered
- As a player, I want to select each player's Kill Team before turning point tracking begins
- As a player, I want to go back if I tap end-game by accident
- As a player, I want to save final scores into a future stats/history pool or discard them at the final score step

## Deferred Items

- Stats dashboard button and stats screen (deferred from V3 to a later milestone)

## V4 Stats/History MVP

The next version focuses on turning completed games into a reusable local stats pool.

### Match History Requirements

- When a game is finalized from the Final Score screen and the user chooses Save Final Scores, the app should archive that completed match into local history.
- The archive must preserve full per-game scoring details so future stats can be computed without data loss.
- Stored match data should include, at minimum:
  - Both selected teams
  - Both players' score buckets: Command Points, Tac Op VP, Kill Op VP, Crit Op VP, Bonus VP
  - Revealed Primary Op / secret-op selection for each player
  - Final totals / winner or draw outcome
  - Enough metadata to support future expansion, such as archive timestamp and schema version
- Active-game save/resume remains separate from completed-match history.

### Initial Stats Screen MVP

- Enable the Stats entrypoint from Home.
- Provide an initial win-percentage-focused stats view.
- Show:
  - Player 1 win percentage
  - Player 2 win percentage
  - Team win percentage overall
  - Team win percentage when played as Player 1
  - Team win percentage when played as Player 2
- Handle empty history clearly.

### Non-Goals For This MVP

- Advanced charts or deep analytics
- Editing or deleting archived matches
- Cloud sync or remote storage
- Additional derived stats such as average VP, primary-op pick rates, or matchup tables

## Technical Requirements

- Built with Kivy for cross-platform UI
- Local JSON storage for game state (no cloud)
- Offline operation
- Simple, mobile-optimized interface
- UV for Python dependency management
