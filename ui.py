# ui.py
import pygame

SIDEBAR_WIDTH = 350
BOARD_AREA_WIDTH = 800
WIDTH = BOARD_AREA_WIDTH + SIDEBAR_WIDTH
HEIGHT = 600
CREAM = (245, 245, 220)

UNDO_BUTTON_RECT = pygame.Rect(SIDEBAR_WIDTH//2, HEIGHT - 200, 150, 40)
SAVE_BUTTON_RECT = pygame.Rect(SIDEBAR_WIDTH//2, HEIGHT - 150, 150, 40)
LOAD_BUTTON_RECT = pygame.Rect(SIDEBAR_WIDTH//2, HEIGHT - 100, 150, 40)

def draw_sidebar(screen, player_times, *args, **kwargs):
    font = pygame.font.Font(None, 24)
    w_ms = player_times.get(1, 0)
    b_ms = player_times.get(-1, 0)
    w_m, w_s = divmod(w_ms // 1000, 60)
    b_m, b_s = divmod(b_ms // 1000, 60)
    x = BOARD_AREA_WIDTH + 10
    screen.blit(font.render(f"White Time: {w_m:02d}:{w_s:02d}", True, (0,0,0)), (x, 20))
    screen.blit(font.render(f"Black Time: {b_m:02d}:{b_s:02d}", True, (0,0,0)), (x, 50))

    pygame.draw.rect(screen, (200,200,200), UNDO_BUTTON_RECT)
    pygame.draw.rect(screen, (0,0,0), UNDO_BUTTON_RECT, 2)
    txt = pygame.font.Font(None, 24).render("Undo Move", True, (0,0,0))
    screen.blit(txt, UNDO_BUTTON_RECT.topleft)

    pygame.draw.rect(screen, (200,200,200), SAVE_BUTTON_RECT)
    pygame.draw.rect(screen, (0,0,0), SAVE_BUTTON_RECT, 2)
    txt2 = pygame.font.Font(None, 24).render("Save Game", True, (0,0,0))
    screen.blit(txt2, SAVE_BUTTON_RECT.topleft)

    pygame.draw.rect(screen, (200,200,200), LOAD_BUTTON_RECT)
    pygame.draw.rect(screen, (0,0,0), LOAD_BUTTON_RECT, 2)
    txt3 = pygame.font.Font(None, 24).render("Load Game", True, (0,0,0))
    screen.blit(txt3, LOAD_BUTTON_RECT.topleft)
