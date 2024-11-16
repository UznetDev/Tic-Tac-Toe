from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import numpy as np

app = FastAPI()

boards = {}
games = {}


@app.post("/start_game")
async def start_game(request: Request):
    data = await request.json()
    player_symbol = data.get("player_symbol", "X")
    ai_symbol = "O" if player_symbol == "X" else "X"
    player_turn = data.get("player_turn", True)
    game_id = len(boards) + 1
    board = np.full((3, 3), "")
    boards[game_id] = board
    games[game_id] = {
        "player_symbol": player_symbol,
        "ai_symbol": ai_symbol,
        "player_turn": player_turn,
        "status": "ongoing"
    }

    if not player_turn:
        # AI makes the first move
        move = get_best_move(board, ai_symbol, player_symbol)
        board[move] = ai_symbol

    return JSONResponse({
        "game_id": game_id,
        "board": board.tolist(),
        "status": games[game_id]["status"]
    })


@app.post("/make_move")
async def make_move(request: Request):
    data = await request.json()
    game_id = data["game_id"]
    row = data["row"]
    col = data["col"]

    board = boards[game_id]
    game = games[game_id]

    if board[row, col] != "":
        return JSONResponse({"error": "Invalid move"}, status_code=400)

    board[row, col] = game["player_symbol"]

    if check_winner(board, game["player_symbol"]):
        game["status"] = "player_won"
        return JSONResponse({
            "board": board.tolist(),
            "status": game["status"]
        })

    elif is_draw(board):
        game["status"] = "draw"
        return JSONResponse({
            "board": board.tolist(),
            "status": game["status"]
        })

    # AI's turn
    ai_move = get_best_move(board, game["ai_symbol"], game["player_symbol"])
    board[ai_move] = game["ai_symbol"]

    if check_winner(board, game["ai_symbol"]):
        game["status"] = "ai_won"
    elif is_draw(board):
        game["status"] = "draw"

    return JSONResponse({
        "board": board.tolist(),
        "status": game["status"]
    })


def check_winner(board, symbol):
    # Check rows, columns, and diagonals
    for i in range(3):
        if np.all(board[i, :] == symbol):
            return True
        if np.all(board[:, i] == symbol):
            return True
    if np.all(np.diag(board) == symbol):
        return True
    if np.all(np.diag(np.fliplr(board)) == symbol):
        return True
    return False


def is_draw(board):
    return np.all(board != "")


def get_best_move(board, ai_symbol, player_symbol):
    best_score = -np.inf
    best_move = None

    for idx, value in np.ndenumerate(board):
        if value == "":
            board[idx] = ai_symbol
            score = minimax(board, 0, False, ai_symbol, player_symbol)
            board[idx] = ""
            if score > best_score:
                best_score = score
                best_move = idx
    return best_move


def minimax(board, depth, is_maximizing, ai_symbol, player_symbol):
    if check_winner(board, ai_symbol):
        return 1
    elif check_winner(board, player_symbol):
        return -1
    elif is_draw(board):
        return 0

    if is_maximizing:
        best_score = -np.inf
        for idx, value in np.ndenumerate(board):
            if value == "":
                board[idx] = ai_symbol
                score = minimax(board, depth + 1, False, ai_symbol, player_symbol)
                board[idx] = ""
                best_score = max(score, best_score)
        return best_score
    else:
        best_score = np.inf
        for idx, value in np.ndenumerate(board):
            if value == "":
                board[idx] = player_symbol
                score = minimax(board, depth + 1, True, ai_symbol, player_symbol)
                board[idx] = ""
                best_score = min(score, best_score)
        return best_score
