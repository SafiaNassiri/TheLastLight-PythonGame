import pygame
from scripts.Tilemap import TileMap
from scripts.player import Player
from scripts.orb import Orb
from scripts.shrine import Shrine
from scripts.enemy import Enemy

pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("The Last Light")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)

# ----- LOAD MAP -----
tilemap = TileMap("map.json", 32)

# ----- ENTITIES -----
player = None
shrine = None
orbs = []
enemies = []

spawn_layer = tilemap.layers.get("spawnpoints", [])
print("Spawn layer tiles:", spawn_layer)

for tile in spawn_layer:
    x, y = tile["x"], tile["y"]
    tile_type = tile["type"].lower()
    world_x, world_y = x * tilemap.tile_size, y * tilemap.tile_size

    if tile_type == "player":
        player = Player(world_x, world_y, "satiro-Sheet v1.1.png", tilemap)
    elif tile_type == "knight":
        enemies.append(Enemy(world_x, world_y, "Knight", tilemap))
    elif tile_type == "skeleton":
        enemies.append(Enemy(world_x, world_y, "Skeleton", tilemap, path_id=tile.get("path_id")))
    elif tile_type == "shrine":
        shrine = Shrine(world_x, world_y, "shrine.png", max_light=5)

if player is None:
    raise RuntimeError("No player spawn found in map!")

# ----- CAMERA -----
camera_x = 0
camera_y = 0

# ----- GAME LOOP -----
running = True
messages = []
message_timer = 0

while running:
    dt = clock.tick(60) / 1000  # delta time in seconds

    # ----- EVENT HANDLING -----
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # ----- UPDATE ENTITIES -----
    player.handle_input()
    player.update(dt)

    for enemy in enemies:
        enemy.update(player.rect)

    for orb in orbs:
        orb.update()
        if not orb.collected and orb.check_collision(player.rect) and shrine:
            shrine.add_light()
            messages.append(f"Shrine light: {shrine.light}/{shrine.max_light}")
            message_timer = 180

    if shrine:
        shrine.update()

    # ----- CAMERA UPDATE -----
    camera_x = player.rect.centerx - SCREEN_WIDTH // 2
    camera_y = player.rect.centery - SCREEN_HEIGHT // 2
    # Clamp camera to map bounds
    camera_x = max(0, min(camera_x, tilemap.width * tilemap.tile_size - SCREEN_WIDTH))
    camera_y = max(0, min(camera_y, tilemap.height * tilemap.tile_size - SCREEN_HEIGHT))

    # ----- DRAW -----
    screen.fill((25, 25, 25))

    # Draw map and entities with camera offset
    tilemap.draw(screen, camera_x, camera_y)
    if shrine:
        shrine.draw(screen, camera_x, camera_y)
    for orb in orbs:
        orb.draw(screen, camera_x, camera_y)
    for enemy in enemies:
        enemy.draw(screen, camera_x, camera_y)
    player.draw(screen, camera_x, camera_y)

    if shrine:
        shrine.draw_light_mask(screen, camera_x, camera_y)

    # Draw messages
    if messages and message_timer > 0:
        text_surf = font.render(messages[-1], True, (255, 255, 200))
        screen.blit(text_surf, (10, 10))
        message_timer -= 1

    pygame.display.flip()

pygame.quit()
