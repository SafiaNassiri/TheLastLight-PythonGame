import pygame, os, math, random

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, enemy_type, tilemap, path_id=None):
        super().__init__()
        self.enemy_type = enemy_type
        self.tilemap = tilemap
        self.path_id = path_id
        self.load_sprites()
        self.image = self.idle_frames[0]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.frame_index = 0
        self.anim_speed = 6
        self.timer = 0

        # Behavior
        self.player_detect_range = 64  # pixels
        self.attack_cooldown = 1.5
        self.attack_timer = 0
        self.speed = 50 if enemy_type == "Skeleton" else 0
        self.state = "idle"

        # For patrolling Skeletons
        self.path_points = self.get_path_points(path_id)
        self.path_index = 0
        self.direction = 1

    def load_sprites(self):
        base_path = os.path.join("assets", "entities", "Enemies", self.enemy_type)
        if self.enemy_type == "Knight":
            self.idle_frames = [pygame.image.load(os.path.join(base_path, "KnightIdle_strip.png")).convert_alpha()]
            self.attack_frames = [pygame.image.load(os.path.join(base_path, "KnightAttack_strip.png")).convert_alpha()]
        elif self.enemy_type == "Skeleton":
            self.idle_frames = [pygame.image.load(os.path.join(base_path, "Skeleton Idle.png")).convert_alpha()]
            self.walk_frames = [pygame.image.load(os.path.join(base_path, "Skeleton Walk.png")).convert_alpha()]
            self.attack_frames = [pygame.image.load(os.path.join(base_path, "Skeleton Attack.png")).convert_alpha()]

    def get_path_points(self, path_id):
        if path_id is None: return []
        # Hardcode or later load from map.json or editor
        paths = {
            1: [(10, 15), (15, 15)],
            2: [(5, 20), (8, 20), (5, 20)],
            3: [(12, 10), (12, 13)]
        }
        return paths.get(path_id, [])

    def update(self, player_rect, dt):
        self.timer += dt
        self.attack_timer = max(0, self.attack_timer - dt)

        # Calculate distance to player
        dx = player_rect.centerx - self.rect.centerx
        dy = player_rect.centery - self.rect.centery
        dist = math.hypot(dx, dy)

        if self.enemy_type == "Knight":
            # Stationary, attacks if near
            if dist < self.player_detect_range and self.attack_timer <= 0:
                self.attack()
        elif self.enemy_type == "Skeleton":
            if dist < self.player_detect_range * 2:
                self.chase(player_rect, dt)
            else:
                self.patrol(dt)

    def attack(self):
        self.state = "attack"
        self.attack_timer = self.attack_cooldown
        self.image = self.attack_frames[0]

    def chase(self, player_rect, dt):
        self.state = "chase"
        direction = pygame.Vector2(player_rect.centerx - self.rect.centerx, player_rect.centery - self.rect.centery).normalize()
        self.rect.x += direction.x * self.speed * dt
        self.rect.y += direction.y * self.speed * dt
        self.image = self.walk_frames[0]

    def patrol(self, dt):
        if not self.path_points: 
            self.image = self.idle_frames[0]
            return
        target = pygame.Vector2(self.path_points[self.path_index][0] * 32,
                                self.path_points[self.path_index][1] * 32)
        current = pygame.Vector2(self.rect.topleft)
        if current.distance_to(target) < 5:
            self.path_index += self.direction
            if self.path_index >= len(self.path_points) or self.path_index < 0:
                self.direction *= -1
                self.path_index += self.direction
        else:
            move_dir = (target - current).normalize()
            self.rect.x += move_dir.x * self.speed * dt
            self.rect.y += move_dir.y * self.speed * dt
            self.image = self.walk_frames[0]

    def draw(self, surf):
        surf.blit(self.image, self.rect)
