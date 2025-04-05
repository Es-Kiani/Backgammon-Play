import pygame

# --- UI Constants ---
# Screen dimensions
SIDEBAR_WIDTH = 350
BOARD_AREA_WIDTH = 800 # Original board area width
WIDTH = BOARD_AREA_WIDTH + SIDEBAR_WIDTH
HEIGHT = 600

# Colors (RGB)
CREAM = (245, 245, 220)
BROWN = (139, 69, 19)
LIGHT_BROWN = (210, 180, 140) # Tan
MEDIUM_BROWN = (188, 143, 143) # Rosy Brown
BAR_BROWN = (127, 88, 88) 
SIDEBAR_BG = (50, 50, 50) # Dark background for sidebar
SIDEBAR_TEXT = (220, 220, 220) # Light text for sidebar
BLACK = (0, 0, 0)
WHITE = (235, 235, 235) # Changed to light grey instead of pure white
RED = (255, 0, 0)
GREEN = (0, 180, 0) # Brighter Green
YELLOW = (255, 255, 0)
BLUE = (100, 100, 255) # Lighter Blue for highlighting

# Board layout (relative to the board area, not the full window)
BOARD_MARGIN_X = 50
BOARD_MARGIN_Y = 50
BOARD_WIDTH = BOARD_AREA_WIDTH - 2 * BOARD_MARGIN_X
BOARD_HEIGHT = HEIGHT - 2 * BOARD_MARGIN_Y
POINT_WIDTH = BOARD_WIDTH / 13
POINT_HEIGHT = BOARD_HEIGHT * 0.4
BAR_WIDTH = POINT_WIDTH
CHECKER_RADIUS = int(POINT_WIDTH * 0.4)
BAR_CENTER_X = BOARD_MARGIN_X + 6 * POINT_WIDTH + BAR_WIDTH / 2

# --- Sidebar UI Constants ---
UI_MARGIN_X = 20 # Padding inside sidebar
UI_MARGIN_Y = 20
SIDEBAR_X_START = BOARD_AREA_WIDTH

# Button dimensions and position (Top of Sidebar)
BUTTON_WIDTH = SIDEBAR_WIDTH - 2 * UI_MARGIN_X
BUTTON_HEIGHT = 40
BUTTON_X = SIDEBAR_X_START + UI_MARGIN_X
BUTTON_Y = UI_MARGIN_Y + 40 # Place below title
BUTTON_RECT = pygame.Rect(BUTTON_X, BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT)

# Dice dimensions and position (Below button)
DICE_SIZE = 40
DICE_SPACING = 15
DICE_AREA_WIDTH = DICE_SIZE * 2 + DICE_SPACING
DICE_Y = BUTTON_Y + BUTTON_HEIGHT + UI_MARGIN_Y
DICE1_X = SIDEBAR_X_START + (SIDEBAR_WIDTH - DICE_AREA_WIDTH) // 2
DICE2_X = DICE1_X + DICE_SIZE + DICE_SPACING

# Info text positions
INFO_START_Y = DICE_Y + DICE_SIZE + UI_MARGIN_Y
INFO_LINE_HEIGHT = 30

# Button Positions (Continued)
# Position buttons relative to the bottom of the sidebar
BACK_BUTTON_Y = HEIGHT - UI_MARGIN_Y - BUTTON_HEIGHT
RESET_BUTTON_Y = BACK_BUTTON_Y - UI_MARGIN_Y // 2 - BUTTON_HEIGHT
RESET_BUTTON_RECT = pygame.Rect(BUTTON_X, RESET_BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT)
BACK_BUTTON_RECT = pygame.Rect(BUTTON_X, BACK_BUTTON_Y, BUTTON_WIDTH, BUTTON_HEIGHT)

# Point number constants
POINT_NUM_Y_OFFSET = 15 # Offset from board edge

# --- Fonts (Initialize once) ---
pygame.font.init() # Explicitly initialize font module
font = pygame.font.Font(None, 36) # Main font
small_font = pygame.font.Font(None, 24) # For point numbers, sidebar info
title_font = pygame.font.Font(None, 48) # For sidebar title

# --- Load and Scale Background Image ---
main_menu_background = None # Initialize globally

def load_background():
    """Loads and scales the background image. Call after display setup."""
    global main_menu_background
    try:
        raw_background = pygame.image.load("background.png").convert()
        main_menu_background = pygame.transform.scale(raw_background, (WIDTH, HEIGHT))
    except pygame.error as e:
        print(f"Error loading background.png: {e}")
        print("Using default background color instead.")
        main_menu_background = None # Fallback if loading fails

# --- Main Menu Constants ---
MENU_BUTTON_WIDTH = 250
MENU_BUTTON_HEIGHT = 50
MENU_Y_START = HEIGHT // 2 - MENU_BUTTON_HEIGHT * 1.5 - 20 # Start position for buttons
MENU_BUTTON_SPACING = 20
HOST_BUTTON_WIDTH = 180 # Slightly smaller buttons (Moved definition here)
MENU_CENTER_X = WIDTH // 2 # Center on the whole window for menu

OFFLINE_BUTTON_RECT = pygame.Rect(0, 0, MENU_BUTTON_WIDTH, MENU_BUTTON_HEIGHT)
OFFLINE_BUTTON_RECT.center = (MENU_CENTER_X, MENU_Y_START)

HOST_BUTTON_RECT = pygame.Rect(0, 0, MENU_BUTTON_WIDTH, MENU_BUTTON_HEIGHT)
HOST_BUTTON_RECT.center = (MENU_CENTER_X, MENU_Y_START + MENU_BUTTON_HEIGHT + MENU_BUTTON_SPACING)

JOIN_BUTTON_RECT = pygame.Rect(0, 0, MENU_BUTTON_WIDTH, MENU_BUTTON_HEIGHT)
JOIN_BUTTON_RECT.center = (MENU_CENTER_X, MENU_Y_START + 2 * (MENU_BUTTON_HEIGHT + MENU_BUTTON_SPACING))

EXIT_MENU_BUTTON_RECT = pygame.Rect(0, 0, MENU_BUTTON_WIDTH, MENU_BUTTON_HEIGHT)
EXIT_MENU_BUTTON_RECT.center = (MENU_CENTER_X, MENU_Y_START + 3 * (MENU_BUTTON_HEIGHT + MENU_BUTTON_SPACING))

# --- IP Input Box Constants ---
INPUT_BOX_WIDTH = 400
INPUT_BOX_HEIGHT = 50
INPUT_BOX_RECT = pygame.Rect(0, 0, INPUT_BOX_WIDTH, INPUT_BOX_HEIGHT)
INPUT_BOX_RECT.center = (WIDTH // 2, HEIGHT // 2 + 50) # Position lower than menu center
INPUT_PROMPT_Y_OFFSET = 30

# Join IP Screen Button Constants (Shared width/height with Host Cancel for simplicity)
JOIN_CANCEL_BUTTON_Y = INPUT_BOX_RECT.bottom + 40
JOIN_IP_BUTTON_RECT = pygame.Rect(0, 0, HOST_BUTTON_WIDTH, MENU_BUTTON_HEIGHT)
JOIN_CANCEL_IP_BUTTON_RECT = pygame.Rect(0, 0, HOST_BUTTON_WIDTH, MENU_BUTTON_HEIGHT)
JOIN_IP_BUTTON_RECT.center = (MENU_CENTER_X - HOST_BUTTON_WIDTH // 2 - MENU_BUTTON_SPACING, JOIN_CANCEL_BUTTON_Y)
JOIN_CANCEL_IP_BUTTON_RECT.center = (MENU_CENTER_X + HOST_BUTTON_WIDTH // 2 + MENU_BUTTON_SPACING, JOIN_CANCEL_BUTTON_Y)

# --- Hosting Setup Screen Constants ---
HOST_INFO_Y_START = HEIGHT // 5 # Move info higher
HOST_INPUT_WIDTH = 300
HOST_IP_INPUT_RECT = pygame.Rect(0, 0, HOST_INPUT_WIDTH, INPUT_BOX_HEIGHT)
HOST_IP_INPUT_RECT.center = (MENU_CENTER_X, HOST_INFO_Y_START + 180)
HOST_PORT_INPUT_RECT = pygame.Rect(0, 0, HOST_INPUT_WIDTH // 2, INPUT_BOX_HEIGHT) # Port input smaller
HOST_PORT_INPUT_RECT.center = (MENU_CENTER_X, HOST_INFO_Y_START + 260)

HOST_BUTTON_Y_START = HOST_PORT_INPUT_RECT.bottom + 40 # Position buttons below input
START_HOST_BUTTON_RECT = pygame.Rect(0, 0, HOST_BUTTON_WIDTH, MENU_BUTTON_HEIGHT)
START_HOST_BUTTON_RECT.center = (MENU_CENTER_X - HOST_BUTTON_WIDTH // 2 - MENU_BUTTON_SPACING, HOST_BUTTON_Y_START)
CANCEL_HOST_BUTTON_RECT = pygame.Rect(0, 0, HOST_BUTTON_WIDTH, MENU_BUTTON_HEIGHT)
CANCEL_HOST_BUTTON_RECT.center = (MENU_CENTER_X + HOST_BUTTON_WIDTH // 2 + MENU_BUTTON_SPACING, HOST_BUTTON_Y_START)

# --- UI Drawing Functions ---

def get_point_rect(point_index):
    """Calculates the bounding box for drawing checkers on a point or the bar."""
    # IMPORTANT: This function uses the board area coordinates, not the full window width
    x, y, w, h = 0, 0, POINT_WIDTH, POINT_HEIGHT

    if 0 <= point_index <= 11: # Bottom row
        y = HEIGHT - BOARD_MARGIN_Y - POINT_HEIGHT
        if point_index <= 5: # Bottom right quadrant (Points 1-6)
            x = BOARD_AREA_WIDTH - BOARD_MARGIN_X - (point_index + 1) * POINT_WIDTH
        else: # Bottom left quadrant (Points 7-12)
            x = BOARD_MARGIN_X + (11 - point_index) * POINT_WIDTH
        h = POINT_HEIGHT
    elif 12 <= point_index <= 23: # Top row
        y = BOARD_MARGIN_Y
        if point_index <= 17: # Top left quadrant (Points 13-18)
             x = BOARD_MARGIN_X + (point_index - 12) * POINT_WIDTH
        else: # Top right quadrant (Points 19-24)
             x = BOARD_AREA_WIDTH - BOARD_MARGIN_X - (24 - point_index) * POINT_WIDTH
        h = POINT_HEIGHT
    # Handle bar positions
    elif point_index == 24: # White bar
        x = BAR_CENTER_X - BAR_WIDTH / 2
        y = HEIGHT - BOARD_MARGIN_Y - POINT_HEIGHT
        w = BAR_WIDTH
        h = POINT_HEIGHT
    elif point_index == 25: # Black bar
        x = BAR_CENTER_X - BAR_WIDTH / 2
        y = BOARD_MARGIN_Y
        w = BAR_WIDTH
        h = POINT_HEIGHT

    return pygame.Rect(x, y, w, h)

def draw_pip(surface, x, y, size=5):
    """Draw a single pip (dot) on a die."""
    pygame.draw.circle(surface, BLACK, (x, y), size)

def draw_die(surface, x, y, value, size=DICE_SIZE):
    """Draw a single die with the specified value."""
    # Draw die background
    die_rect = pygame.Rect(x, y, size, size)
    pygame.draw.rect(surface, WHITE, die_rect, border_radius=5)
    pygame.draw.rect(surface, BLACK, die_rect, 2, border_radius=5)

    # Calculate pip positions
    pip_size = size // 8
    margin = size // 4
    center = size // 2

    # Pip coordinates dictionary for clarity
    pip_pos = {
        'tl': (x + margin, y + margin),
        'tr': (x + size - margin, y + margin),
        'ml': (x + margin, y + center),
        'mc': (x + center, y + center),
        'mr': (x + size - margin, y + center),
        'bl': (x + margin, y + size - margin),
        'br': (x + size - margin, y + size - margin),
    }

    # Draw pips based on value
    if value == 1: draw_pip(surface, *pip_pos['mc'], pip_size)
    elif value == 2:
        draw_pip(surface, *pip_pos['tl'], pip_size); draw_pip(surface, *pip_pos['br'], pip_size)
    elif value == 3:
        draw_pip(surface, *pip_pos['tl'], pip_size); draw_pip(surface, *pip_pos['mc'], pip_size); draw_pip(surface, *pip_pos['br'], pip_size)
    elif value == 4:
        draw_pip(surface, *pip_pos['tl'], pip_size); draw_pip(surface, *pip_pos['tr'], pip_size);
        draw_pip(surface, *pip_pos['bl'], pip_size); draw_pip(surface, *pip_pos['br'], pip_size)
    elif value == 5:
        draw_pip(surface, *pip_pos['tl'], pip_size); draw_pip(surface, *pip_pos['tr'], pip_size);
        draw_pip(surface, *pip_pos['mc'], pip_size);
        draw_pip(surface, *pip_pos['bl'], pip_size); draw_pip(surface, *pip_pos['br'], pip_size)
    elif value == 6:
        draw_pip(surface, *pip_pos['tl'], pip_size); draw_pip(surface, *pip_pos['tr'], pip_size);
        draw_pip(surface, *pip_pos['ml'], pip_size); draw_pip(surface, *pip_pos['mr'], pip_size);
        draw_pip(surface, *pip_pos['bl'], pip_size); draw_pip(surface, *pip_pos['br'], pip_size)

def calculate_blocked_points(board_points):
    """Calculates the number of blocked points for each player."""
    white_blocked = 0
    black_blocked = 0
    for i in range(24):
        if board_points[i] > 1: # White has 2 or more
            white_blocked += 1
        elif board_points[i] < -1: # Black has 2 or more
            black_blocked += 1
    return white_blocked, black_blocked

def draw_sidebar(screen, game_phase, current_player, is_rolling_animation, animation_dice, dice, game_start_time, board_points, connection_status, white_borne_off, black_borne_off):
    """Draws the sidebar background and all UI elements within it."""
    sidebar_rect = pygame.Rect(SIDEBAR_X_START, 0, SIDEBAR_WIDTH, HEIGHT)
    pygame.draw.rect(screen, SIDEBAR_BG, sidebar_rect)
    pygame.draw.line(screen, BLACK, (SIDEBAR_X_START, 0), (SIDEBAR_X_START, HEIGHT), 2)

    # --- Title ---
    title_pos = (SIDEBAR_X_START + SIDEBAR_WIDTH // 2, UI_MARGIN_Y + 10) # Increased Y offset slightly
    # Draw shadow first
    title_shadow = title_font.render("Backgammon", True, BLACK)
    title_shadow_rect = title_shadow.get_rect(center=(title_pos[0] + 2, title_pos[1] + 2)) # Offset shadow
    screen.blit(title_shadow, title_shadow_rect)
    # Draw main text
    title_surf = title_font.render("Backgammon", True, CREAM)
    title_rect = title_surf.get_rect(center=title_pos)
    screen.blit(title_surf, title_rect)

    # --- Draw roll button ---
    button_color = GREEN if game_phase == 'ROLLING' else LIGHT_BROWN
    pygame.draw.rect(screen, button_color, BUTTON_RECT, border_radius=10)
    pygame.draw.rect(screen, BLACK, BUTTON_RECT, 2, border_radius=10)
    button_text = font.render("Roll Dice", True, BLACK if game_phase == 'ROLLING' else SIDEBAR_TEXT)
    text_rect = button_text.get_rect(center=BUTTON_RECT.center)
    screen.blit(button_text, text_rect)

    # --- Draw dice ---
    if is_rolling_animation:
        draw_die(screen, DICE1_X, DICE_Y, animation_dice[0])
        draw_die(screen, DICE2_X, DICE_Y, animation_dice[1])
    elif dice[0] is not None:
        draw_die(screen, DICE1_X, DICE_Y, dice[0])
        draw_die(screen, DICE2_X, DICE_Y, dice[1])

    # --- Draw Turn/Phase Info ---
    y_pos = INFO_START_Y
    turn_text_str = f"Turn: {'White' if current_player == 1 else 'Black'}"
    turn_color = WHITE if current_player == 1 else BLACK
    turn_text = small_font.render(turn_text_str, True, SIDEBAR_TEXT)
    turn_rect = turn_text.get_rect(left=SIDEBAR_X_START + UI_MARGIN_X, top=y_pos)
    screen.blit(turn_text, turn_rect)
    # Small indicator color block
    pygame.draw.rect(screen, turn_color, (turn_rect.right + 5, y_pos + 4, 15, 15))

    y_pos += INFO_LINE_HEIGHT
    phase_text_str = f"Phase: {game_phase}"
    phase_text = small_font.render(phase_text_str, True, SIDEBAR_TEXT)
    phase_rect = phase_text.get_rect(left=SIDEBAR_X_START + UI_MARGIN_X, top=y_pos)
    screen.blit(phase_text, phase_rect)

    # --- Draw "No Moves" message if applicable ---
    if game_phase == 'NO_MOVES_FEEDBACK':
        y_pos += INFO_LINE_HEIGHT * 0.5 # Small gap
        no_moves_text = small_font.render("No valid moves!", True, RED)
        no_moves_rect = no_moves_text.get_rect(left=SIDEBAR_X_START + UI_MARGIN_X, top=y_pos)
        screen.blit(no_moves_text, no_moves_rect)

    # --- Draw Connection Status ---
    y_pos += INFO_LINE_HEIGHT
    status_text = small_font.render(connection_status, True, YELLOW)
    status_rect = status_text.get_rect(left=SIDEBAR_X_START + UI_MARGIN_X, top=y_pos)
    screen.blit(status_text, status_rect)

    # --- Draw Blocked Points Info ---
    y_pos += INFO_LINE_HEIGHT * 1.5 # Add extra space
    white_blocked, black_blocked = calculate_blocked_points(board_points)

    blocked_title = small_font.render("Blocked Points:", True, SIDEBAR_TEXT)
    blocked_title_rect = blocked_title.get_rect(left=SIDEBAR_X_START + UI_MARGIN_X, top=y_pos)
    screen.blit(blocked_title, blocked_title_rect)

    y_pos += INFO_LINE_HEIGHT
    white_blocked_text = small_font.render(f"- White: {white_blocked}", True, WHITE)
    white_blocked_rect = white_blocked_text.get_rect(left=SIDEBAR_X_START + UI_MARGIN_X + 10, top=y_pos)
    screen.blit(white_blocked_text, white_blocked_rect)

    y_pos += INFO_LINE_HEIGHT
    black_blocked_text = small_font.render(f"- Black: {black_blocked}", True, SIDEBAR_TEXT) # Use sidebar text for black
    black_blocked_rect = black_blocked_text.get_rect(left=SIDEBAR_X_START + UI_MARGIN_X + 10, top=y_pos)
    screen.blit(black_blocked_text, black_blocked_rect)

    # --- Draw Borne Off Info ---
    y_pos += INFO_LINE_HEIGHT * 1.5 # Add extra space
    borne_off_title = small_font.render("Borne Off:", True, SIDEBAR_TEXT)
    borne_off_title_rect = borne_off_title.get_rect(left=SIDEBAR_X_START + UI_MARGIN_X, top=y_pos)
    screen.blit(borne_off_title, borne_off_title_rect)

    y_pos += INFO_LINE_HEIGHT
    white_borne_text = small_font.render(f"- White: {white_borne_off}", True, WHITE)
    white_borne_rect = white_borne_text.get_rect(left=SIDEBAR_X_START + UI_MARGIN_X + 10, top=y_pos)
    screen.blit(white_borne_text, white_borne_rect)

    y_pos += INFO_LINE_HEIGHT
    black_borne_text = small_font.render(f"- Black: {black_borne_off}", True, SIDEBAR_TEXT)
    black_borne_rect = black_borne_text.get_rect(left=SIDEBAR_X_START + UI_MARGIN_X + 10, top=y_pos)
    screen.blit(black_borne_text, black_borne_rect)

    # --- Draw Timer ---
    y_pos += INFO_LINE_HEIGHT * 1.5
    elapsed_ticks = pygame.time.get_ticks() - game_start_time
    elapsed_seconds = elapsed_ticks // 1000
    minutes = elapsed_seconds // 60
    seconds = elapsed_seconds % 60
    timer_text_str = f"Time: {minutes:02d}:{seconds:02d}"
    timer_text = small_font.render(timer_text_str, True, SIDEBAR_TEXT)
    timer_rect = timer_text.get_rect(left=SIDEBAR_X_START + UI_MARGIN_X, top=y_pos)
    screen.blit(timer_text, timer_rect)

    # --- Draw Reset Button ---
    reset_color = (200, 100, 100) # Reddish
    pygame.draw.rect(screen, reset_color, RESET_BUTTON_RECT, border_radius=10)
    pygame.draw.rect(screen, BLACK, RESET_BUTTON_RECT, 2, border_radius=10)
    reset_btn_text = font.render("Reset", True, BLACK)
    reset_text_rect = reset_btn_text.get_rect(center=RESET_BUTTON_RECT.center)
    screen.blit(reset_btn_text, reset_text_rect)

    # --- Draw Back to Menu Button ---
    exit_color = (150, 150, 150) # Grayish
    pygame.draw.rect(screen, exit_color, BACK_BUTTON_RECT, border_radius=10)
    pygame.draw.rect(screen, BLACK, BACK_BUTTON_RECT, 2, border_radius=10)
    exit_btn_text = font.render("Back to Menu", True, BLACK)
    exit_text_rect = exit_btn_text.get_rect(center=BACK_BUTTON_RECT.center)
    screen.blit(exit_btn_text, exit_text_rect)

def draw_point_numbers(screen, valid_destination_indices):
    """Draws the point numbers (1-24) above/below the board."""
    for i in range(24):
        point_rect = get_point_rect(i)
        # Map index (0-23) to standard point number (1-24)
        if 0 <= i <= 5: point_number = i + 1        # Bottom right 1-6
        elif 6 <= i <= 11: point_number = i + 1    # Bottom left 7-12
        elif 12 <= i <= 17: point_number = i + 1   # Top left 13-18
        else: point_number = i + 1                 # Top right 19-24

        text_color = BLACK

        # Highlight if it's a valid destination
        if i in valid_destination_indices:
            text_color = GREEN

        number_text = small_font.render(str(point_number), True, text_color)
        number_rect = number_text.get_rect()
        number_rect.centerx = point_rect.centerx

        if 0 <= i <= 11: # Bottom row
            number_rect.top = HEIGHT - BOARD_MARGIN_Y + POINT_NUM_Y_OFFSET
        else: # Top row
            number_rect.bottom = BOARD_MARGIN_Y - POINT_NUM_Y_OFFSET

        screen.blit(number_text, number_rect)

def draw_game_over_screen(screen, winner_player):
    """Draws the game over message centered on the board area."""
    overlay_color = (0, 0, 0, 180) # Semi-transparent black overlay
    overlay_surface = pygame.Surface((BOARD_AREA_WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay_surface.fill(overlay_color)
    screen.blit(overlay_surface, (0, 0))

    # "Game Over!" message
    msg1_font = pygame.font.Font(None, 100)
    msg1_text = msg1_font.render("Game Over!", True, YELLOW)
    msg1_rect = msg1_text.get_rect(centerx=BOARD_AREA_WIDTH // 2, centery=HEIGHT // 2 - 40)
    screen.blit(msg1_text, msg1_rect)

    # Winner message
    winner_color_name = "White" if winner_player == 1 else "Black"
    winner_color_rgb = WHITE if winner_player == 1 else BLACK
    msg2_font = pygame.font.Font(None, 60)
    msg2_text = msg2_font.render(f"{winner_color_name} Wins!", True, winner_color_rgb)
    msg2_rect = msg2_text.get_rect(centerx=BOARD_AREA_WIDTH // 2, centery=HEIGHT // 2 + 40)
    # Add background rect for black text visibility
    if winner_player == -1:
        bg_rect = msg2_rect.inflate(10, 10)
        pygame.draw.rect(screen, CREAM, bg_rect, border_radius=5)

    screen.blit(msg2_text, msg2_rect)

def draw_board(screen, selected_point_index):
    """Draws the Backgammon board background, points, and selection highlight."""
    # Board area is drawn within the 0 to BOARD_AREA_WIDTH part of the screen
    screen.fill(CREAM, (0, 0, BOARD_AREA_WIDTH, HEIGHT)) # Fill only the board area

    # Draw main board area rectangle
    board_rect = pygame.Rect(BOARD_MARGIN_X, BOARD_MARGIN_Y, BOARD_WIDTH, BOARD_HEIGHT)
    pygame.draw.rect(screen, MEDIUM_BROWN, board_rect)

    # Draw the bar
    bar_x = BOARD_MARGIN_X + 6 * POINT_WIDTH
    bar_rect = pygame.Rect(bar_x, BOARD_MARGIN_Y, BAR_WIDTH, BOARD_HEIGHT)
    pygame.draw.rect(screen, BAR_BROWN, bar_rect) # Match the main board color

    # Draw the points (triangles)
    for i in range(24):
        point_rect = get_point_rect(i)
        color = LIGHT_BROWN if i % 2 == 0 else CREAM
        if i >= 12:
            color = CREAM if i % 2 == 0 else LIGHT_BROWN

        # Define triangle vertices based on row
        if 0 <= i <= 11: # Bottom row points up
            p1 = (point_rect.left, point_rect.bottom)
            p2 = (point_rect.right, point_rect.bottom)
            p3 = (point_rect.centerx, point_rect.top)
        else: # Top row points down
            p1 = (point_rect.left, point_rect.top)
            p2 = (point_rect.right, point_rect.top)
            p3 = (point_rect.centerx, point_rect.bottom)

        pygame.draw.polygon(screen, color, [p1, p2, p3])
        pygame.draw.polygon(screen, BLACK, [p1, p2, p3], 1)

    # Draw selection highlight
    if selected_point_index is not None:
        highlight_rect = get_point_rect(selected_point_index)
        # Adjust highlight for bar
        if selected_point_index == 24: # White bar
            highlight_rect = pygame.Rect(BAR_CENTER_X - CHECKER_RADIUS, HEIGHT - BOARD_MARGIN_Y - POINT_HEIGHT, CHECKER_RADIUS*2, POINT_HEIGHT)
        elif selected_point_index == 25: # Black bar
            highlight_rect = pygame.Rect(BAR_CENTER_X - CHECKER_RADIUS, BOARD_MARGIN_Y, CHECKER_RADIUS*2, POINT_HEIGHT)

        pygame.draw.rect(screen, YELLOW, highlight_rect, 3)

def draw_checkers(screen, board_points):
    """Draws the checkers on their respective points and the bar."""
    # Coordinates are relative to the board area
    max_checkers_display = 5

    # Draw checkers on points 0-23
    for i in range(24):
        num_checkers = board_points[i]
        if num_checkers == 0:
            continue

        color = WHITE if num_checkers > 0 else BLACK
        abs_num = abs(num_checkers)
        point_rect = get_point_rect(i)

        for j in range(min(abs_num, max_checkers_display)):
            # Calculate checker position within the point
            if 0 <= i <= 11: # Bottom row - stack upwards
                checker_y = point_rect.bottom - CHECKER_RADIUS - (j * CHECKER_RADIUS * 1.8)
            else: # Top row - stack downwards
                checker_y = point_rect.top + CHECKER_RADIUS + (j * CHECKER_RADIUS * 1.8)
            checker_x = point_rect.centerx

            # Draw checker
            # Add a slight 3D effect
            highlight_color = tuple(min(c + 40, 255) for c in (color if color != BLACK else (50, 50, 50))) # Brighter version
            shadow_color = tuple(max(c - 40, 0) for c in color) # Darker version
            pygame.draw.circle(screen, shadow_color, (checker_x + 1, int(checker_y) + 1), CHECKER_RADIUS)
            pygame.draw.circle(screen, color, (checker_x, int(checker_y)), CHECKER_RADIUS)
            # Black border for white checkers, white border for black checkers
            border_color = BLACK if color == WHITE else WHITE
            pygame.draw.circle(screen, border_color, (checker_x, int(checker_y)), CHECKER_RADIUS, 2) # Thicker border
            pygame.draw.circle(screen, highlight_color, (checker_x, int(checker_y)), CHECKER_RADIUS - 2, 1) # Inner highlight

        # If more checkers than display limit, draw count
        if abs_num > max_checkers_display:
             count_y = checker_y - CHECKER_RADIUS if 0 <= i <= 11 else checker_y + CHECKER_RADIUS
             count_text = small_font.render(str(abs_num), True, RED)
             count_rect = count_text.get_rect(center=(checker_x, int(count_y)))
             screen.blit(count_text, count_rect)

    # Draw checkers on the bar (points 24 and 25)
    for bar_index, player_sign, base_y_factor in [(24, 1, 1), (25, -1, 0)]:
        num_checkers = board_points[bar_index]
        if num_checkers == 0:
            continue

        color = WHITE if player_sign > 0 else BLACK
        abs_num = abs(num_checkers)

        for j in range(min(abs_num, max_checkers_display)):
            # Calculate checker position on the bar
            if player_sign == 1: # White bar (bottom half)
                 checker_y = HEIGHT - BOARD_MARGIN_Y - CHECKER_RADIUS - (j * CHECKER_RADIUS * 1.8)
            else: # Black bar (top half)
                 checker_y = BOARD_MARGIN_Y + CHECKER_RADIUS + (j * CHECKER_RADIUS * 1.8)
            checker_x = BAR_CENTER_X

            # Draw checker
            # Add a slight 3D effect
            highlight_color = tuple(min(c + 40, 255) for c in (color if color != BLACK else (50, 50, 50))) # Brighter version
            shadow_color = tuple(max(c - 40, 0) for c in color) # Darker version
            pygame.draw.circle(screen, shadow_color, (int(checker_x) + 1, int(checker_y) + 1), CHECKER_RADIUS)
            pygame.draw.circle(screen, color, (int(checker_x), int(checker_y)), CHECKER_RADIUS)
            # Black border for white checkers, white border for black checkers
            border_color = BLACK if color == WHITE else WHITE
            pygame.draw.circle(screen, border_color, (int(checker_x), int(checker_y)), CHECKER_RADIUS, 2) # Thicker border
            pygame.draw.circle(screen, highlight_color, (int(checker_x), int(checker_y)), CHECKER_RADIUS - 2, 1) # Inner highlight

        # If more checkers than display limit, draw count
        if abs_num > max_checkers_display:
             count_y = checker_y - CHECKER_RADIUS if player_sign == 1 else checker_y + CHECKER_RADIUS
             count_text = small_font.render(str(abs_num), True, RED)
             count_rect = count_text.get_rect(center=(int(checker_x), int(count_y)))
             screen.blit(count_text, count_rect)

def draw_main_menu(screen):
    """Draws the main menu screen with options."""
    # Draw background image or fallback color
    if main_menu_background:
        screen.blit(main_menu_background, (0, 0))
    else:
        screen.fill(SIDEBAR_BG) # Fallback if image failed to load

    # --- Helper Function for Text Shadow (defined inside for locality) ---
    def draw_text_with_shadow(surface, text, font_obj, color, shadow_color, center_pos):
        # Shadow
        shadow_surf = font_obj.render(text, True, shadow_color)
        shadow_rect = shadow_surf.get_rect(center=(center_pos[0] + 2, center_pos[1] + 2))
        surface.blit(shadow_surf, shadow_rect)
        # Main Text
        text_surf = font_obj.render(text, True, color)
        text_rect = text_surf.get_rect(center=center_pos)
        surface.blit(text_surf, text_rect)

    # Title
    title_pos = (WIDTH // 2, HEIGHT // 6)
    draw_text_with_shadow(screen, "Backgammon", title_font, CREAM, BLACK, title_pos)

    # --- Buttons with Transparency and Text Shadow ---
    # Define semi-transparent colors (R, G, B, Alpha)
    TRANS_GREEN = (0, 180, 0, 180)
    TRANS_BLUE = (100, 100, 255, 180)
    TRANS_YELLOW = (255, 255, 0, 180)
    TRANS_RED = (255, 0, 0, 180)

    # Offline Button
    pygame.draw.rect(screen, TRANS_GREEN, OFFLINE_BUTTON_RECT, border_radius=10)
    pygame.draw.rect(screen, BLACK, OFFLINE_BUTTON_RECT, 2, border_radius=10)
    draw_text_with_shadow(screen, "Play Offline", font, WHITE, BLACK, OFFLINE_BUTTON_RECT.center)

    # Host Button
    pygame.draw.rect(screen, TRANS_BLUE, HOST_BUTTON_RECT, border_radius=10)
    pygame.draw.rect(screen, BLACK, HOST_BUTTON_RECT, 2, border_radius=10)
    draw_text_with_shadow(screen, "Host Game (LAN)", font, WHITE, BLACK, HOST_BUTTON_RECT.center)

    # Join Button
    pygame.draw.rect(screen, TRANS_YELLOW, JOIN_BUTTON_RECT, border_radius=10)
    pygame.draw.rect(screen, BLACK, JOIN_BUTTON_RECT, 2, border_radius=10)
    draw_text_with_shadow(screen, "Join Game (LAN)", font, WHITE, BLACK, JOIN_BUTTON_RECT.center)

    # Exit Game Button (Menu)
    pygame.draw.rect(screen, TRANS_RED, EXIT_MENU_BUTTON_RECT, border_radius=10)
    pygame.draw.rect(screen, BLACK, EXIT_MENU_BUTTON_RECT, 2, border_radius=10)
    draw_text_with_shadow(screen, "Exit Game", font, WHITE, BLACK, EXIT_MENU_BUTTON_RECT.center)

def draw_hosting_setup_screen(screen, suggested_ips, host_ip_text, host_port_text, active_box, error_msg):
    """Draws the screen for setting up hosting."""
    screen.fill(SIDEBAR_BG)
    y_pos = HOST_INFO_Y_START # Starting Y for the title

    title_text = title_font.render("Host Game Setup", True, CREAM)
    title_rect = title_text.get_rect(center=(WIDTH // 2, y_pos))
    screen.blit(title_text, title_rect)
    y_pos += 70 # Space after title

    ip_text_header = small_font.render("Suggested Local IPs (for opponent to enter):", True, SIDEBAR_TEXT)
    ip_header_rect = ip_text_header.get_rect(center=(WIDTH // 2, y_pos))
    screen.blit(ip_text_header, ip_header_rect)
    y_pos += 35 # Space after header

    # Display suggested IPs
    for ip in suggested_ips:
        ip_text = small_font.render(ip, True, YELLOW)
        ip_rect = ip_text.get_rect(center=(WIDTH // 2, y_pos))
        screen.blit(ip_text, ip_rect)
        y_pos += INFO_LINE_HEIGHT # Move down for next IP
    
    # --- Position and Draw IP Input Box ---
    ip_input_y = y_pos + 40 # Add space after last suggested IP
    HOST_IP_INPUT_RECT.center = (MENU_CENTER_X, ip_input_y)
    ip_prompt_surf = small_font.render("Host on IP (leave blank to auto-select):", True, SIDEBAR_TEXT)
    ip_prompt_rect = ip_prompt_surf.get_rect(center=(HOST_IP_INPUT_RECT.centerx, HOST_IP_INPUT_RECT.top - 20))
    screen.blit(ip_prompt_surf, ip_prompt_rect)

    ip_border_color = YELLOW if active_box == 'ip' else WHITE
    pygame.draw.rect(screen, WHITE, HOST_IP_INPUT_RECT)
    pygame.draw.rect(screen, ip_border_color, HOST_IP_INPUT_RECT, 2, border_radius=3)
    ip_input_surf = font.render(host_ip_text, True, BLACK)
    screen.blit(ip_input_surf, (HOST_IP_INPUT_RECT.x + 10, HOST_IP_INPUT_RECT.y + (HOST_IP_INPUT_RECT.height - ip_input_surf.get_height()) // 2))

    # --- Position and Draw Port Input Box ---
    port_input_y = ip_input_y + INPUT_BOX_HEIGHT + 40 # Space below IP input
    HOST_PORT_INPUT_RECT.center = (MENU_CENTER_X, port_input_y)
    port_prompt_surf = small_font.render("Port:", True, SIDEBAR_TEXT)
    port_prompt_rect = port_prompt_surf.get_rect(center=(HOST_PORT_INPUT_RECT.centerx, HOST_PORT_INPUT_RECT.top - 20))
    screen.blit(port_prompt_surf, port_prompt_rect)

    port_border_color = YELLOW if active_box == 'port' else WHITE
    pygame.draw.rect(screen, WHITE, HOST_PORT_INPUT_RECT)
    pygame.draw.rect(screen, port_border_color, HOST_PORT_INPUT_RECT, 2, border_radius=3)
    port_input_surf = font.render(host_port_text, True, BLACK)
    screen.blit(port_input_surf, (HOST_PORT_INPUT_RECT.x + 10, HOST_PORT_INPUT_RECT.y + (HOST_PORT_INPUT_RECT.height - port_input_surf.get_height()) // 2))

    # --- Position and Draw Buttons ---
    button_y = port_input_y + INPUT_BOX_HEIGHT + 60 # Space below Port input
    START_HOST_BUTTON_RECT.center = (MENU_CENTER_X - HOST_BUTTON_WIDTH // 2 - MENU_BUTTON_SPACING, button_y)
    CANCEL_HOST_BUTTON_RECT.center = (MENU_CENTER_X + HOST_BUTTON_WIDTH // 2 + MENU_BUTTON_SPACING, button_y)

    # Draw Start Hosting Button
    pygame.draw.rect(screen, GREEN, START_HOST_BUTTON_RECT, border_radius=10)
    pygame.draw.rect(screen, BLACK, START_HOST_BUTTON_RECT, 2, border_radius=10)
    start_text = font.render("Start Hosting", True, BLACK)
    start_rect = start_text.get_rect(center=START_HOST_BUTTON_RECT.center)
    screen.blit(start_text, start_rect)

    # Draw Cancel Button
    pygame.draw.rect(screen, RED, CANCEL_HOST_BUTTON_RECT, border_radius=10)
    pygame.draw.rect(screen, BLACK, CANCEL_HOST_BUTTON_RECT, 2, border_radius=10)
    cancel_text = font.render("Cancel", True, BLACK)
    cancel_rect = cancel_text.get_rect(center=CANCEL_HOST_BUTTON_RECT.center)
    screen.blit(cancel_text, cancel_rect)

    # --- Draw Error Message ---
    if error_msg:
        error_surf = small_font.render(error_msg, True, RED)
        error_rect = error_surf.get_rect(center=(WIDTH // 2, button_y + MENU_BUTTON_HEIGHT + 30))
        screen.blit(error_surf, error_rect)

def draw_waiting_screen(screen):
    """Draws the screen shown while waiting for a connection."""
    screen.fill(SIDEBAR_BG)
    wait_text = title_font.render("Waiting for opponent...", True, YELLOW)
    wait_rect = wait_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(wait_text, wait_rect)
    
    # Cancel Button (Use same rect as hosting setup cancel)
    pygame.draw.rect(screen, RED, CANCEL_HOST_BUTTON_RECT, border_radius=10)
    pygame.draw.rect(screen, BLACK, CANCEL_HOST_BUTTON_RECT, 2, border_radius=10)
    cancel_text = font.render("Cancel", True, BLACK)
    cancel_rect = cancel_text.get_rect(center=CANCEL_HOST_BUTTON_RECT.center)
    screen.blit(cancel_text, cancel_rect)

def draw_ip_input_box(screen, prompt, input_text, is_active, error_msg):
    """Draws a graphical input box for IP address entry."""
    screen.fill(SIDEBAR_BG) # Fill background

    # Title
    title_text = title_font.render("Join Game", True, CREAM)
    title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 4))
    screen.blit(title_text, title_rect)
    
    # Prompt Text
    prompt_surf = font.render(prompt, True, SIDEBAR_TEXT) # Ensure visible on SIDEBAR_BG
    prompt_rect = prompt_surf.get_rect(center=(INPUT_BOX_RECT.centerx, INPUT_BOX_RECT.top - INPUT_PROMPT_Y_OFFSET))
    screen.blit(prompt_surf, prompt_rect)
    
    # Input Box Rect
    border_color = YELLOW if is_active else WHITE
    pygame.draw.rect(screen, WHITE, INPUT_BOX_RECT) # White background
    pygame.draw.rect(screen, border_color, INPUT_BOX_RECT, 2, border_radius=3)

    # Text inside box
    text_surface = font.render(input_text, True, BLACK)
    # TODO: Add blinking cursor if is_active
    screen.blit(text_surface, (INPUT_BOX_RECT.x + 10, INPUT_BOX_RECT.y + (INPUT_BOX_HEIGHT - text_surface.get_height()) // 2))

    # Cancel Button (Position below input box)
    pygame.draw.rect(screen, RED, JOIN_CANCEL_IP_BUTTON_RECT, border_radius=10)
    pygame.draw.rect(screen, BLACK, JOIN_CANCEL_IP_BUTTON_RECT, 2, border_radius=10)
    cancel_text = font.render("Cancel", True, BLACK)
    cancel_text_rect = cancel_text.get_rect(center=JOIN_CANCEL_IP_BUTTON_RECT.center)
    screen.blit(cancel_text, cancel_text_rect)

    # Join Button
    pygame.draw.rect(screen, GREEN, JOIN_IP_BUTTON_RECT, border_radius=10)
    pygame.draw.rect(screen, BLACK, JOIN_IP_BUTTON_RECT, 2, border_radius=10)
    join_text = font.render("Join", True, BLACK)
    join_text_rect = join_text.get_rect(center=JOIN_IP_BUTTON_RECT.center)
    screen.blit(join_text, join_text_rect)

    # Display connection error if any
    if error_msg:
        error_surf = small_font.render(error_msg, True, RED)
        error_rect = error_surf.get_rect(center=(WIDTH // 2, JOIN_CANCEL_IP_BUTTON_RECT.bottom + 30)) # Position below buttons
        screen.blit(error_surf, error_rect)

# --- Connecting Screen --- 
def draw_connecting_screen(screen, target_ip):
    """Draws the screen shown while attempting to connect to a host."""
    screen.fill(SIDEBAR_BG)
    y_pos = HEIGHT // 3

    # Connecting Text
    connecting_text = title_font.render(f"Connecting to {target_ip}...", True, YELLOW)
    connecting_rect = connecting_text.get_rect(center=(WIDTH // 2, y_pos))
    screen.blit(connecting_text, connecting_rect)

    # Cancel Button (Use Join Cancel Rect)
    pygame.draw.rect(screen, RED, JOIN_CANCEL_IP_BUTTON_RECT, border_radius=10)
    pygame.draw.rect(screen, BLACK, JOIN_CANCEL_IP_BUTTON_RECT, 2, border_radius=10)
    cancel_text = font.render("Cancel", True, BLACK)
    cancel_rect = cancel_text.get_rect(center=JOIN_CANCEL_IP_BUTTON_RECT.center)
    screen.blit(cancel_text, cancel_rect) 