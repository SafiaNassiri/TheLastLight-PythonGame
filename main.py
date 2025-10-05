import pygame, os, sys
from scripts.Tilemap import TileMap
from scripts.player import Player
from scripts.orb import Orb
from scripts.shrine import ShrineManager
from scripts.message_manager import MessageManager

pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("The Last Light")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)

# ----- LOAD MAP -----
tilemap = TileMap("map.json", 32)

# Count tiles for debugging
for lname, layer in tilemap.layers.items():
    print(f"{lname} tile count:", sum(1 for row in layer for t in row if t))

# ----- ENTITY SETUP -----
player = None
orbs = []

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
orb_path = os.path.join(BASE_DIR, "assets", "entities", "Orb", "orbs.png")

# ----- PLAYER SPAWN -----
spawn_layer = tilemap.layers.get("spawnpoints", [])
for y, row in enumerate(spawn_layer):
    for x, tile_type in enumerate(row):
        if tile_type and tile_type.lower() == "player":
            world_x = x * tilemap.tile_size
            world_y = y * tilemap.tile_size
            player = Player(world_x, world_y, tilemap)

if player is None:
    raise RuntimeError("No player spawn found in map!")

# ----- ORB SPAWN -----
orb_layer = tilemap.layers.get("orb_spawn", [])
for y, row in enumerate(orb_layer):
    for x, marker in enumerate(row):
        if marker and marker.lower() == "orb":
            world_x = x * tilemap.tile_size
            world_y = y * tilemap.tile_size
            orbs.append(Orb(world_x, world_y, orb_path, row=2))

total_orbs = len(orbs)
print(f"Spawned {total_orbs} orbs.")

# ----- SHRINE MANAGER & MESSAGE MANAGER -----
message_manager = MessageManager(font)
shrine_manager = ShrineManager(tilemap, total_orbs)

# ----- CAMERA -----
camera_x, camera_y = 0, 0

# ----- GAME LOOP -----
running = True
while running:
    dt = clock.tick(60) / 1000

    # --- Events ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # --- Update ---
    player.handle_input()
    player.update(dt)

    # Orbs collection
    for orb in orbs:
        orb.update(dt)
        if not orb.collected and orb.check_collision(player.hitbox):
            orb.collected = True
            collected_count = sum(1 for o in orbs if o.collected)
            message_manager.add_message(f"Collected orb ({collected_count}/{total_orbs})")

    # Shrine interaction
    orbs_collected = sum(1 for orb in orbs if orb.collected)
    shrine_manager.update(player, message_manager, orbs_collected)
    message_manager.update()

    # --- Camera ---
    camera_x = player.rect.centerx - SCREEN_WIDTH // 2
    camera_y = player.rect.centery - SCREEN_HEIGHT // 2
    camera_x = max(0, min(camera_x, tilemap.width * tilemap.tile_size - SCREEN_WIDTH))
    camera_y = max(0, min(camera_y, tilemap.height * tilemap.tile_size - SCREEN_HEIGHT))

    # --- Draw ---
    screen.fill((10, 10, 10))  # Base darkness
    tilemap.draw(screen, camera_x, camera_y)

    # Draw orbs and shrines first so they glow under the fog
    for orb in orbs:
        orb.draw(screen, camera_x, camera_y)
    shrine_manager.draw(screen)
    player.draw(screen, camera_x, camera_y)

    # --- LIGHT / FOG OF WAR ---
    fog = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    fog.fill((0, 0, 0, 220))  # mostly opaque darkness

    # Player light
    light_radius = 120  # smaller radius
    player_pos = (int(player.rect.centerx - camera_x), int(player.rect.centery - camera_y))
    for r in range(light_radius, 0, -1):
        alpha = int(200 * (r / light_radius) ** 2)  # fade faster with squared distance
        pygame.draw.circle(fog, (0, 0, 0, alpha), player_pos, r)

    # Shrine light glow
    for shrine in shrine_manager.shrines + ([shrine_manager.main_shrine] if shrine_manager.main_shrine else []):
        if shrine is None:
            continue

        # Parameters
        oval_width = 15   # half-width
        oval_height = 40  # half-height
        center_shift_y = -40  # move light slightly up

        # Create a temporary surface for the light
        light_surf = pygame.Surface((oval_width*2, oval_height*2), pygame.SRCALPHA)
        
        # Draw nested ellipses from outer to inner
        for i in range(oval_height, 0, -1):
            alpha = int(150 * (1 - i / oval_height))  # brighter at center (i small)
            rect = pygame.Rect(oval_width - oval_width, oval_height - i, oval_width*2, i*2)
            pygame.draw.ellipse(light_surf, (255, 255, 200, alpha), rect)

        # Position light slightly above shrine
        shrine_pos = (
            int(shrine.rect.centerx - camera_x - oval_width),
            int(shrine.rect.centery - camera_y - oval_height + center_shift_y)
        )

        # Subtract from fog to create light effect
        fog.blit(light_surf, shrine_pos, special_flags=pygame.BLEND_RGBA_SUB)

    # Orb glow
    for orb in orbs:
        if not orb.collected:
            orb_pos = (int(orb.rect.centerx - camera_x), int(orb.rect.centery - camera_y))
            orb_radius = 40
            for r in range(orb_radius, 0, -1):
                alpha = int(180 * (r / orb_radius) ** 2)
                pygame.draw.circle(fog, (0, 0, 0, alpha), orb_pos, r)

    # Apply fog on top
    screen.blit(fog, (0, 0))

    # Draw messages
    message_manager.draw(screen)
    pygame.display.flip()

pygame.quit()
