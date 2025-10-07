import pygame

def draw_light(surface, position, radius_w, radius_h, intensity=100):
    light_surf = pygame.Surface((radius_w*2, radius_h*2), pygame.SRCALPHA)
    pygame.draw.ellipse(light_surf, (255, 255, 200, intensity), (0, 0, radius_w*2, radius_h*2))
    surface.blit(light_surf, (position[0]-radius_w, position[1]-radius_h), special_flags=pygame.BLEND_RGBA_SUB)
