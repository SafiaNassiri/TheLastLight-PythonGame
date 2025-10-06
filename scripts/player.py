import pygame, os

ANIMATION_SPEED = 0.2  # seconds per frame

# Map movement direction to nearest sprite sheet row
DIR_TO_ROW = {
    (0, 1): 0,      # down
    (-1, 1): 1,     # left_down
    (-1, -1): 2,    # left_up
    (0, -1): 3,     # up
    (1, -1): 4,     # right_up
    (1, 1): 5       # right_down
}


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, tilemap):
        super().__init__()
        self.tilemap = tilemap

        # Sprite sheet info
        self.frame_width = 48
        self.frame_height = 64
        self.sheet_cols = 8
        self.sheet_rows = 6

        # Load sprite sheets
        base_path = os.path.join(os.getcwd(), "assets", "entities", "Player", "The Male adventurer - Free")
        self.sheets = {
            "idle": pygame.image.load(os.path.join(base_path, "idle.png")).convert_alpha(),
            "walk": pygame.image.load(os.path.join(base_path, "walk.png")).convert_alpha()
        }

        # Slice sheets into animations
        self.animations = {}
        directions = ["down", "left_down", "left_up", "up", "right_up", "right_down"]
        for anim_name, sheet in self.sheets.items():
            for row in range(self.sheet_rows):
                direction_name = directions[row]
                frames = []
                for col in range(self.sheet_cols):
                    frame = sheet.subsurface(
                        col * self.frame_width,
                        row * self.frame_height,
                        self.frame_width,
                        self.frame_height
                    )
                    # Scale to fit tile size
                    frame = pygame.transform.scale(frame, (96, 128))
                    frames.append(frame)
                self.animations[f"{anim_name}_{direction_name}"] = frames

        # Initial state
        self.current_animation = "idle_down"
        self.frame_index = 0
        self.animation_timer = 0
        self.is_moving = False

        self.image = self.animations[self.current_animation][0]
        self.rect = self.image.get_rect(topleft=(x, y))

        # Collision rect (hitbox) anchored to feet
        hitbox_width = 24
        hitbox_height = 16
        self.hitbox = pygame.Rect(
            self.rect.centerx - hitbox_width // 2,
            self.rect.bottom - hitbox_height - 28,
            hitbox_width,
            hitbox_height
        )

        # Movement
        self.speed = 300
        self.dx = 0
        self.dy = 0

        # Last vertical input for horizontal movement
        self.last_vertical = 1  # default down

    def handle_input(self):
        keys = pygame.key.get_pressed()
        self.dx = (keys[pygame.K_d] - keys[pygame.K_a])
        self.dy = (keys[pygame.K_s] - keys[pygame.K_w])
        self.is_moving = (self.dx != 0 or self.dy != 0)

        anim_prefix = "walk" if self.is_moving else "idle"

        # Determine direction for animation
        if self.is_moving:
            dx_norm = 0 if self.dx == 0 else (1 if self.dx > 0 else -1)
            dy_norm = 0 if self.dy == 0 else (1 if self.dy > 0 else -1)

            # Handle straight horizontal by picking diagonal frame
            if dx_norm != 0 and dy_norm == 0:
                dy_norm = self.last_vertical
            elif dy_norm != 0:
                self.last_vertical = dy_norm

            direction_row = DIR_TO_ROW.get((dx_norm, dy_norm), 0)
            directions = ["down", "left_down", "left_up", "up", "right_up", "right_down"]
            direction = directions[direction_row]
        else:
            direction = "down"

        self.current_animation = f"{anim_prefix}_{direction}"

        # Normalize diagonal speed
        if self.dx != 0 and self.dy != 0:
            inv = 1 / (2 ** 0.5)
            self.dx *= inv
            self.dy *= inv

    def update(self, dt):
        # Predict movement and check collisions
        new_hitbox = self.hitbox.copy()
        new_hitbox.x += self.dx * self.speed * dt
        if not self.tilemap.is_solid(new_hitbox):
            self.hitbox.x = new_hitbox.x
        else:
            print("[DEBUG] Collision on X-axis")

        new_hitbox = self.hitbox.copy()
        new_hitbox.y += self.dy * self.speed * dt
        if not self.tilemap.is_solid(new_hitbox):
            self.hitbox.y = new_hitbox.y
        else:
            print("[DEBUG] Collision on Y-axis")

        # Sync sprite rect with hitbox for drawing
        self.rect.midbottom = (self.hitbox.centerx, self.hitbox.bottom + 32)

        # Animate
        frames = self.animations.get(self.current_animation, self.animations["idle_down"])
        self.animation_timer += dt
        if self.is_moving:
            if self.animation_timer >= ANIMATION_SPEED:
                self.animation_timer = 0
                self.frame_index = (self.frame_index + 1) % len(frames)
        else:
            self.frame_index = 0

        self.image = frames[self.frame_index]

    def draw(self, surf, camera_x=0, camera_y=0):
        surf.blit(self.image, self.rect.move(-camera_x, -camera_y))
        #DEBUG: red rect at player sprite feet
        # pygame.draw.rect(surf, (255, 0, 0), self.hitbox.move(-camera_x, -camera_y), 1)

