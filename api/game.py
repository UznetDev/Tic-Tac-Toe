import numpy as np

class TicTacToe:
    def __init__(self, board=None):
        self.board = board if board is not None else np.zeros((3, 3), dtype=int)
        self.current_winner = None

    def empty_squares(self):
        return [(i, j) for i in range(3) for j in range(3) if self.board[i][j] == 0]

    def winner(self, player):
        for i in range(3):
            if all([self.board[i][j] == player for j in range(3)]):
                return True
            if all([self.board[j][i] == player for j in range(3)]):
                return True

        if all([self.board[i][i] == player for i in range(3)]):
            return True
        if all([self.board[i][2 - i] == player for i in range(3)]):
            return True

        return False

    def is_draw(self):
        return len(self.empty_squares()) == 0 and not self.current_winner

    def make_move(self, square, player):
        if self.board[square[0]][square[1]] == 0:
            self.board[square[0]][square[1]] = player
            if self.winner(player):
                self.current_winner = player
            return True
        return False

    def minimax(self, state, player):
        max_player = 2
        other_player = 1 if player == 2 else 2

        if self.winner(other_player):
            return {'position': None, 'score': 1 * (len(self.empty_squares()) + 1) if other_player == max_player else -1 * (len(self.empty_squares()) + 1)}
        elif self.is_draw():
            return {'position': None, 'score': 0}

        if player == max_player:
            best = {'position': None, 'score': -np.inf}
        else:
            best = {'position': None, 'score': np.inf}

        for possible_move in self.empty_squares():
            state[possible_move[0]][possible_move[1]] = player
            sim_score = self.minimax(state, other_player)
            state[possible_move[0]][possible_move[1]] = 0
            sim_score['position'] = possible_move

            if player == max_player:
                if sim_score['score'] > best['score']:
                    best = sim_score
            else:
                if sim_score['score'] < best['score']:
                    best = sim_score

        return best