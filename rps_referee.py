# Rock Paper Scissors Plus – Minimal Referee


import random
from typing import Literal

# ---------- STATE MODEL ----------
game_state = {
    "round": 1,
    "user_score": 0,
    "bot_score": 0,
    "user_bomb_used": False,
    "bot_bomb_used": False,
    "moves": [],
    "game_over": False
}

# ---------- GAME LOGIC ----------

def determine_winner(user_move: str, bot_move: str) -> Literal["user","bot","draw"]:

    if user_move == "bomb" and bot_move == "bomb":
        return "draw"
    if user_move == "bomb":
        return "user"
    if bot_move == "bomb":
        return "bot"

    if user_move == bot_move:
        return "draw"

    beats = {
        "rock": "scissors",
        "paper": "rock",
        "scissors": "paper"
    }

    if beats.get(user_move) == bot_move:
        return "user"
    return "bot"


def validate_move(user_input: str) -> str:
    move = user_input.strip().lower()
    valid_moves = ["rock","paper","scissors","bomb"]

    if move not in valid_moves:
        return "invalid"

    if move == "bomb" and game_state["user_bomb_used"]:
        return "invalid"

    return move


def handle_turn(user_input: str):

    user_move = validate_move(user_input)
    bot_move = choose_bot_move()

    if user_move == "invalid":
        game_state["moves"].append({
            "round": game_state["round"],
            "user": "invalid",
            "bot": bot_move,
            "winner": "bot"
        })

        game_state["bot_score"] += 1
        game_state["round"] += 1
        return "wasted"

    if user_move == "bomb":
        game_state["user_bomb_used"] = True
    if bot_move == "bomb":
        game_state["bot_bomb_used"] = True

    winner = determine_winner(user_move, bot_move)

    if winner == "user":
        game_state["user_score"] += 1
    elif winner == "bot":
        game_state["bot_score"] += 1

    game_state["moves"].append({
        "round": game_state["round"],
        "user": user_move,
        "bot": bot_move,
        "winner": winner
    })

    game_state["round"] += 1

    if game_state["round"] > 3:
        game_state["game_over"] = True

    return winner


def choose_bot_move():
    options = ["rock","paper","scissors"]
    if not game_state["bot_bomb_used"]:
        options.append("bomb")
    return random.choice(options)


def final_result():

    if game_state["user_score"] > game_state["bot_score"]:
        w = "User wins the game!"
    elif game_state["bot_score"] > game_state["user_score"]:
        w = "Bot wins the game!"
    else:
        w = "Game is Draw."

    return f"Game Over after 3 rounds | User Score={game_state['user_score']} | Bot Score={game_state['bot_score']} -> {w}"


# ---------- MAIN ----------
if __name__ == "__main__":

    print("Best of 3 rounds | moves: rock,paper,scissors,bomb once | invalid wastes round | bomb beats all")

    for i in range(3):
        inp = input("> ")
        print("Referee:", handle_turn(inp))

    print("---")
    print(final_result())
