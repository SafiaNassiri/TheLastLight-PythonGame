import pygame
import math

class Orb:
    def __init__(self, x, y, image_path):
        self.image = pygame.image.load(image_path).convert_alpha()
        self.rect = self.image.get_rect(topleft=(x,y))
        self.collected = False
        self.float_timer = 0

    def check_collision(self, player_rect):
        if self.rect.colliderect(player_rect):
            self.collected = True
            return True
        return False

    def update(self):
        # simple float animation
        self.float_timer += 0.05
        self.offset_y = math.sin(self.float_timer) * 4

    def draw(self, surface):
        if not self.collected:
            surface.blit(self.image, (self.rect.x, self.rect.y + self.offset_y))
