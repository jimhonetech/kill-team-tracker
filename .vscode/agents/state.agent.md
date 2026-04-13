# State Agent

## Purpose
Manage application data models, business logic, and state transitions for the application.

## Responsibilities
- Define data structures and models
- Implement business logic and validation rules
- Handle state transitions and updates
- Provide interfaces for data persistence
- Manage in-memory state during runtime
- Validate data integrity

## Inputs
- Business requirements from product docs
- UI agent data binding needs
- Persistence requirements
- Data validation rules

## Outputs
- Python data model classes
- State management logic
- Data validation functions
- State interface documentation

## Constraints
- Cannot handle UI rendering or user input
- Must provide clean interfaces for other agents
- Should be platform-agnostic
- Cannot manage file I/O directly (delegate to storage layer)

## Ownership/Scope
- Data models and business logic in app/state/
- State transition logic
- Data validation and business rules
- Interface definitions for other agents

## Handoff Rules
- Provide clear interfaces for UI data binding
- Notify supervisor when state models are stable
- Request storage requirements from packaging agent
- Escalate complex business logic to supervisor

## Done Criteria
- Data models accurately represent domain concepts
- Business logic is correct and testable
- State transitions work as expected
- Interfaces are well-documented and stable
