# game.py
import random

class Game:
    """Encapsulates the state and rules of a Backgammon game."""

    def __init__(self):
        """Initializes a new game."""
        self.board_points = [0] * 26  # 0-23 points, 24 white bar, 25 black bar
        self.current_player = 1      # 1 for White, -1 for Black
        self.dice = [None, None]     # Current dice roll
        self.moves_left = []         # List of available moves from dice
        self.white_borne_off = 0
        self.black_borne_off = 0
        self.winner = 0              # 0: No winner, 1: White, -1: Black
        self.move_history = []
        self.reset()

    def _setup_initial_board(self):
        """Sets the board_points array to the standard starting position."""
        # Standard starting position
        initial_board = [0] * 26
        initial_board[0] = 2    # Point 1
        initial_board[5] = -5   # Point 6
        initial_board[7] = -3   # Point 8
        initial_board[11] = 5   # Point 12
        initial_board[12] = -5  # Point 13
        initial_board[16] = 3   # Point 17
        initial_board[18] = 5   # Point 19
        initial_board[23] = -2  # Point 24
        return initial_board

    def reset(self):
        """Resets the game state to the initial configuration."""
        self.board_points = self._setup_initial_board()
        self.current_player = 1
        self.dice = [None, None]
        self.moves_left = []
        self.white_borne_off = 0
        self.black_borne_off = 0
        self.winner = 0
        print("Game state reset.")

    def roll_dice(self):
        """Rolls two dice and sets up available moves. Returns True if roll was valid."""
        if self.winner != 0:
            print("Cannot roll, game is over.")
            return False # Indicate roll didn't happen

        self.dice[0] = random.randint(1, 6)
        self.dice[1] = random.randint(1, 6)

        if self.dice[0] == self.dice[1]: # Doubles
            self.moves_left = [self.dice[0]] * 4
        else:
            self.moves_left = [self.dice[0], self.dice[1]]

        print(f"Rolled {self.dice}. Moves: {self.moves_left}")
        return True # Indicate roll happened

    def _can_bear_off(self, player):
        """Checks if all the player's checkers are in their home board."""
        checkers_outside_home = 0
        if player == 1: # White's home is 18-23
            if self.board_points[24] > 0: return False # Check bar
            for i in range(18):
                if self.board_points[i] > 0: checkers_outside_home += self.board_points[i]
        else: # Black's home is 0-5
            if self.board_points[25] < 0: return False # Check bar
            for i in range(6, 24):
                if self.board_points[i] < 0: checkers_outside_home += abs(self.board_points[i])

        return checkers_outside_home == 0

    def _check_win(self):
        """Checks if a player has won (borne off all 15 checkers). Sets self.winner."""
        if self.white_borne_off == 15:
            self.winner = 1
            return True
        if self.black_borne_off == 15:
            self.winner = -1
            return True
        return False

    def _get_target_index(self, start_index, die_roll, player):
        """Calculates the target point index based on start, roll, and player.
           Returns target index, or -99 if calculation results in invalid state (e.g., wrong bar entry)."""
        # White moves from 0 towards 23, Black moves from 23 towards 0
        if player == 1: # White
            if start_index == 24: # Moving from white bar
                target = die_roll - 1 # Target is 0-indexed point number
                return target if 0 <= target <= 5 else -99 # Invalid entry point
            else:
                target = start_index + die_roll
                return target # Can be >= 24 for bear off attempts
        else: # Black
            if start_index == 25: # Moving from black bar
                target = 24 - die_roll # Target is 0-indexed point number
                return target if 18 <= target <= 23 else -99 # Invalid entry point
            else:
                target = start_index - die_roll
                return target # Can be < 0 for bear off attempts

    def is_move_valid(self, start_index, die_roll):
        """Checks if a move is valid for the current player.
           Returns (True, target_index) if valid, (False, reason_code) if invalid.
           target_index can be 0-23, 24 (white bear off), -1 (black bear off).
           reason_code can be -99 (general invalid), or a target_index indicating the failed destination.
        """
        player = self.current_player

        # 0. Basic checks
        if self.winner != 0: return False, -99
        if die_roll not in self.moves_left: return False, -99 # Die not available

        # 1. Check if player has checkers on the starting point (incl. bar)
        if start_index == 24: # White bar
             if self.board_points[24] <= 0: return False, -99
        elif start_index == 25: # Black bar
             if self.board_points[25] >= 0: return False, -99
        elif 0 <= start_index <= 23:
             if self.board_points[start_index] * player <= 0: return False, -99 # Point empty or opponent's
        else:
            return False, -99 # Invalid start_index

        # 2. Check if moving from the bar is required
        white_bar_idx, black_bar_idx = 24, 25
        if player == 1 and self.board_points[white_bar_idx] > 0 and start_index != white_bar_idx:
            return False, -99 # Must move from white bar
        if player == -1 and self.board_points[black_bar_idx] < 0 and start_index != black_bar_idx:
            return False, -99 # Must move from black bar

        # 3. Calculate potential target index
        target_index = self._get_target_index(start_index, die_roll, player)

        # 4. Check invalid bar entry / invalid target calculation
        if target_index == -99:
            return False, target_index # Specific reason code for bad calculation

        # 5. Check for bearing off
        can_bear_off_now = self._can_bear_off(player)
        if can_bear_off_now:
            is_bearing_off_attempt = (player == 1 and target_index >= 24) or (player == -1 and target_index < 0)
            if is_bearing_off_attempt:
                actual_target_for_bear_off = 24 if player == 1 else -1 # Special target indices
                is_exact_roll = (player == 1 and target_index == 24) or (player == -1 and target_index == -1)
                is_overshoot = (player == 1 and target_index > 24) or (player == -1 and target_index < -1)

                is_furthest = True
                if is_overshoot:
                    if player == 1:
                        # Check points HIGHER than start_index (closer to point 24)
                        for i in range(start_index + 1, 24):
                            if self.board_points[i] > 0: is_furthest = False; break
                    else: # player == -1
                        # Check points LOWER than start_index (closer to point -1)
                        for i in range(start_index - 1, -1, -1):
                            if self.board_points[i] < 0: is_furthest = False; break

                if is_exact_roll or (is_overshoot and is_furthest):
                    return True, actual_target_for_bear_off
                else:
                    # Invalid bear off (e.g., overshoot but not furthest, etc.)
                    # If target is still on board (0-23), proceed to check landing spot
                    if not (0 <= target_index <= 23):
                        return False, target_index # Invalid bear off target

        # 6. Check if target is on the main board (0-23)
        if not (0 <= target_index <= 23):
             # This case should now only happen if bearing off was attempted but failed the logic above
             return False, target_index

        # 7. Check target point occupancy (landing spot check)
        target_point_checkers = self.board_points[target_index]
        is_opponent_occupied = (target_point_checkers * player) < 0

        if is_opponent_occupied and abs(target_point_checkers) > 1:
            return False, target_index # Target point is blocked

        # If all checks pass, it's a valid regular move to target_index
        return True, target_index

    def can_player_move(self):
        """Checks if the current player has ANY valid moves with the current dice."""
        player = self.current_player
        current_moves = self.moves_left
        if not current_moves or self.winner != 0:
            return False # No dice rolled or moves used up, or game over

        bar_idx = 24 if player == 1 else 25

        # 1. Check if must move from bar
        if self.board_points[bar_idx] * player > 0:
            for die_roll in set(current_moves): # Use set to avoid checking same roll multiple times for doubles
                is_valid, _ = self.is_move_valid(bar_idx, die_roll)
                if is_valid: return True
            return False # No valid moves possible from bar

        # 2. If not on bar, check moves from regular points
        else:
            for point_idx in range(24):
                if self.board_points[point_idx] * player > 0:
                    for die_roll in set(current_moves):
                        is_valid, _ = self.is_move_valid(point_idx, die_roll)
                        if is_valid: return True
            return False # No valid moves found from any point

    def make_move(self, start_index, die_roll):
        """Attempts to make a move for the current player using a specific die roll.
           Returns True if the move was successful, False otherwise."""
        self.move_history.append(self.get_state().copy())
        player = self.current_player

        is_valid, target_index = self.is_move_valid(start_index, die_roll)

        if not is_valid:
            # print(f"Move from {start_index} with {die_roll} is invalid.")
            return False

        # --- Execute the move ---
        # print(f"Making move: P{player} from {start_index} to {target_index} using {die_roll}")
        self.board_points[start_index] -= player # Remove checker from start
        is_bearing_off = (target_index == -1 or target_index == 24)

        if is_bearing_off:
            if player == 1: self.white_borne_off += 1
            else: self.black_borne_off += 1
            # print(f"Borne off: W={self.white_borne_off}, B={self.black_borne_off}")
        else:
            # Check for hit before placing checker
            if (self.board_points[target_index] * player) < 0:
                # print(f"Hit opponent on point {target_index}!")
                self.board_points[target_index] = 0 # Clear opponent's checker (should only be 1)
                opponent_bar_index = 25 if player == 1 else 24
                self.board_points[opponent_bar_index] -= player # Add opponent checker to their bar

            self.board_points[target_index] += player # Add checker to target

        # Update game state
        self.moves_left.remove(die_roll)
        self._check_win() # Check if this move resulted in a win

        return True

    def switch_player(self):
        """Switches the current player and resets dice/moves."""
        if self.winner != 0:
            print("Cannot switch player, game is over.")
            return
        self.current_player *= -1
        self.dice = [None, None]
        self.moves_left = []
        print(f"Turn switched to Player {self.current_player} ({'White' if self.current_player == 1 else 'Black'})")

    def get_state(self):
        """Returns a dictionary representing the current game state, suitable for network transfer."""
        return {
            'board_points': self.board_points,
            'current_player': self.current_player,
            'dice': self.dice,
            'moves_left': self.moves_left,
            'white_borne_off': self.white_borne_off,
            'black_borne_off': self.black_borne_off,
            'winner': self.winner,
        }

    def apply_state(self, state_dict):
        """Updates the game state from a received state dictionary."""
        self.board_points = state_dict.get('board_points', self.board_points)
        self.current_player = state_dict.get('current_player', self.current_player)
        self.dice = state_dict.get('dice', self.dice)
        self.moves_left = state_dict.get('moves_left', self.moves_left)
        # We don't necessarily apply game_phase from here, that's App logic
        self.white_borne_off = state_dict.get('white_borne_off', self.white_borne_off)
        self.black_borne_off = state_dict.get('black_borne_off', self.black_borne_off)
        self.winner = state_dict.get('winner', self.winner)
        # print("Game state updated from received data.")

    def undo_last_move(self):
        if not self.move_history:
            print("No moves to undo.")
            return False
        last_state = self.move_history.pop()
        self.apply_state(last_state)
        print("Undo performed.")
        return True
