# ai-game-referee-upliance
# Rock–Paper–Scissors–Plus Game Referee

**Assignment Submission – AI Product Engineer (Conversational Agents)**  
**Company: upliance.ai**

---

## Overview

This project implements a minimal chatbot that acts as a referee for a best-of-three game of Rock–Paper–Scissors–Plus. The solution was built to demonstrate how I design reliable agents with clear logic, persistent state, and intelligent responses in a simple conversational loop.

---

## Architecture

The design follows three responsibilities:

### 1. Intent Understanding
The agent interprets what the user was trying to do and decides when a tool should be called.

### 2. Game Logic
Pure functions contain the fixed rules that determine the winner of each round.

### 3. State Mutation
All updates to rounds and scores happen through explicitly defined ADK tools.  
This prevents keeping state only inside prompts and mirrors real product agents that must enforce constraints.

---

## State Model

The central state tracks:

- Current round number from 1 to 3  
- User and bot scores  
- Bomb-once restriction flags  
- Move history for audit  
- Game termination flag

The state is kept as an in-memory model as allowed by requirements.

---

## Tool Design

Three tools were created:

- **validate_and_process_move** – validates input and bomb restrictions  
- **get_game_state** – reads state without side effects  
- **reset_game** – prepares new match

Error handling ensures invalid inputs only waste rounds and never crash.

---

## Key Decisions

- Users never reach dead ends  
- Tool granularity kept atomic  
- Bot strategy kept lightweight  
- Single file delivery for easy review

---

## Tradeoffs

| Decision | Pros | Cons | Reason |
|---------|------|------|-------|
| Global state | Simple, clear | Not thread-safe | Assignment scope |
| Random opponent | Fast | Not optimal | Focus on referee |
| CLI interface | Minimal | No rich UI | Allowed |
| Single file | Easy review | Less modular | Simpler deliverable |

---

## Improvements Planned

If more time were available:

1. Better parsing for natural sentences  
2. Typed schemas for tool responses  
3. Unit tests for bomb cases  
4. Session-scoped state  
5. Observability logs  
6. Difficulty levels

---

## Requirements Checklist

| Requirement | Status |
|-------------|--------|
| Best of 3 rounds | ✅ |
| Valid moves | ✅ |
| Bomb beats all | ✅ |
| Bomb once per player | ✅ |
| Invalid wastes round | ✅ |
| Auto end after 3 rounds | ✅ |
| Google ADK usage | ✅ |
| Explicit tools | ✅ |
| State not in prompt | ✅ |
| Separation of layers | ✅ |
| Rules explained ≤5 lines | ✅ |
| Final result | ✅ |

---

## Closing

This assignment reflects my approach to applied AI: thinking through constraints and user intent first, then expressing them in simple engineering logic suitable for production agents.
