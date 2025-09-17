import pygame

class Shrine:
    def __init__(self, x, y, radius, total_orbs):
        self.x = x
        self.y = y
        self.radius = radius
        self.total_orbs = total_orbs
        self.collected_orbs = 0
        self.color = (100, 100, 100)  # starts dim gray
        self.milestones = [0.25, 0.5, 0.75, 1.0]
        self.triggered_messages = set()
        self.messages = [
            "A faint light flickers in the Shrine...",
            "The Shrine pulses with life again!",
            "Hope spreads across the land!",
            "The darkness recedes completely. Light returns!"
        ]
        self.font = pygame.font.SysFont(None, 28)

    def collect_orb(self):
        self.collected_orbs += 1
        intensity = min(255, int((self.collected_orbs / self.total_orbs) * 255))
        self.color = (intensity, intensity, 0)  # glowing yellow

    def check_milestones(self):
        messages_to_display = []
        fraction = self.collected_orbs / self.total_orbs
        for i, milestone in enumerate(self.milestones):
            if fraction >= milestone and i not in self.triggered_messages:
                messages_to_display.append(self.messages[i])
                self.triggered_messages.add(i)
        return messages_to_display

    # Updated draw method to accept camera offsets
    def draw(self, screen, camera_x=0, camera_y=0):
        pygame.draw.circle(screen, self.color, (self.x - camera_x, self.y - camera_y), self.radius)
        progress_text = self.font.render(f"{self.collected_orbs}/{self.total_orbs}", True, (255, 255, 255))
        screen.blit(progress_text, (
            self.x - camera_x - progress_text.get_width() // 2,
            self.y - camera_y - progress_text.get_height() // 2
        ))
