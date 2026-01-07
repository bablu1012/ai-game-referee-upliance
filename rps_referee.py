"""
Rock-Paper-Scissors-Plus Game Referee
An AI-powered game referee using Google ADK

Author: [Your Name]
Assignment: AI Product Engineer (Conversational Agents)
Company: upliance.ai
"""

from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from typing import Literal, Optional
import random
import os

# =============================================================================
# STATE MODEL
# =============================================================================

class GameState(BaseModel):
    """
    Central game state - single source of truth for all game data.
    Using Pydantic for type safety and validation.
    """
    rounds_played: int = Field(default=0, ge=0, le=3, description="Number of rounds completed (0-3)")
    user_score: int = Field(default=0, ge=0, description="User's win count")
    bot_score: int = Field(default=0, ge=0, description="Bot's win count")
    user_bomb_used: bool = Field(default=False, description="Whether user has used their bomb")
    bot_bomb_used: bool = Field(default=False, description="Whether bot has used their bomb")
    game_over: bool = Field(default=False, description="Game termination flag")
    last_user_move: Optional[str] = Field(default=None, description="User's last move (audit trail)")
    last_bot_move: Optional[str] = Field(default=None, description="Bot's last move (audit trail)")
    last_round_result: Optional[str] = Field(default=None, description="Last round outcome")

# Global state instance (simulates persistence without database)
game_state = GameState()

# =============================================================================
# GAME LOGIC LAYER - Pure Functions (No Side Effects)
# =============================================================================

def determine_winner(user_move: str, bot_move: str) -> Literal['user', 'bot', 'draw']:
    """
    Core game logic: determines round winner based on moves.
    Pure function - no side effects, fully testable.
    
    Args:
        user_move: User's move ('rock', 'paper', 'scissors', 'bomb')
        bot_move: Bot's move ('rock', 'paper', 'scissors', 'bomb')
    
    Returns:
        'user', 'bot', or 'draw'
    """
    # Special case: Bomb logic
    if user_move == 'bomb' and bot_move == 'bomb':
        return 'draw'
    if user_move == 'bomb':
        return 'user'
    if bot_move == 'bomb':
        return 'bot'
    
    # Draw case
    if user_move == bot_move:
        return 'draw'
    
    # Standard Rock-Paper-Scissors rules
    win_conditions = {
        'rock': 'scissors',      # rock crushes scissors
        'paper': 'rock',         # paper covers rock
        'scissors': 'paper'      # scissors cuts paper
    }
    
    if win_conditions.get(user_move) == bot_move:
        return 'user'
    return 'bot'

def get_bot_move(bot_bomb_available: bool, rounds_played: int) -> str:
    """
    Bot decision logic with strategic considerations.
    
    Args:
        bot_bomb_available: Whether bot still has bomb
        rounds_played: Current round number (0-2)
    
    Returns:
        Bot's chosen move
    """
    moves = ['rock', 'paper', 'scissors']
    
    # Strategic bomb usage: higher probability in later rounds
    if bot_bomb_available:
        # 15% in round 1, 25% in round 2, 30% in round 3
        bomb_probability = 0.15 + (rounds_played * 0.075)
        if random.random() < bomb_probability:
            return 'bomb'
    
    return random.choice(moves)

# =============================================================================
# ADK TOOLS - State Mutation & Validation Layer
# =============================================================================

def validate_and_process_move(user_input: str) -> dict:
    """
    PRIMARY TOOL: Validates user input and processes the complete round.
    This is the main state mutation point - all game state changes happen here.
    
    Handles:
    - Input validation (format, valid moves)
    - Bomb restriction enforcement
    - Round execution (bot move, winner determination)
    - Score updates
    - Game termination logic
    
    Args:
        user_input: Raw user input string
    
    Returns:
        Dict with validation result and complete round outcome
    """
    global game_state
    
    # Normalize input
    user_input = user_input.lower().strip()
    
    # Guard: Check if game is already over
    if game_state.game_over:
        return {
            "valid": False,
            "error": "Game is already over. Please start a new game.",
            "final_score": {
                "user": game_state.user_score,
                "bot": game_state.bot_score
            }
        }
    
    # Validation: Check if input is a valid move
    valid_moves = ['rock', 'paper', 'scissors', 'bomb']
    
    if user_input not in valid_moves:
        # Invalid input WASTES the round (per requirements)
        game_state.rounds_played += 1
        
        result = {
            "valid": False,
            "error": f"Invalid move '{user_input}'. Valid moves are: rock, paper, scissors, bomb.",
            "round_wasted": True,
            "rounds_played": game_state.rounds_played,
            "rounds_remaining": 3 - game_state.rounds_played
        }
        
        # Check if this wasted round ends the game
        if game_state.rounds_played >= 3:
            game_state.game_over = True
            result["game_over"] = True
            result["final_score"] = {
                "user": game_state.user_score,
                "bot": game_state.bot_score
            }
        
        return result
    
    # Validation: Check bomb usage restriction
    if user_input == 'bomb' and game_state.user_bomb_used:
        # Attempting to reuse bomb WASTES the round
        game_state.rounds_played += 1
        
        result = {
            "valid": False,
            "error": "You've already used your bomb! This round is wasted.",
            "round_wasted": True,
            "rounds_played": game_state.rounds_played,
            "rounds_remaining": 3 - game_state.rounds_played
        }
        
        if game_state.rounds_played >= 3:
            game_state.game_over = True
            result["game_over"] = True
            result["final_score"] = {
                "user": game_state.user_score,
                "bot": game_state.bot_score
            }
        
        return result
    
    # === VALID MOVE: Process the round ===
    
    user_move = user_input
    bot_move = get_bot_move(not game_state.bot_bomb_used, game_state.rounds_played)
    
    # Update bomb usage flags
    if user_move == 'bomb':
        game_state.user_bomb_used = True
    if bot_move == 'bomb':
        game_state.bot_bomb_used = True
    
    # Determine round winner
    winner = determine_winner(user_move, bot_move)
    
    # Update scores
    if winner == 'user':
        game_state.user_score += 1
    elif winner == 'bot':
        game_state.bot_score += 1
    
    # Update audit trail
    game_state.last_user_move = user_move
    game_state.last_bot_move = bot_move
    game_state.last_round_result = winner
    
    # Increment round counter
    game_state.rounds_played += 1
    
    # Check game termination
    if game_state.rounds_played >= 3:
        game_state.game_over = True
    
    # Return comprehensive round result
    return {
        "valid": True,
        "round_number": game_state.rounds_played,
        "user_move": user_move,
        "bot_move": bot_move,
        "round_winner": winner,
        "user_score": game_state.user_score,
        "bot_score": game_state.bot_score,
        "rounds_remaining": 3 - game_state.rounds_played,
        "game_over": game_state.game_over,
        "user_bomb_available": not game_state.user_bomb_used,
        "final_score": {
            "user": game_state.user_score,
            "bot": game_state.bot_score
        } if game_state.game_over else None
    }

def get_game_state() -> dict:
    """
    QUERY TOOL: Returns current game state (read-only).
    Useful for agent to check game status without modifying state.
    """
    return {
        "rounds_played": game_state.rounds_played,
        "rounds_remaining": 3 - game_state.rounds_played,
        "user_score": game_state.user_score,
        "bot_score": game_state.bot_score,
        "user_bomb_available": not game_state.user_bomb_used,
        "bot_bomb_available": not game_state.bot_bomb_used,
        "game_over": game_state.game_over,
        "last_round": {
            "user_move": game_state.last_user_move,
            "bot_move": game_state.last_bot_move,
            "result": game_state.last_round_result
        } if game_state.last_user_move else None
    }

def reset_game() -> dict:
    """
    RESET TOOL: Clears all game state for a new game.
    """
    global game_state
    game_state = GameState()
    return {
        "status": "success",
        "message": "Game reset successfully. Ready for a new game!"
    }

# =============================================================================
# ADK TOOL DECLARATIONS
# =============================================================================

validate_move_declaration = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="validate_and_process_move",
            description="Validates the user's move input and processes the complete game round. Handles validation (invalid inputs, bomb restrictions), executes game logic (determines winner), and updates game state. Returns comprehensive round outcome including scores and game status. This is the primary state mutation tool.",
            parameters={
                "type": "object",
                "properties": {
                    "user_input": {
                        "type": "string",
                        "description": "The raw move input from the user. Should be one of: 'rock', 'paper', 'scissors', or 'bomb'. Any other input will be treated as invalid and waste the round."
                    }
                },
                "required": ["user_input"]
            }
        )
    ]
)

get_state_declaration = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="get_game_state",
            description="Retrieves the current game state including scores, rounds played, bomb availability, and last round details. Read-only operation - does not modify state. Use this to check game status before responding to user.",
            parameters={
                "type": "object",
                "properties": {}
            }
        )
    ]
)

reset_game_declaration = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="reset_game",
            description="Resets the game state completely, clearing all scores, round counts, and bomb usage. Use this to start a fresh game after the current game ends.",
            parameters={
                "type": "object",
                "properties": {}
            }
        )
    ]
)

# =============================================================================
# AGENT CONFIGURATION
# =============================================================================

SYSTEM_INSTRUCTION = """You are an intelligent Game Referee for Rock-Paper-Scissors-Plus.

GAME RULES (explain in ≤5 lines):
- Best of 3 rounds. Valid moves: rock, paper, scissors, bomb.
- Standard RPS: rock beats scissors, paper beats rock, scissors beats paper.
- Bomb beats everything (bomb vs bomb = draw). Each player gets ONE bomb per game.
- Invalid input wastes the round. Game automatically ends after 3 rounds.

YOUR RESPONSIBILITIES:
1. At game start: Explain rules concisely and prompt for first move
2. For each user input: ALWAYS call validate_and_process_move tool
3. Present round results clearly:
   - Round number
   - Both moves played
   - Round winner
   - Current score
   - Rounds remaining
4. After 3 rounds: Announce final result (User wins / Bot wins / Draw)
5. Handle errors gracefully with helpful messages

OUTPUT FORMAT (per round):
Round X/3: You played [move] | Bot played [move] → [Winner wins/Draw]
Score: You X - Bot Y | [X rounds remaining] | Your bomb: [available/used]

Be conversational, encouraging, and clear. Never let the game exceed 3 rounds."""

# =============================================================================
# MAIN GAME LOOP
# =============================================================================

def run_game():
    """
    Main game execution loop with Google ADK agent.
    Handles agent initialization, conversation flow, and tool execution.
    """
    
    # Validate API key
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("❌ Error: GOOGLE_API_KEY environment variable not set")
        print("Please set it with: export GOOGLE_API_KEY='your-key-here'")
        return
    
    # Initialize ADK client
    client = genai.Client(api_key=api_key)
    
    # Configure agent with tools
    agent_config = {
        "model": "gemini-2.0-flash-exp",
        "system_instruction": SYSTEM_INSTRUCTION,
        "tools": [
            validate_move_declaration,
            get_state_declaration,
            reset_game_declaration
        ]
    }
    
    print("=" * 60)
    print("🎮 ROCK-PAPER-SCISSORS-PLUS REFEREE")
    print("=" * 60)
    print()
    
    try:
        # Create chat session
        session = client.agentic.chats.create(**agent_config)
        
        # Initial message to start game
        response = session.send_message("Hello! Please start the game and explain the rules.")
        print(f"🤖 Referee:\n{response.text}\n")
        
        # Main game loop
        while not game_state.game_over:
            # Get user input
            user_input = input("Your move: ").strip()
            
            if not user_input:
                print("⚠️  Please enter a move!\n")
                continue
            
            # Handle quit command
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Thanks for playing!")
                break
            
            # Send user message to agent
            response = session.send_message(user_input)
            
            # Process any tool calls in response
            while response.candidates[0].content.parts:
                part = response.candidates[0].content.parts[0]
                
                # Check if agent is requesting a tool call
                if hasattr(part, 'function_call'):
                    func_call = part.function_call
                    
                    # Execute the requested tool
                    if func_call.name == "validate_and_process_move":
                        result = validate_and_process_move(func_call.args["user_input"])
                    elif func_call.name == "get_game_state":
                        result = get_game_state()
                    elif func_call.name == "reset_game":
                        result = reset_game()
                    else:
                        result = {"error": f"Unknown tool: {func_call.name}"}
                    
                    # Send tool result back to agent
                    response = session.send_message(
                        types.Content(parts=[
                            types.Part(function_response=types.FunctionResponse(
                                name=func_call.name,
                                response=result
                            ))
                        ])
                    )
                else:
                    # No more tool calls, break loop
                    break
            
            # Display agent's response to user
            print(f"\n🤖 Referee:\n{response.text}\n")
        
        # Game ended
        if game_state.game_over:
            print("=" * 60)
            print("🏁 GAME OVER")
            print("=" * 60)
            print(f"Final Score: You {game_state.user_score} - Bot {game_state.bot_score}")
            
            if game_state.user_score > game_state.bot_score:
                print("🎉 Congratulations! You win!")
            elif game_state.bot_score > game_state.user_score:
                print("🤖 Bot wins this time!")
            else:
                print("🤝 It's a draw!")
            print()
    
    except Exception as e:
        print(f"\n❌ Error occurred: {e}")
        print("Please check your API key and internet connection.")

if __name__ == "__main__":
    run_game()
