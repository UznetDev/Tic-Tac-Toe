from fastapi import HTTPException, Query
from api.game import TicTacToe
from loader import db, app
import numpy as np

games = {}
game_id_counter = 1


@app.get("/start_game")
def start_game(player_piece: int = Query(1), first_player: str = Query('user')):
    try:
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
        raise HTTPException(status_code=500, 
                            detail=f"An error occurred while starting the game: {str(e)}")


@app.get("/play")
def play(
    game_id: int,
    board: str,
    position: str,
    player: int = Query(1),
    move_number: int = Query(1)
):
    try:
        board = np.array(eval(board))
        position = tuple(map(int, position.split(',')))
        game = games.get(game_id)

        if not game:
            raise HTTPException(status_code=404, detail="Invalid game ID")

        game.board = board

        if game.current_winner or game.is_draw():
            return {"board": game.board.tolist(), "message": "Game over"}

        if not game.make_move(position, player):
            return {"board": game.board.tolist(), "message": "Invalid move"}
        db.insert_move(game_id, move_number=move_number, player=player, position=position, result="ongoing")
        move_number += 1

        if game.current_winner:
            db.insert_move(game_id, move_number=move_number, player=player, position=position, result="win")
            return {"board": game.board.tolist(), "message": f"Player {player} wins!"}

        if game.is_draw():
            db.insert_move(game_id, move_number=move_number, player=player, position=position, result="draw")
            return {"board": game.board.tolist(), "message": "It's a draw!"}

        # Kompyuter yurishi
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
        raise HTTPException(status_code=500, 
                            detail=f"An error occurred during gameplay: {str(e)}")
