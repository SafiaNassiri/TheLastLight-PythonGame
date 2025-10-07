class MessageManager:
    def __init__(self, font, fps=60, max_width=760):
        self.messages = []  # current messages
        self.timer = []     # frame timer for each message
        self.font = font
        self.fps = fps
        self.max_width = max_width  # maximum width for messages

    def add_message(self, text, duration_seconds=2): 
        # Add a message that lasts `duration_seconds` seconds.
        self.messages.append(text)
        self.timer.append(int(duration_seconds * self.fps))

    def update(self):
        for i in reversed(range(len(self.timer))):
            self.timer[i] -= 1
            if self.timer[i] <= 0:
                self.timer.pop(i)
                self.messages.pop(i)

    def wrap_text(self, text):
        """Return a list of lines wrapped to fit screen max_width."""
        words = text.split(' ')
        lines = []
        current_line = ''
        for word in words:
            test_line = current_line + (' ' if current_line else '') + word
            if self.font.size(test_line)[0] <= self.max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        return lines

    def draw(self, surface):
        y_offset = 20
        for msg in self.messages:
            wrapped_lines = self.wrap_text(msg)
            for line in wrapped_lines:
                surf_msg = self.font.render(line, True, (255, 255, 200))
                surface.blit(surf_msg, (20, y_offset))
                y_offset += surf_msg.get_height() + 4  # spacing between lines
