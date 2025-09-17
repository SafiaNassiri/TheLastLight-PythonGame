import pygame

class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 40, 40)
        self.color = (0, 0, 255)
        self.speed = 5
        self.orbs_carried = 0
        self.light_radius = 250     # radius of light around player

    def move(self, keys, walls=[], world_width=2000, world_height=1200):
        dx, dy = 0, 0
        if keys[pygame.K_LEFT]:
            dx -= self.speed
        if keys[pygame.K_RIGHT]:
            dx += self.speed
        if keys[pygame.K_UP]:
            dy -= self.speed
        if keys[pygame.K_DOWN]:
            dy += self.speed

        # Move horizontally and check wall collisions
        self.rect.x += dx
        for wall in walls:
            if self.rect.colliderect(wall):
                if dx > 0:
                    self.rect.right = wall.left
                elif dx < 0:
                    self.rect.left = wall.right

        # Move vertically and check wall collisions
        self.rect.y += dy
        for wall in walls:
            if self.rect.colliderect(wall):
                if dy > 0:
                    self.rect.bottom = wall.top
                elif dy < 0:
                    self.rect.top = wall.bottom

        # Keep player inside world bounds
        self.rect.x = max(0, min(self.rect.x, world_width - self.rect.width))
        self.rect.y = max(0, min(self.rect.y, world_height - self.rect.height))

    def attack(self):
        print("Player attacks!")

    def draw(self, screen, camera_x=0, camera_y=0):
        # Create gradient light
        light_surface = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
        light_surface.fill((0, 0, 0, 255))  # start fully dark

        # Smooth radial gradient
        for radius in range(self.light_radius, 0, -1):
            alpha = int(255 * (1 - (radius / self.light_radius))**2)
            pygame.draw.circle(
                light_surface,
                (0, 0, 0, alpha),
                (self.rect.centerx - camera_x, self.rect.centery - camera_y),
                radius
            )

        screen.blit(light_surface, (0, 0))

        # Draw player on top of light
        pygame.draw.rect(screen, self.color, pygame.Rect(
            self.rect.x - camera_x,
            self.rect.y - camera_y,
            self.rect.width,
            self.rect.height
        ))
