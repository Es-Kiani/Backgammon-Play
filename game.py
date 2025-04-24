# game.py
import random
import pickle
from copy import deepcopy

class Game:
    def __init__(self):
        self.history = []
        self.reset()

    def _setup_initial_board(self):
        initial_board = [0] * 26
        initial_board[0] = 2
        initial_board[5] = -5
        initial_board[7] = -3
        initial_board[11] = 5
        initial_board[12] = -5
        initial_board[16] = 3
        initial_board[18] = 5
        initial_board[23] = -2
        return initial_board

    def reset(self):
        self.board_points = self._setup_initial_board()
        self.current_player = 1
        self.dice = [None, None]
        self.moves_left = []
        self.white_borne_off = 0
        self.black_borne_off = 0
        self.winner = 0
        self.history.clear()
        self._save_history()

    def _save_history(self):
        state = {
            'board_points': deepcopy(self.board_points),
            'current_player': self.current_player,
            'dice': list(self.dice),
            'moves_left': list(self.moves_left),
            'white_borne_off': self.white_borne_off,
            'black_borne_off': self.black_borne_off,
            'winner': self.winner,
        }
        self.history.append(state)

    def undo_move(self):
        if len(self.history) >= 2:
            self.history.pop()
            prev = self.history[-1]
            self.apply_state(prev)
            return True
        return False

    def save_game(self, filepath):
        with open(filepath, 'wb') as f:
            pickle.dump(self.history, f)

    def load_game(self, filepath):
        try:
            with open(filepath, 'rb') as f:
                loaded = pickle.load(f)
            if isinstance(loaded, list) and loaded:
                self.history = loaded
                self.apply_state(self.history[-1])
                return True
        except Exception:
            pass
        return False

    def apply_state(self, state):
        self.board_points = deepcopy(state['board_points'])
        self.current_player = state['current_player']
        self.dice = list(state['dice'])
        self.moves_left = list(state['moves_left'])
        self.white_borne_off = state['white_borne_off']
        self.black_borne_off = state['black_borne_off']
        self.winner = state['winner']

    def roll_dice(self):
        if self.winner != 0:
            return False
        self._save_history()
        self.dice[0] = random.randint(1, 6)
        self.dice[1] = random.randint(1, 6)
        if self.dice[0] == self.dice[1]:
            self.moves_left = [self.dice[0]] * 4
        else:
            self.moves_left = [self.dice[0], self.dice[1]]
        return True

    def is_move_valid(self, start_index, die_roll):
        return True, start_index

    def can_player_move(self):
        return True

    def make_move(self, start_index, die_roll):
        self._save_history()
        player = self.current_player
        is_valid, target_index = self.is_move_valid(start_index, die_roll)
        if not is_valid:
            return False
        self.board_points[start_index] -= player
        if target_index == 24 or target_index == -1:
            if player == 1:
                self.white_borne_off += 1
            else:
                self.black_borne_off += 1
        else:
            if self.board_points[target_index] * player < 0:
                self.board_points[target_index] = 0
                bar_idx = 25 if player == 1 else 24
                self.board_points[bar_idx] -= player
            self.board_points[target_index] += player
        self.moves_left.remove(die_roll)
        return True

    def switch_player(self):
        self._save_history()
        self.current_player *= -1
        self.dice = [None, None]
        self.moves_left.clear()
