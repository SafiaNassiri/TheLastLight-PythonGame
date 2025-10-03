import pygame

class Player:
    def __init__(self, x, y, sprite_sheet_path, tilemap, speed=4):
        self.tilemap = tilemap
        self.speed = speed
        self.rect = pygame.Rect(x, y, 32, 32)
        self.frames = []
        self.load_sprites(sprite_sheet_path)
        self.current_frame = 0
        self.frame_timer = 0.1  # seconds per frame

    def load_sprites(self, path):
        sheet = pygame.image.load(path).convert_alpha()
        frame_count = 4  # horizontal strip
        frame_width = sheet.get_width() // frame_count
        frame_height = sheet.get_height()
        for i in range(frame_count):
            frame = sheet.subsurface(pygame.Rect(i*frame_width, 0, frame_width, frame_height))
            self.frames.append(frame)

    def handle_input(self):
        keys = pygame.key.get_pressed()
        dx = dy = 0
        if keys[pygame.K_a]: dx = -self.speed
        if keys[pygame.K_d]: dx = self.speed
        if keys[pygame.K_w]: dy = -self.speed
        if keys[pygame.K_s]: dy = self.speed
        self.move(dx, dy)

    def move(self, dx, dy):
        self.rect.x += dx
        if self.collides_with_tile(): self.rect.x -= dx
        self.rect.y += dy
        if self.collides_with_tile(): self.rect.y -= dy

        if dx != 0 or dy != 0:
            self.update_animation()

    def update_animation(self):
        self.frame_timer -= 1/60
        if self.frame_timer <= 0:
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.frame_timer = 0.1

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
