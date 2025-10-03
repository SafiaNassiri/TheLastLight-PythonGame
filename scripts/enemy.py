import pygame

class Enemy:
    def __init__(self, x, y, sprite_sheet_path, tilemap, speed=2):
        self.tilemap = tilemap
        self.speed = speed
        self.rect = pygame.Rect(x, y, 32, 32)
        self.frames = []
        self.load_sprites(sprite_sheet_path)
        self.current_frame = 0
        self.frame_timer = 0.15
        self.dir = 1  # patrol direction

    def load_sprites(self, path):
        sheet = pygame.image.load(path).convert_alpha()
        frame_count = 4
        w = sheet.get_width() // frame_count
        h = sheet.get_height()
        for i in range(frame_count):
            self.frames.append(sheet.subsurface(pygame.Rect(i*w,0,w,h)))

    def update(self, player_rect, chase_radius=100):
        dx = player_rect.centerx - self.rect.centerx
        dy = player_rect.centery - self.rect.centery
        dist = (dx**2 + dy**2)**0.5

        if dist < chase_radius:
            move_x = self.speed if dx > 0 else -self.speed
            move_y = self.speed if dy > 0 else -self.speed
            self.move(move_x, move_y)
        else:
            self.move(self.speed*self.dir, 0)

    def move(self, dx, dy):
        self.rect.x += dx
        if self.collides_with_tile():
            self.rect.x -= dx
            self.dir *= -1
        self.rect.y += dy
        if self.collides_with_tile():
            self.rect.y -= dy

        if dx != 0 or dy != 0:
            self.update_animation()

    def update_animation(self):
        self.frame_timer -= 1/60
        if self.frame_timer <= 0:
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.frame_timer = 0.15

    def collides_with_tile(self):
        for y,row in enumerate(self.tilemap.tiles):
            for x,tile_id in enumerate(row):
                if tile_id is not None:
                    tile_rect = pygame.Rect(x*self.tilemap.tile_size, y*self.tilemap.tile_size,
                                            self.tilemap.tile_size, self.tilemap.tile_size)
                    if self.rect.colliderect(tile_rect): return True
        return False

    def draw(self, surface):
        surface.blit(self.frames[self.current_frame], self.rect.topleft)
