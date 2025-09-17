import pygame
import random
import math

class Enemy:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 40, 40)
        self.color = (255, 0, 0)
        self.speed = 2
        self.detection_radius = 150  # pixels

    def move(self, player, walls=[], world_width=2000, world_height=1200):
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        distance = math.hypot(dx, dy)

        if distance < self.detection_radius and distance != 0:
            # Move toward player
            self.rect.x += int(self.speed * dx / distance)
            self.rect.y += int(self.speed * dy / distance)
        else:
            # Random movement
            self.rect.x += random.choice([-1,0,1]) * self.speed
            self.rect.y += random.choice([-1,0,1]) * self.speed

        # Collisions with walls
        for wall in walls:
            if self.rect.colliderect(wall):
                if dx > 0: self.rect.right = wall.left
                elif dx < 0: self.rect.left = wall.right
                if dy > 0: self.rect.bottom = wall.top
                elif dy < 0: self.rect.top = wall.bottom

        # Keep enemy inside world bounds
        self.rect.x = max(0, min(self.rect.x, world_width - self.rect.width))
        self.rect.y = max(0, min(self.rect.y, world_height - self.rect.height))

    def draw(self, screen, camera_x=0, camera_y=0):
        pygame.draw.rect(screen, self.color, pygame.Rect(
            self.rect.x - camera_x,
            self.rect.y - camera_y,
            self.rect.width,
            self.rect.height
        ))
