# app.py
import pygame
import sys
import math # Keep math? Game class might need it indirectly? Check game.py - No. Remove.
import random # Used by _update_animation
import time
import socket # For getting local IP
import threading # For non-blocking server start
from network import Network # Import the class directly
from game import Game

# --- Import UI elements ---
# TODO: Review if ALL these are needed directly by App or only by drawing functions
from ui import (
    WIDTH, HEIGHT, SIDEBAR_X_START, CREAM,
    BUTTON_RECT, RESET_BUTTON_RECT, BACK_BUTTON_RECT, # In-game buttons
    OFFLINE_BUTTON_RECT, HOST_BUTTON_RECT, JOIN_BUTTON_RECT, EXIT_MENU_BUTTON_RECT, # Menu buttons
    START_HOST_BUTTON_RECT, CANCEL_HOST_BUTTON_RECT, HOST_IP_INPUT_RECT, HOST_PORT_INPUT_RECT, # Hosting setup
    JOIN_IP_BUTTON_RECT, JOIN_CANCEL_IP_BUTTON_RECT, # Join IP screen buttons
    INPUT_BOX_RECT, # Client IP Input box
    draw_board, draw_checkers, draw_point_numbers, draw_sidebar, draw_game_over_screen, get_point_rect, draw_main_menu,
    draw_hosting_setup_screen, draw_waiting_screen, draw_ip_input_box, draw_connecting_screen, load_background,
    font, small_font, # Fonts needed for drawing error messages directly in App._draw
    RED, BLACK, # Colors needed for error messages
)


class App:
    """Manages the overall application lifecycle, game phases, user input,
       and coordinates between the Game, UI, and Network components."""

    def __init__(self):
        # Pygame setup
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Backgammon")
        load_background() # Load background image AFTER display is set

        # Core game instance
        self.game = Game()

        # App State Variables
        self.running = False
        self.game_phase = 'MAIN_MENU'
        self.selected_point_index = None
        self.valid_destination_indices = set()

        # Animation state
        self.animation_start_time = 0
        self.is_rolling_animation = False
        self.animation_dice = [None, None]

        # Timer state
        self.game_start_time = 0

        # Network state
        self.network = None
        self.player_id = 0 # 1 for White (host), -1 for Black (client)
        self.connection_status = "Offline"
        self.network_error = None
        self.server_thread = None
        self.connection_thread = None
        self.connection_target_ip = None
        self.connection_result = None
        self.assigned_player_id_temp = None

        # Menu/Input state
        self.local_ips = []
        self.host_port_default = 5555
        self.input_active = False
        self.input_text = ""
        self.input_prompt = ""
        self.host_ip_input = ""
        self.host_port_input = str(self.host_port_default)
        self.active_input_box = None

        # State for showing "No Moves" feedback
        self.pending_no_moves_switch = False
        self.no_moves_phase_start_time = 0

    def _handle_click(self, pos):
        """Handles BOARD clicks for selecting/moving checkers."""
        # Assumes it's the current player's turn and they clicked on the board area.
        # Ignore board clicks if game is over or during animation (checked in main loop)
        clicked_point_index = -2 # Default: click outside points/bar

        # Check bar click first
        bar_rect_white_abs = get_point_rect(24)
        bar_rect_black_abs = get_point_rect(25)
        if self.game.current_player == 1 and self.game.board_points[24] > 0 and bar_rect_white_abs.collidepoint(pos):
            clicked_point_index = 24
        elif self.game.current_player == -1 and self.game.board_points[25] < 0 and bar_rect_black_abs.collidepoint(pos):
            clicked_point_index = 25
        else:
            # Check regular point clicks
            for i in range(24):
                point_rect_abs = get_point_rect(i)
                if point_rect_abs.collidepoint(pos):
                    clicked_point_index = i
                    break

        # --- Action 1: Select a checker (if phase is MOVING) ---
        if self.game_phase == 'MOVING':
            if self.selected_point_index is None:
                must_move_from_bar = (self.game.current_player == 1 and self.game.board_points[24] > 0) or \
                                     (self.game.current_player == -1 and self.game.board_points[25] < 0)

                potential_selection = -1
                if must_move_from_bar:
                     if (self.game.current_player == 1 and clicked_point_index == 24) or \
                        (self.game.current_player == -1 and clicked_point_index == 25):
                         potential_selection = clicked_point_index
                elif clicked_point_index >= 0 and clicked_point_index <= 23 and (self.game.board_points[clicked_point_index] * self.game.current_player) > 0:
                    potential_selection = clicked_point_index

                if potential_selection != -1:
                    self.selected_point_index = potential_selection
                    self.valid_destination_indices.clear()
                    player = self.game.current_player # Cache player

                    # --- Check individual die moves ---
                    for die_roll in set(self.game.moves_left): # Use set to check unique rolls
                        is_valid, target_idx = self.game.is_move_valid(self.selected_point_index, die_roll)
                        if is_valid:
                            self.valid_destination_indices.add(target_idx)

                    # --- Check sum move (only if non-doubles and both dice available) ---
                    if len(self.game.moves_left) == 2 and self.game.dice[0] != self.game.dice[1]:
                        d1, d2 = self.game.dice[0], self.game.dice[1]
                        start_idx = self.selected_point_index
                        sum_move_valid = False
                        final_sum_target = -99

                        # Check path d1 then d2
                        is_valid_inter1, inter1 = self.game.is_move_valid(start_idx, d1)
                        # Check if intermediate move is valid AND lands on the board (not bear off)
                        if is_valid_inter1 and 0 <= inter1 <= 23:
                            # Temporarily modify state to check validity of second step
                            board_backup = list(self.game.board_points)
                            moves_backup = list(self.game.moves_left)
                            self.game.board_points[start_idx] -= player
                            self.game.board_points[inter1] += player # Assume no hit for temp check
                            self.game.moves_left = [d2]
                            is_valid_final1, final1 = self.game.is_move_valid(inter1, d2)
                            # Restore state
                            self.game.board_points = board_backup
                            self.game.moves_left = moves_backup
                            if is_valid_final1:
                                sum_move_valid = True
                                final_sum_target = final1

                        # Check path d2 then d1 (only if path 1 wasn't valid)
                        if not sum_move_valid:
                            is_valid_inter2, inter2 = self.game.is_move_valid(start_idx, d2)
                            if is_valid_inter2 and 0 <= inter2 <= 23:
                                board_backup = list(self.game.board_points)
                                moves_backup = list(self.game.moves_left)
                                self.game.board_points[start_idx] -= player
                                self.game.board_points[inter2] += player # Assume no hit for temp check
                                self.game.moves_left = [d1]
                                is_valid_final2, final2 = self.game.is_move_valid(inter2, d1)
                                # Restore state
                                self.game.board_points = board_backup
                                self.game.moves_left = moves_backup
                                if is_valid_final2:
                                    sum_move_valid = True
                                    final_sum_target = final2

                        if sum_move_valid:
                            self.valid_destination_indices.add(final_sum_target)

                else:
                    self.selected_point_index = None

            # --- Action 2: Move a selected checker ---\
            elif self.selected_point_index is not None: # Only proceed if a checker is already selected
                # Deselect if clicking same point again
                if clicked_point_index == self.selected_point_index:
                    self.selected_point_index = None
                    self.valid_destination_indices.clear()
                    return

                moved = False
                used_die = -1
                move_target_index = -99

                if clicked_point_index >= 0 and clicked_point_index <= 23 and clicked_point_index in self.valid_destination_indices:
                     move_target_index = clicked_point_index
                elif clicked_point_index == -2:
                     bear_off_target = 24 if self.game.current_player == 1 else -1
                     if bear_off_target in self.valid_destination_indices:
                         move_target_index = bear_off_target

                if move_target_index != -99:
                     # Find which die roll allows this move
                     for die_roll in self.game.moves_left:
                        is_valid, potential_target = self.game.is_move_valid(self.selected_point_index, die_roll)
                        if is_valid and potential_target == move_target_index:
                            used_die = die_roll
                            # Attempt the move using the game object
                            moved = self.game.make_move(self.selected_point_index, die_roll)
                            break

                # --- Try Sum Move (if single move didn't happen and non-doubles available) ---
                if not moved and len(self.game.moves_left) == 2 and self.game.dice[0] != self.game.dice[1]:
                    d1, d2 = self.game.dice[0], self.game.dice[1]
                    start_idx = self.selected_point_index
                    player = self.game.current_player

                    # --- Re-validate and execute Path d1 then d2 ---
                    is_valid_inter1, inter1 = self.game.is_move_valid(start_idx, d1)
                    if is_valid_inter1 and 0 <= inter1 <= 23:
                        # Temporarily apply first move to check second
                        board_backup = list(self.game.board_points)
                        moves_backup = list(self.game.moves_left)
                        # Simulate first move (simplified, no hit check needed here for validation)
                        self.game.board_points[start_idx] -= player
                        self.game.board_points[inter1] += player
                        self.game.moves_left = [d2]
                        is_valid_final1, final1 = self.game.is_move_valid(inter1, d2)
                        # Restore state
                        self.game.board_points = board_backup
                        self.game.moves_left = moves_backup

                        if is_valid_final1 and final1 == move_target_index:
                            print(f"Executing sum move ({d1} then {d2})")
                            # Execute first part (handles hits properly)
                            move1_success = self.game.make_move(start_idx, d1)
                            if move1_success:
                                # Calculate actual intermediate landing spot (important if hit occurred)
                                actual_inter1 = self.game._get_target_index(start_idx, d1, player)
                                # Execute second part from the actual intermediate spot
                                move2_success = self.game.make_move(actual_inter1, d2)
                                if move2_success:
                                    moved = True # Mark as successfully moved
                                else:
                                    # This case is tricky - move 1 happened, move 2 failed
                                    # For now, let the turn potentially end if no other moves
                                    print("WARN: Second part of sum move failed!")
                                    pass # moved remains False
                            else:
                                print("WARN: First part of sum move failed!")

                    # --- Re-validate and execute Path d2 then d1 (if path 1 failed or wasn't the target) ---
                    if not moved:
                        is_valid_inter2, inter2 = self.game.is_move_valid(start_idx, d2)
                        if is_valid_inter2 and 0 <= inter2 <= 23:
                            board_backup = list(self.game.board_points)
                            moves_backup = list(self.game.moves_left)
                            self.game.board_points[start_idx] -= player
                            self.game.board_points[inter2] += player
                            self.game.moves_left = [d1]
                            is_valid_final2, final2 = self.game.is_move_valid(inter2, d1)
                            self.game.board_points = board_backup
                            self.game.moves_left = moves_backup

                            if is_valid_final2 and final2 == move_target_index:
                                print(f"Executing sum move ({d2} then {d1})")
                                move1_success = self.game.make_move(start_idx, d2)
                                if move1_success:
                                    actual_inter2 = self.game._get_target_index(start_idx, d2, player)
                                    move2_success = self.game.make_move(actual_inter2, d1)
                                    if move2_success:
                                        moved = True
                                    else:
                                        print("WARN: Second part of sum move failed!")
                                        pass
                                else:
                                    print("WARN: First part of sum move failed!")

                if moved:
                    # Move was successful, reset UI selection state
                    self.selected_point_index = None
                    self.valid_destination_indices.clear()

                    # Check game over state (make_move updates game.winner)
                    if self.game.winner != 0:
                        self.game_phase = 'GAME_OVER'
                        if self.network: self._send_game_state() # Send final winning state
                        return # End turn processing

                    # After a move, check if any *further* moves are possible with remaining dice
                    can_move_further = self.game.can_player_move()

                    # If moves left is now empty OR no further moves are possible, switch turn
                    if not self.game.moves_left or not can_move_further:
                        if not can_move_further and self.game.moves_left:
                             print(f"No valid moves left for Player {self.game.current_player} with remaining dice {self.game.moves_left}. Ending turn.")
                        if self.network:
                            self._send_game_state(switch_player=True)
                        self.game.switch_player() # Switch player in game state

    def _update_animation(self):
        """Update the dice animation state."""
        # Animation constants should be defined elsewhere or passed in
        ANIMATION_DURATION = 500
        ANIMATION_FRAME_RATE = 10

        if self.is_rolling_animation:
            current_time = pygame.time.get_ticks()
            elapsed_time = current_time - self.animation_start_time

            # Update animation dice values rapidly (simple approach)
            if (elapsed_time // (1000 // ANIMATION_FRAME_RATE)) != ((elapsed_time - (1000//ANIMATION_FRAME_RATE)) // (1000 // ANIMATION_FRAME_RATE)) :
                 self.animation_dice = [random.randint(1, 6), random.randint(1, 6)]

            # End animation after duration
            if elapsed_time >= ANIMATION_DURATION:
                self.is_rolling_animation = False
                # Check if we need to switch turn due to no moves
                if self.pending_no_moves_switch:
                    self.game_phase = 'NO_MOVES_FEEDBACK'
                    self.no_moves_phase_start_time = pygame.time.get_ticks()
                    self.pending_no_moves_switch = False # Reset flag
                    # Send current state (with dice), but don't switch player yet
                    if self.network:
                        self._send_game_state(switch_player=False)
                else:
                    # Normal case: moves are possible
                    self.game_phase = 'MOVING'
                    # Send the state with the final dice roll AFTER animation finishes
                    if self.network:
                        self._send_game_state(switch_player=False)

    def _send_game_state(self, switch_player=False):
        """Sends the current game state via the network."""
        if not self.network:
            return
        state = self.game.get_state() # Get state from game object
        if switch_player:
             # If indicating turn switch, modify state BEFORE sending
             state['current_player'] *= -1
             state['dice'] = [None, None]
             state['moves_left'] = []
             # print(f"Sending state and switching turn to player {state['current_player']}...")
        else:
             # print("Sending current state...")
             pass
        success = self.network.send(state)
        if not success:
            print("Failed to send game state. Opponent might have disconnected.")
            # Consider handling disconnection more formally here

    def _start_offline_game(self):
        self.network = None
        self.player_id = 1 # Default to player 1 in offline
        self.connection_status = "Offline Mode"
        self.game.reset() # Reset game state using game object
        self.game_start_time = pygame.time.get_ticks()
        self.game_phase = 'ROLLING'
        self.selected_point_index = None # Reset UI state
        self.valid_destination_indices.clear()
        print("Starting Offline Game.")

    def _start_hosting_game(self):
        self.network = Network()
        # Get host and port from input fields (with validation/defaults)
        # Fetch IPs if needed
        if not self.local_ips:
             self._get_local_ips()
        host_ip = self.host_ip_input if self.host_ip_input else (self.local_ips[0] if self.local_ips and self.local_ips[0] != "Could not determine IP" else '0.0.0.0')
        try:
            host_port = int(self.host_port_input)
            if not (1024 <= host_port <= 65535):
                 raise ValueError("Port out of valid range")
        except ValueError:
            self.network_error = "Invalid Port (must be 1024-65535)"
            self.game_phase = 'HOSTING_SETUP' # Stay on setup screen
            return

        print(f"Starting server thread on {host_ip}:{host_port}...")
        self.server_thread = threading.Thread(target=self.network.start_server, args=(host_ip, host_port), daemon=True)
        self.server_thread.start()
        self.game_phase = 'WAITING_FOR_CLIENT' # Move to waiting phase
        self.network_error = None

    def _cancel_hosting_attempt(self):
        """Clean up when cancelling hosting before or during waiting."""
        print("Cancelling hosting...")
        if self.server_thread and self.server_thread.is_alive():
            # Attempt to unblock the accept() call by connecting to self
            try:
                # Find a non-loopback IP to connect to if possible
                host_ip = '127.0.0.1' # Fallback
                # Use self.local_ips if already populated, otherwise fetch
                ips_to_check = self.local_ips if self.local_ips else self._get_local_ips()
                for ip in ips_to_check:
                     if ip != "Could not determine IP":
                          host_ip = ip
                          break
                # Use the port that was attempted
                port_to_connect = int(self.host_port_input) if self.host_port_input.isdigit() else self.host_port_default
                print(f"Attempting self-connect to {host_ip}:{port_to_connect} to unblock accept()...")
                dummy_socket = socket.create_connection((host_ip, port_to_connect), timeout=0.5)
                dummy_socket.close()
                print("Self-connect successful, server thread should exit.")
                self.server_thread.join(timeout=1.0) # Wait briefly for thread to exit
            except (socket.timeout, ConnectionRefusedError, OSError) as e:
                print(f"Self-connect failed (may be okay if thread closing): {e}")
            except Exception as e:
                 print(f"Unexpected error during self-connect: {e}")

        if self.network:
            self.network.close() # Close the server socket
        self.network = None
        self.server_thread = None
        self.network_error = None
        self.connection_status = "Offline"
        self.player_id = 0
        self.game_phase = 'MAIN_MENU'

    def _attempt_connection(self):
        """Runs in a separate thread to attempt connection without blocking."""
        # Create Network instance within the thread
        # Use a local variable first to avoid race conditions on the global 'network'
        local_network = Network()

        print(f"Thread attempting connection to {self.connection_target_ip}...")
        # Use default port if needed, maybe make configurable later
        assigned_id = local_network.connect(self.connection_target_ip) # Assumes default port 5555

        if assigned_id:
            print(f"Thread connection successful. Assigned ID: {assigned_id}")
            # Only assign to global network if successful
            self.network = local_network
            self.assigned_player_id_temp = assigned_id
            self.connection_result = 'success'
        else:
            print("Thread connection failed.")
            self.connection_result = 'failed'
            # Ensure the local object is closed if connection failed partway
            local_network.close()

    def _start_joining_game(self, server_ip):
        if not server_ip:
            self.network_error = "IP Address cannot be empty."
            return

        print(f"Initiating connection sequence to {server_ip}")
        self.network = None # Ensure no old network object exists
        self.network_error = None
        self.connection_target_ip = server_ip
        self.connection_result = None # Reset result status
        self.assigned_player_id_temp = None

        # Start connection attempt in a background thread
        self.connection_thread = threading.Thread(target=self._attempt_connection, daemon=True)
        self.connection_thread.start()
        self.game_phase = 'CONNECTING' # Switch to connecting phase

    def _cancel_connection_attempt(self):
        """Handles cancellation during the CONNECTING phase."""
        print("Cancelling connection attempt...")
        if self.connection_thread and self.connection_thread.is_alive():
            # Try to interrupt the connection by closing the socket from the main thread
            # This is a bit forceful but often necessary for blocking calls like connect()
            temp_socket_closer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                # We don't have the network object's socket directly accessible easily here
                # Instead, we signal the thread conceptually. Closing the global network
                # might race condition if the thread just succeeded.
                # The _attempt_connection handles cleanup on failure.
                # We mainly just need to change phase and let the thread exit.
                print("Connection cancelled by user. Thread will terminate.")
            except Exception as e:
                print(f"Error during conceptual socket close for cancellation: {e}")
            finally:
                temp_socket_closer.close()
            # Give the thread a moment to potentially finish/fail due to interruption
            self.connection_thread.join(timeout=0.1)

        # Reset state regardless of thread status
        self.network = None
        self.connection_thread = None
        self.connection_target_ip = None
        self.connection_result = None
        self.network_error = None
        self.game_phase = 'MAIN_MENU'

    def _get_local_ips(self):
        """Tries to get local IP addresses and returns them as a list."""
        ips = []
        try:
            hostname = socket.gethostname()
            # Get all addresses associated with the hostname
            addresses = socket.getaddrinfo(hostname, None)
            for addr in addresses:
                ip = addr[4][0] # The IP address is in the 5th element, index 4
                if ':' not in ip and ip not in ips and not ip.startswith("127."): # Filter IPv6, duplicates, loopback
                    ips.append(ip)
        except socket.gaierror:
            ips.append("Could not determine IP")
        # Fallback if no suitable IP found via getaddrinfo
        if not ips or ips == ["Could not determine IP"]:
             try:
                  # Create a temporary socket to connect to an external server
                  # This forces the OS to choose an appropriate outbound IP
                  with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                       s.settimeout(0) # Non-blocking
                       s.connect(('10.254.254.254', 1)) # Doesn't need to be reachable
                       ip = s.getsockname()[0]
                       if ip and ip not in ips and not ip.startswith("127."):
                           ips.append(ip)
             except Exception:
                  pass # Ignore errors here, it was just a fallback
        if not ips: # If still nothing, add the error message
             ips.append("Could not determine IP")
        self.local_ips = ips # Store fetched IPs
        return ips

    # --- Main Execution Methods ---
    def run(self):
        """The main application loop."""
        self.running = True
        clock = pygame.time.Clock() # For managing frame rate

        while self.running:
            # --- Event Handling ---
            self._handle_events()
            if not self.running: # Check if quit event occurred
                break

            # --- Game State Updates ---
            self._update()

            # --- Drawing ---
            self._draw()

            # --- Frame Rate Control ---
            clock.tick(60) # Limit FPS to 60

        # --- Cleanup ---
        self._cleanup()

    def _handle_events(self):
        """Handles all Pygame events based on the current game phase."""
        is_my_turn = (self.network is None) or (self.player_id == self.game.current_player)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                if self.game_phase == 'CONNECTING': self._cancel_connection_attempt()
                if self.game_phase == 'WAITING_FOR_CLIENT': self._cancel_hosting_attempt()
                return # Exit event handling early

            # --- Phase-Specific Event Handling ---
            if self.game_phase == 'MAIN_MENU':
                self._handle_main_menu_events(event)
            elif self.game_phase == 'HOSTING_SETUP':
                self._handle_hosting_setup_events(event)
            elif self.game_phase == 'WAITING_FOR_CLIENT':
                self._handle_waiting_events(event)
            elif self.game_phase == 'GETTING_IP':
                self._handle_getting_ip_events(event)
            elif self.game_phase == 'CONNECTING':
                self._handle_connecting_events(event)
            # Note: WAITING_FOR_STATE currently has simple quit handling in main update
            elif self.game_phase in ['ROLLING', 'MOVING', 'ROLLING_ANIMATION', 'GAME_OVER']:
                self._handle_in_game_events(event, is_my_turn)

    def _update(self):
        """Updates game state, animations, and network status."""
        # --- Network Receive ---\
        if self.network and not self.is_rolling_animation and self.game_phase not in [
            'MAIN_MENU', 'GETTING_IP', 'WAITING_FOR_STATE',
            'HOSTING_SETUP', 'WAITING_FOR_CLIENT', 'CONNECTING']:
            received_data = self.network.receive()
            if received_data:
                # print("Received state from opponent.")
                self.game.apply_state(received_data)
                # Check win condition based on received state
                if self.game.winner != 0 and self.game_phase != 'GAME_OVER':
                    self.game_phase = 'GAME_OVER' # Update local phase
                    print(f"Game Over signal received. Winner: {self.game.winner}")
                    # Reset UI state on receiving game over
                    self.selected_point_index = None
                    self.valid_destination_indices.clear()
                    self.is_rolling_animation = False
                # <<< START FIX >>>
                # If game is not over and it's now our turn after receiving state, set phase to ROLLING
                elif self.game.winner == 0 and self.game.current_player == self.player_id:
                    print("Received turn, setting phase to ROLLING.")
                    self.game_phase = 'ROLLING'
                    self.selected_point_index = None # Reset selection when turn starts
                    self.valid_destination_indices.clear()
                # <<< END FIX >>>

        # --- Phase-Specific Updates ---\
        if self.game_phase == 'WAITING_FOR_CLIENT':
            self._update_waiting_for_client()
        elif self.game_phase == 'CONNECTING':
            self._update_connecting()
        elif self.game_phase == 'WAITING_FOR_STATE':
            self._update_waiting_for_state()
        elif self.game_phase == 'ROLLING_ANIMATION':
            self._update_animation() # Updates internal animation state

        elif self.game_phase == 'NO_MOVES_FEEDBACK':
            current_time = pygame.time.get_ticks()
            if current_time - self.no_moves_phase_start_time >= 2000: # 2 seconds delay
                print("Feedback delay over. Switching turn.")
                if self.network:
                    self._send_game_state(switch_player=True)
                self.game.switch_player()
                self.game_phase = 'ROLLING'

    def _draw(self):
        """Draws the entire screen based on the current game phase."""
        # Default background or board background
        if self.game_phase in ['ROLLING', 'ROLLING_ANIMATION', 'MOVING', 'GAME_OVER']:
            self.screen.fill(CREAM) # Board area background
        else:
            # Other phases handle their own full backgrounds (menu, setup, etc.)
            pass

        # --- Phase-Specific Drawing ---\
        if self.game_phase == 'MAIN_MENU':
            draw_main_menu(self.screen)
            # Display network error if any
            if self.network_error:
                error_surf = small_font.render(self.network_error, True, RED)
                error_rect = error_surf.get_rect(center=(WIDTH // 2, JOIN_BUTTON_RECT.bottom + 30))
                self.screen.blit(error_surf, error_rect)

        elif self.game_phase == 'HOSTING_SETUP':
            draw_hosting_setup_screen(self.screen, self.local_ips, self.host_ip_input, self.host_port_input, self.active_input_box, self.network_error)

        elif self.game_phase == 'WAITING_FOR_CLIENT':
            draw_waiting_screen(self.screen)

        elif self.game_phase == 'GETTING_IP':
            draw_ip_input_box(self.screen, self.input_prompt, self.input_text, self.input_active, self.network_error)

        elif self.game_phase == 'CONNECTING':
            draw_connecting_screen(self.screen, self.connection_target_ip)

        elif self.game_phase == 'WAITING_FOR_STATE':
            # Simple waiting message (already handled in _update_waiting_for_state)
            self.screen.fill(CREAM)
            wait_text = font.render("Waiting for host...", True, BLACK)
            wait_rect = wait_text.get_rect(center=(WIDTH//2, HEIGHT//2))
            self.screen.blit(wait_text, wait_rect)

        elif self.game_phase in ['ROLLING', 'ROLLING_ANIMATION', 'MOVING', 'GAME_OVER']:
            # Draw Board Elements
            draw_board(self.screen, self.selected_point_index)
            draw_checkers(self.screen, self.game.board_points)
            draw_point_numbers(self.screen, self.valid_destination_indices)

            # Draw Sidebar
            draw_sidebar(self.screen, self.game_phase, self.game.current_player,
                         self.is_rolling_animation, self.animation_dice, self.game.dice,
                         self.game_start_time, self.game.board_points, self.connection_status,
                         self.game.white_borne_off, self.game.black_borne_off)

            # Draw Game Over screen if applicable
            if self.game_phase == 'GAME_OVER' and self.game.winner != 0:
                draw_game_over_screen(self.screen, self.game.winner)

        # Update the display
        pygame.display.flip()

    # --- Event Handling Sub-Methods ---
    def _handle_main_menu_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if OFFLINE_BUTTON_RECT.collidepoint(event.pos):
                self._start_offline_game()
            elif HOST_BUTTON_RECT.collidepoint(event.pos):
                self.game_phase = 'HOSTING_SETUP'
                self.active_input_box = None # Reset focus
                self._get_local_ips() # Fetch IPs for display
                 # Pre-fill host IP input with the first suggestion if empty
                if not self.host_ip_input and self.local_ips and self.local_ips[0] != "Could not determine IP":
                     self.host_ip_input = self.local_ips[0]
                self.host_port_input = str(self.host_port_default) # Reset port
            elif JOIN_BUTTON_RECT.collidepoint(event.pos):
                self.game_phase = 'GETTING_IP'
                self.network_error = None # Clear previous errors
                self.input_active = True
                self.input_text = "" # Clear previous input
                self.input_prompt = "Enter Host IP Address:"
                self.active_input_box = 'client_ip'
            elif EXIT_MENU_BUTTON_RECT.collidepoint(event.pos):
                self.running = False

    def _handle_hosting_setup_events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if START_HOST_BUTTON_RECT.collidepoint(event.pos):
                self._start_hosting_game()
            elif CANCEL_HOST_BUTTON_RECT.collidepoint(event.pos):
                self.game_phase = 'MAIN_MENU'
                self.network_error = None
                self.active_input_box = None
            elif HOST_IP_INPUT_RECT.collidepoint(event.pos):
                 self.active_input_box = 'ip'
            elif HOST_PORT_INPUT_RECT.collidepoint(event.pos):
                 self.active_input_box = 'port'
            else:
                 self.active_input_box = None

        if event.type == pygame.KEYDOWN:
             if self.active_input_box == 'ip':
                 if event.key == pygame.K_BACKSPACE:
                     self.host_ip_input = self.host_ip_input[:-1]
                 elif event.unicode.isalnum() or event.unicode == '.':
                     self.host_ip_input += event.unicode
             elif self.active_input_box == 'port':
                 if event.key == pygame.K_BACKSPACE:
                     self.host_port_input = self.host_port_input[:-1]
                 elif event.unicode.isdigit() and len(self.host_port_input) < 5:
                     self.host_port_input += event.unicode

    def _handle_waiting_events(self, event): # Used by WAITING_FOR_CLIENT
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if CANCEL_HOST_BUTTON_RECT.collidepoint(event.pos): # Same cancel button
                self._cancel_hosting_attempt()

    def _handle_getting_ip_events(self, event):
        if event.type == pygame.KEYDOWN:
            if self.input_active:
                if event.key == pygame.K_RETURN:
                    if self.input_text:
                        self._start_joining_game(self.input_text)
                    self.input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    self.input_text = self.input_text[:-1]
                elif event.unicode.isalnum() or event.unicode == '.':
                    self.input_text += event.unicode
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if JOIN_CANCEL_IP_BUTTON_RECT.collidepoint(event.pos):
                self.game_phase = 'MAIN_MENU'
                self.input_active = False
                self.network_error = None
                self.active_input_box = None
            elif JOIN_IP_BUTTON_RECT.collidepoint(event.pos):
                if self.input_text:
                    self._start_joining_game(self.input_text)
                self.input_active = False
            elif INPUT_BOX_RECT.collidepoint(event.pos):
                 self.input_active = True
            else:
                self.input_active = False

    def _handle_connecting_events(self, event):
         if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
             if JOIN_CANCEL_IP_BUTTON_RECT.collidepoint(event.pos):
                 self._cancel_connection_attempt()

    def _handle_in_game_events(self, event, is_my_turn):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not self.is_rolling_animation:
            # Sidebar Buttons
            if RESET_BUTTON_RECT.collidepoint(event.pos):
                 if self.network is None or self.player_id == 1:
                     self.game.reset()
                     self.game_start_time = pygame.time.get_ticks()
                     self.selected_point_index = None # Reset UI
                     self.valid_destination_indices.clear()
                     if self.network and self.player_id == 1:
                         self._send_game_state()
            elif BACK_BUTTON_RECT.collidepoint(event.pos):
                 self._go_back_to_menu()
            # Roll Dice Button
            elif is_my_turn and BUTTON_RECT.collidepoint(event.pos) and self.game_phase == 'ROLLING':
                 self._attempt_roll()
            # Board Clicks
            elif is_my_turn and self.game_phase == 'MOVING' and event.pos[0] < SIDEBAR_X_START:
                self._handle_click(event.pos)

    # --- Update Sub-Methods ---
    def _update_waiting_for_client(self):
        if self.server_thread and not self.server_thread.is_alive():
            if self.network and self.network.conn:
                self.player_id = 1
                self.connection_status = f"Hosting | Client Connected | You: White (P{self.player_id})"
                self.game.reset()
                self.game_start_time = pygame.time.get_ticks()
                self._send_game_state() # Send initial state
                self.game_phase = 'ROLLING'
                self.network_error = None
            else:
                self.network_error = "Failed to start server or accept connection."
                self.game_phase = 'HOSTING_SETUP'
                if self.network: self.network.close()
                self.network = None
            self.server_thread = None

    def _update_connecting(self):
        if self.connection_result == 'success':
            self.player_id = self.assigned_player_id_temp
            self.connection_status = f"Connected | You: Black (P{self.player_id})"
            self.game_phase = 'WAITING_FOR_STATE'
        elif self.connection_result == 'failed':
            self.network_error = f"Failed to connect to {self.connection_target_ip}"
            self.game_phase = 'GETTING_IP' # Go back to IP input

    def _update_waiting_for_state(self):
        if not self.network: # Should not happen, but safety check
             self.game_phase = 'MAIN_MENU'
             self.network_error = "Connection lost unexpectedly."
             return

        received_state = self.network.receive()
        if received_state:
            self.game.apply_state(received_state)
            self.game_start_time = pygame.time.get_ticks()
            self.game_phase = 'ROLLING'
            print("Initial state received, starting game.")
        # Note: Simple quit check is handled in _handle_events

    def _attempt_roll(self):
        """Handles the logic sequence for rolling the dice."""
        rolled = self.game.roll_dice() # Roll dice using game object
        if rolled:
            self.is_rolling_animation = True
            self.animation_start_time = pygame.time.get_ticks()
            self.animation_dice[:] = self.game.dice # Copy dice for animation

            if not self.game.can_player_move():
                print(f"No valid moves for {'White' if self.game.current_player == 1 else 'Black'} with roll {self.game.dice}. Starting feedback phase.")
                # Set flag: Turn will switch after animation/feedback
                self.pending_no_moves_switch = True
                # Start the animation anyway to show the dice
                self.game_phase = 'ROLLING_ANIMATION'
            else:
                self.game_phase = 'ROLLING_ANIMATION' # Proceed to animation
                self.pending_no_moves_switch = False # Ensure flag is reset if moves are possible

    def _go_back_to_menu(self):
        """Cleans up network and returns to the main menu."""
        if self.network:
            self.network.close()
            self.network = None
        self.game_phase = 'MAIN_MENU'
        self.network_error = None
        self.connection_status = "Offline"
        self.player_id = 0
        # Reset relevant UI states if needed
        self.selected_point_index = None
        self.valid_destination_indices.clear()
        self.input_active = False
        self.active_input_box = None

    def _cleanup(self):
        """Cleans up resources on application exit."""
        if self.network:
            self.network.close()
        pygame.quit()
        sys.exit()