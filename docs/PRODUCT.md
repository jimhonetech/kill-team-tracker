# Product Vision: Kill Team Tracker

## Overview

Kill Team Tracker is a mobile app for Warhammer 40k Kill Team players to track essential game scores during matches. Version 1 focuses on core score tracking without implementing full game rules.

## V1 Core Features

- **Turn Tracking**: Display current turning point (1-5)
- **Command Points**: Track each player's command points (0-6)
- **Victory Points**:
  - Tactical Objective VP (0-15 per player)
  - Kill Objective VP (0-15 per player)
  - Main Mission VP (0-15 per player)
- **End-Game Bonus**: Select one operation for bonus scoring, track associated bonus points
- **Game Management**:
  - Start new game (reset all scores)
  - Save current game state locally
  - Resume saved game

## Target Platform

- Android (primary via Buildozer)
- Desktop (for development and testing)

## User Stories

- As a player, I want to see the current turn number clearly
- As a player, I want to increment/decrement command points for each player
- As a player, I want to update VP totals for each category
- As a player, I want to select which operation to use for end-game bonus
- As a player, I want to calculate and display total scores including bonuses
- As a player, I want to start a new game with zeroed scores
- As a player, I want to save my game progress and resume later

## Technical Requirements

- Built with Kivy for cross-platform UI
- Local JSON storage for game state (no cloud)
- Offline operation
- Simple, mobile-optimized interface
- UV for Python dependency management