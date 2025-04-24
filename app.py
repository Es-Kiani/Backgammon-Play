# app.py
import pygame, sys, yaml, time, random
from game import Game
from ui import *
import pickle

class App:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.game = Game()
        self.network = None
        self.player_times = {1: 0, -1: 0}
        self.last_time_update = pygame.time.get_ticks()

    def _attempt_roll(self):
        if self.game.roll_dice():
            self.last_time_update = pygame.time.get_ticks()

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if UNDO_BUTTON_RECT.collidepoint(event.pos):
                    if self.game.undo_move():
                        self.last_time_update = pygame.time.get_ticks()
                elif SAVE_BUTTON_RECT.collidepoint(event.pos):
                    self.save_game('savegame.dat')
                elif LOAD_BUTTON_RECT.collidepoint(event.pos):
                    self.load_game('savegame.dat')

    def run(self):
        self.running = True
        clock = pygame.time.Clock()
        while self.running:
            self._update_timers()
            self._handle_events()
            draw_sidebar(self.screen, self.player_times)
            pygame.display.flip()
            clock.tick(60)
        pygame.quit()
        sys.exit()

    def _update_timers(self):
        now = pygame.time.get_ticks()
        delta = now - self.last_time_update
        self.player_times[self.game.current_player] += delta
        self.last_time_update = now

    def save_game(self, filepath):
        try:
            with open(filepath, 'wb') as f:
                data = {
                    'history': self.game.history,
                    'player_times': self.player_times
                }
                pickle.dump(data, f)
        except Exception as e:
            print(f"Save failed: {e}")

    def load_game(self, filepath):
        try:
            with open(filepath, 'rb') as f:
                data = pickle.load(f)
            if isinstance(data, dict):
                if 'history' in data:
                    self.game.history = data['history']
                    self.game.apply_state(self.game.history[-1])
                if 'player_times' in data:
                    self.player_times = data['player_times']
                self.last_time_update = pygame.time.get_ticks()
        except Exception as e:
            print(f"Load failed: {e}")

if __name__ == '__main__':
    App().run()
