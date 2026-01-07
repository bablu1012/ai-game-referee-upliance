
# Rock–Paper–Scissors–Plus Game Referee

**Assignment Submission – AI Product Engineer (Conversational Agents)**  
**Company: upliance.ai**  
**Author: Mohammed Bilal M**

---

## Overview

This project implements a minimal chatbot that acts as a referee for a short game of Rock–Paper–Scissors–Plus. The referee manages a best-of-3 match between the user and the bot, validates every move, tracks the score across turns, and ends the game automatically after three rounds. The implementation was intentionally kept simple to highlight logical correctness and clear agent design.

---

## Architecture

The solution is organized into three clearly separated parts:

1. **Intent Understanding**  
   User input from the CLI is normalized and interpreted through the validation function to understand what the player attempted to do.

2. **Game Logic (Pure Functions)**  
   - `determine_winner()` implements the fixed game outcome rules.  
   - `choose_bot_move()` implements the opponent strategy.  
   These functions have no side effects and can be tested independently.

3. **State Mutation (Tool Functions)**  
   - `validate_move()` – checks valid moves and bomb-once constraint.  
   - `resolve_round()` – decides the winner deterministically.  
   - `update_game_state()` – performs all updates to the game state and history.  
   Centralizing mutation ensured that the state is never kept only inside prompts.

---

## State Model

The game state is stored as an in-memory dictionary and tracks:

- Current round number (1–3)  
- User score and bot score  
- Bomb usage flags for both players  
- Move history for auditing  
- Game termination flag

### Why this model

- A single source of truth prevents state drift  
- Flags enforce business constraints  
- History enables debugging and future UX features

---

## Key Design Decisions

- **Invalid Input Handling:**  
  Any move outside the allowed set wastes the round but the loop continues safely.

- **Bomb Restriction:**  
  The special bomb move can be used only once per player per game.

- **Termination:**  
  The game ends automatically after exactly 3 rounds.

- **Delivery Format:**  
  A single Python file was used for easy reviewer evaluation.

---

## Tradeoffs Made

| Area | Pros | Cons |
|-----|-----|-----|
| Global in-memory state | Simple and clear | Not concurrent-safe |
| Random opponent AI | Fast implementation | Not optimal strategy |
| CLI interface | Minimal setup | No rich UI |
| Single file | Easy review | Less modular |

---

## What I Would Improve With More Time

- Fuzzy parsing for natural sentences  
- Typed schemas for responses  
- Unit tests for all edge cases  
- Session-scoped state for concurrency  
- Observability logs  
- Difficulty levels for opponent

---

## Requirements Checklist

| Requirement | Status |
|-------------|--------|
| Best of 3 rounds | ✅ |
| Valid moves | ✅ |
| Bomb beats all | ✅ |
| Bomb once per player | ✅ |
| Invalid wastes round | ✅ |
| Auto-end after 3 rounds | ✅ |
| Explicit tools defined | ✅ |
| State not only in prompt | ✅ |
| Separation of layers | ✅ |
| Final result shown | ✅ |

---

## Conclusion

This assignment reflects my approach to applied AI systems: by thinking through rules and constraints first, encoding them in predictable logic, and ensuring that users never encounter dead ends. The same reasoning style is suitable for real-world conversational agents such as smart cooking companions.

