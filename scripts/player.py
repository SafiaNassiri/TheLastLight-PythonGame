import pygame, os

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, sprite_sheet, tilemap):
        super().__init__()
        self.tilemap = tilemap
        self.sprite_sheet_path = os.path.join("assets", "entities", "Player", "Satyr", sprite_sheet)
        self.sheet = pygame.image.load(self.sprite_sheet_path).convert_alpha()

        # animation setup
        self.animations = self.load_animations()
        self.current_animation = "idle"
        self.current_frame = 0
        self.frame_timer = 0
        self.frame_duration = 0.1  # seconds per frame

        self.image = self.animations[self.current_animation][0]
        self.rect = self.image.get_rect(topleft=(x, y))

        self.speed = 150
        self.dx = 0
        self.dy = 0

    def load_animations(self):
        sheet = self.sheet
        w, h = sheet.get_size()
        rows = 8
        frame_height = h // rows

        # Correct frame counts for each row (from your asset description)
        anim_data = {
            "idle": 6,
            "run": 8,
            "jump": 3,
            "fall": 3,
            "hurt": 4,
            "dead": 9,
            "stop": 3,
            "dash": 6
        }

        animations = {}
        y = 0
        for name, frame_count in anim_data.items():
            frames = []
            frame_width = w // frame_count  # only for this row
            for i in range(frame_count):
                rect = pygame.Rect(i * frame_width, y, frame_width, frame_height)
                frames.append(sheet.subsurface(rect))
            animations[name] = frames
            y += frame_height
        return animations

    def handle_input(self):
        keys = pygame.key.get_pressed()
        self.dx = (keys[pygame.K_d] - keys[pygame.K_a]) * self.speed
        self.dy = (keys[pygame.K_s] - keys[pygame.K_w]) * self.speed

        new_animation = "run" if self.dx != 0 or self.dy != 0 else "idle"
        if new_animation != self.current_animation:
            self.current_animation = new_animation
            self.current_frame = 0
            self.frame_timer = 0

    def update(self, dt):
        self.rect.x += self.dx * dt
        self.rect.y += self.dy * dt

        # Animation timing
        self.frame_timer += dt
        if self.frame_timer >= self.frame_duration:
            self.frame_timer = 0
            frames = self.animations[self.current_animation]
            self.current_frame = (self.current_frame + 1) % len(frames)
            self.image = frames[self.current_frame]

    def draw(self, surf, camera_x=0, camera_y=0):
        # Draw the player relative to the camera
        draw_pos = self.rect.move(-camera_x, -camera_y)
        surf.blit(self.image, draw_pos)
