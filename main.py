from fastapi import FastAPI, Request, HTTPException
from api.game import TicTacToe
from loader import db
import numpy as np

app = FastAPI()
games = {}
game_id_counter = 1


@app.post("/start_game")
async def start_game(request: Request):
    try:
        data = await request.json()
        player_piece = data.get('player_piece', 1)
        first_player = data.get('first_player', 'user')
        global game_id_counter
        game_id = game_id_counter
        game_id_counter += 1

        game = TicTacToe()
        games[game_id] = game

        if first_player == 'computer':
            best_move = game.minimax(game.board.copy(), 2)['position']
            game.make_move(best_move, 2)
            db.insert_move(game_id, move_number=1, player=2, position=best_move, result="ongoing")

        return {"game_id": game_id, "board": game.board.tolist(), "message": "Game started"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while starting the game: {str(e)}")


@app.post("/play")
async def play(request: Request):
    try:
        data = await request.json()
        board = np.array(data['board'])
        position = data['position']
        player = data.get('player', 1)
        game_id = data['game_id']
        move_number = data.get('move_number', 1)

        game = games.get(game_id)
        if not game:
            raise HTTPException(status_code=404, detail="Invalid game ID")

        game.board = board

        if game.current_winner or game.is_draw():
            return {"board": game.board.tolist(), "message": "Game over"}

        # Player's move
        if not game.make_move(position, player):
            return {"board": game.board.tolist(), "message": "Invalid move"}
        db.insert_move(game_id, 
                       move_number=move_number, 
                       player=player, 
                       position=position, 
                       result="ongoing")
        move_number += 1

        if game.current_winner:
            db.insert_move(game_id, 
                           move_number=move_number, 
                           player=player, 
                           position=position, result="win")
            return {"board": game.board.tolist(), 
                    "message": f"Player {player} wins!"}

        if game.is_draw():
            db.insert_move(game_id, 
                           move_number=move_number, 
                           player=player, position=position, result="draw")
            return {"board": game.board.tolist(), "message": "It's a draw!"}

        best_move = game.minimax(game.board.copy(), 2)['position']
        game.make_move(best_move, 2)
        db.insert_move(game_id, move_number=move_number, player=2, position=best_move, result="ongoing")
        move_number += 1

        if game.current_winner:
            db.insert_move(game_id, move_number=move_number, player=2, position=best_move, result="win")
            return {"board": game.board.tolist(), "message": "Computer wins!"}

        if game.is_draw():
            db.insert_move(game_id, move_number=move_number, player=2, position=best_move, result="draw")
            return {"board": game.board.tolist(), "message": "It's a draw!"}

        return {"board": game.board.tolist(), "message": "Game continues", "move_number": move_number}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred during gameplay: {str(e)}")