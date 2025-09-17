import pygame

class Orb:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 20, 20)
        self.color = (255, 255, 0)

    def draw(self, screen, camera_x=0, camera_y=0):
        pygame.draw.rect(screen, self.color, pygame.Rect(
            self.rect.x - camera_x,
            self.rect.y - camera_y,
            self.rect.width,
            self.rect.height
        ))
