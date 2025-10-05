import pygame
import math

class Orb:
    def __init__(self, x, y, image_path, row=2, tile_size=32):
        """
        x, y: tile coordinates
        image_path: path to orb sprite sheet
        row: 0-indexed row to use from the sheet
        tile_size: size of a single tile/frame
        """
        full_sheet = pygame.image.load(image_path).convert_alpha()
        sheet_width, sheet_height = full_sheet.get_size()
        cols = sheet_width // tile_size
        # select only the given row
        rect = pygame.Rect(0, row * tile_size, sheet_width, tile_size)
        self.image = full_sheet.subsurface(rect).copy()

        self.tile_size = tile_size
        self.rect = self.image.get_rect(topleft=(x * tile_size, y * tile_size))
        self.collected = False
        self.float_timer = 0
        self.offset_y = 0

    def check_collision(self, player_rect):
        if not self.collected and self.rect.colliderect(player_rect):
            self.collected = True
            return True
        return False

    def update(self, dt=1.0):
        self.float_timer += 0.05 * dt
        self.offset_y = math.sin(self.float_timer) * 4

    def draw(self, surface, camera_x=0, camera_y=0):
        if not self.collected:
            screen_x = self.rect.x - camera_x
            screen_y = self.rect.y - camera_y + self.offset_y
            surface.blit(self.image, (screen_x, screen_y))
