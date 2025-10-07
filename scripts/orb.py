import pygame
import math

class Orb:
    def __init__(self, x, y, width=24, height=24):
        self.tile_x = x
        self.tile_y = y
        self.width = width
        self.height = height
        self.collected = False

        # Hover / float
        self.float_timer = 0
        self.offset_x = 0
        self.offset_y = 0
        self.hover_amplitude = 5
        self.hover_speed = 2

        # Pulsing inner circle
        self.pulse_timer = 0
        self.inner_min = width // 4
        self.inner_max = width // 2

        # Colors
        self.color = (178, 212, 221)      # main orb
        self.inner_color = (150, 190, 200) # darker, pulsing

    def check_collision(self, player_rect, tile_size=32):
        if not self.collected:
            rect = pygame.Rect(
                self.tile_x * tile_size,
                self.tile_y * tile_size,
                self.width,
                self.height
            )
            if rect.colliderect(player_rect):
                self.collected = True
                return True
        return False

    def update(self, dt=1.0):
        if not self.collected:
            # Hover offsets
            self.float_timer += self.hover_speed * dt
            self.offset_x = math.sin(self.float_timer) * self.hover_amplitude
            self.offset_y = math.cos(self.float_timer) * self.hover_amplitude

            # Inner pulse
            self.pulse_timer += dt * 3  # pulse speed
            self.inner_radius = self.inner_min + (self.inner_max - self.inner_min) * (0.5 + 0.5 * math.sin(self.pulse_timer))

    def draw(self, surface, camera_x=0, camera_y=0, tile_size=32):
        if not self.collected:
            # Pixel position
            px = self.tile_x * tile_size - camera_x + tile_size//2 + self.offset_x
            py = self.tile_y * tile_size - camera_y + tile_size//2 + self.offset_y

            # Main orb
            pygame.draw.circle(surface, self.color, (int(px), int(py)), self.width//2)

            # Inner pulsing circle
            pygame.draw.circle(surface, self.inner_color, (int(px), int(py)), int(self.inner_radius))
