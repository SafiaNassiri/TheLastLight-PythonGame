import pygame

class Button:
    def __init__(self, text, x, y, w, h, font=None):
        self.text = text
        self.rect = pygame.Rect(x, y, w, h)
        self.font = font or pygame.font.SysFont(None, 32)

    def draw(self, screen, selected=False):
        mouse_pos = pygame.mouse.get_pos()
        hovered = self.rect.collidepoint(mouse_pos)
        color = (255, 255, 255) if hovered or selected else (180, 180, 180)
        surf = self.font.render(self.text, True, color)
        screen.blit(surf, self.rect.topleft)

    def handle_event(self, event, selected=False):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN and selected:
            return True
        return False
