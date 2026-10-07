"""
GameEngine: owns the helicopter and all obstacles.

Task 2: hitting the top or bottom wall of an obstacle ends the game
with a game over message. Flying through the gap is always safe.
Pressing R on the game over screen restarts.

Task 3: a distance score goes up while playing, is shown on screen
and on the game over screen, and resets to 0 on restart.
"""

import random

import pygame

from game.helicopter import Helicopter
from game.obstacle import Obstacle
from game.renderer import WIDTH, HEIGHT

SPAWN_INTERVAL_FRAMES = 90
GAP_HEIGHT = 150
WALL_WIDTH = 60
SCROLL_SPEED = 3
PIXELS_PER_DISTANCE_UNIT = 10   # 10 scrolled pixels = 1 point of distance


class GameEngine:
    def __init__(self):
        self.reset()

    def reset(self):
        """Put the game back to its starting state (used on start and restart)."""
        self.helicopter = Helicopter(x=100, y=HEIGHT / 2)
        self.obstacles = []
        self.frames_until_spawn = 0
        self.game_over = False
        self.distance_pixels = 0

    @property
    def distance(self):
        """Distance score shown to the player."""
        return self.distance_pixels // PIXELS_PER_DISTANCE_UNIT

    def _spawn_obstacle(self):
        margin = 60
        gap_y = random.randint(margin + GAP_HEIGHT // 2, HEIGHT - margin - GAP_HEIGHT // 2)
        self.obstacles.append(Obstacle(
            x=WIDTH, gap_y=gap_y, gap_height=GAP_HEIGHT,
            wall_width=WALL_WIDTH, screen_height=HEIGHT, speed=SCROLL_SPEED,
        ))

    def _check_collisions(self):
        """True if the helicopter overlaps any wall. The gap itself has no rect,
        so being inside the gap can never count as a hit."""
        heli_rect = self.helicopter.get_rect()
        for obstacle in self.obstacles:
            if heli_rect.colliderect(obstacle.get_top_rect()):
                return True
            if heli_rect.colliderect(obstacle.get_bottom_rect()):
                return True
        return False

    def handle_input(self, keys_pressed):
        if self.game_over:
            return
        self.helicopter.handle_input(keys_pressed)

    def handle_keydown(self, key):
        if self.game_over and key == pygame.K_r:
            self.reset()

    def update(self):
        if self.game_over:
            return  # freeze everything (including the score) until restart

        self.helicopter.update(HEIGHT)

        self.frames_until_spawn -= 1
        if self.frames_until_spawn <= 0:
            self._spawn_obstacle()
            self.frames_until_spawn = SPAWN_INTERVAL_FRAMES

        for obstacle in self.obstacles:
            obstacle.update()
        self.obstacles = [o for o in self.obstacles if not o.is_off_screen()]

        # The world scrolls SCROLL_SPEED pixels per frame, so that's how far we flew
        self.distance_pixels += SCROLL_SPEED

        if self._check_collisions():
            self.game_over = True

    def draw(self, surface, font):
        from game import renderer
        renderer.draw_scene(surface, self.helicopter, self.obstacles)
        renderer.draw_text(surface, font, f"Distance: {self.distance}", (10, 10))

        if self.game_over:
            renderer.draw_banner(surface, font, "GAME OVER - Press R to restart")
            # Final score on its own line, centered just below the banner
            line = f"Final distance: {self.distance}"
            text_w, text_h = font.size(line)
            pos = ((surface.get_width() - text_w) // 2, surface.get_height() // 2 + text_h)
            renderer.draw_text(surface, font, line, pos)
