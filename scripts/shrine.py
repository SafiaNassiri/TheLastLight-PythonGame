import pygame
import math

class Shrine:
    def __init__(self, x, y, image_path, max_light):
        self.image = pygame.image.load(image_path).convert_alpha()
        self.rect = self.image.get_rect(topleft=(x,y))
        self.light = 0
        self.max_light = max_light
        self.glow_timer = 0

        # Light radius phases
        self.light_phases = [64, 128, 192]
        self.phase_index = 0

    def add_light(self):
        self.light += 1
        if self.light > self.max_light:
            self.light = self.max_light
        self.update_phase()
        self.glow_timer = 30  # glow effect

    def update_phase(self):
        # Determine phase based on current light
        ratio = self.light / self.max_light
        if ratio <= 0.33:
            self.phase_index = 0
        elif ratio <= 0.66:
            self.phase_index = 1
        else:
            self.phase_index = 2

    @property
    def radius(self):
        return self.light_phases[self.phase_index]

    def update(self):
        if self.glow_timer > 0:
            self.glow_timer -= 1

    def draw(self, surface):
        surface.blit(self.image, self.rect.topleft)
        if self.glow_timer > 0:
            alpha = 128 + 127*math.sin(self.glow_timer*0.3)
            glow = pygame.Surface((self.rect.width,self.rect.height), pygame.SRCALPHA)
            glow.fill((255,255,200,int(alpha)))
            surface.blit(glow, self.rect.topleft)

    def draw_light_mask(self, surface):
        # Draw circular light area
        mask = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        mask.fill((0,0,0,200))  # fog color
        pygame.draw.circle(mask, (0,0,0,0), self.rect.center, self.radius)
        surface.blit(mask, (0,0))
