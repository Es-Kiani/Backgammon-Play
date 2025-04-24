
import pygame

class PlayerTimers:
    def __init__(self):
        self.white_time = 0
        self.black_time = 0
        self.last_update = pygame.time.get_ticks()
        self.current_player = 1

    def switch_turn(self, new_player):
        now = pygame.time.get_ticks()
        elapsed = now - self.last_update
        if self.current_player == 1:
            self.white_time += elapsed
        else:
            self.black_time += elapsed
        self.current_player = new_player
        self.last_update = now

    def get_times(self):
        now = pygame.time.get_ticks()
        elapsed = now - self.last_update
        if self.current_player == 1:
            white_total = self.white_time + elapsed
            black_total = self.black_time
        else:
            white_total = self.white_time
            black_total = self.black_time + elapsed
        return white_total, black_total
