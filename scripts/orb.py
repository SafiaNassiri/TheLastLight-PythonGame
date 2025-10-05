import pygame
import math

class Orb:
    def __init__(self, x, y, image_path, row=2, tile_size=32, anim_speed=0.15):
        """
        x, y: tile coordinates
        image_path: path to orb sprite sheet
        row: 0-indexed row to use from the sheet
        tile_size: size of a single frame in the sheet
        anim_speed: seconds per frame
        """
        full_sheet = pygame.image.load(image_path).convert_alpha()
        sheet_width, sheet_height = full_sheet.get_size()
        cols = sheet_width // tile_size

        # Extract frames from the given row
        self.frames = []
        for col in range(cols):
            rect = pygame.Rect(col * tile_size, row * tile_size, tile_size, tile_size)
            frame = full_sheet.subsurface(rect).copy()
            self.frames.append(frame)
        # Create forward-backward animation sequence
        self.frames = self.frames + self.frames[::-1][1:-1]

        self.frame_index = 0
        self.anim_timer = 0
        self.anim_speed = anim_speed

        self.tile_size = tile_size
        self.rect = self.frames[0].get_rect(topleft=(x * tile_size, y * tile_size))
        self.collected = False
        self.float_timer = 0
        self.offset_y = 0

    def check_collision(self, player_rect):
        if not self.collected and self.rect.colliderect(player_rect):
            self.collected = True
            return True
        return False

    def update(self, dt=1.0):
        if not self.collected:
            # Float animation
            self.float_timer += 0.05 * dt
            self.offset_y = math.sin(self.float_timer) * 4

            # Frame animation
            self.anim_timer += dt
            if self.anim_timer >= self.anim_speed:
                self.anim_timer = 0
                self.frame_index = (self.frame_index + 1) % len(self.frames)

    def draw(self, surface, camera_x=0, camera_y=0):
        if not self.collected:
            screen_x = self.rect.x - camera_x
            screen_y = self.rect.y - camera_y + self.offset_y
            surface.blit(self.frames[self.frame_index], (screen_x, screen_y))
