"""
Helicopter: the player-controlled vehicle. Moves vertically based on
held Up/Down keys.
"""

import pygame

THRUST = 0.4
MAX_SPEED = 6.0


class Helicopter:
    def __init__(self, x, y, width=40, height=24):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.vy = 0.0

    def handle_input(self, keys_pressed):
        if keys_pressed[pygame.K_UP]:
            # Moving down but pressing up: kill downward momentum so the turn is instant
            if self.vy > 0:
                self.vy = 0.0
            self.vy -= THRUST
        if keys_pressed[pygame.K_DOWN]:
            # Moving up but pressing down: kill upward momentum so the turn is instant
            if self.vy < 0:
                self.vy = 0.0
            self.vy += THRUST

        # Cap speed so vy can't grow forever while a key is held
        self.vy = max(-MAX_SPEED, min(MAX_SPEED, self.vy))

    def update(self, height_bound):
        self.y += self.vy

        # self.y is the center, so use half the height for the edges
        half_h = self.height / 2

        # Top boundary
        if self.y - half_h < 0:
            self.y = half_h
            self.vy = 0.0

        # Bottom boundary
        if self.y + half_h > height_bound:
            self.y = height_bound - half_h
            self.vy = 0.0

    def get_rect(self):
        return pygame.Rect(
            int(self.x - self.width / 2), int(self.y - self.height / 2),
            self.width, self.height,
        )
