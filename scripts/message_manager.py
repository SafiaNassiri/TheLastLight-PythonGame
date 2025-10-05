class MessageManager:
    def __init__(self, font):
        self.messages = []  # current messages
        self.timer = []     # frame timer for each message
        self.font = font

    def add_message(self, text, duration=180):
        self.messages.append(text)
        self.timer.append(duration)

    def update(self):
        # decrement timers and remove expired messages
        for i in reversed(range(len(self.timer))):
            self.timer[i] -= 1
            if self.timer[i] <= 0:
                self.timer.pop(i)
                self.messages.pop(i)

    def draw(self, surface):
        for i, msg in enumerate(self.messages):
            surf_msg = self.font.render(msg, True, (255, 255, 200))
            surface.blit(surf_msg, (20, 20 + i*24))
