import pygame
import os
import sys
import time
from scripts.Tilemap import TileMap
from scripts.player import Player
from scripts.orb import Orb
from scripts.shrine import ShrineManager
from scripts.message_manager import MessageManager

# ----- GAME SETUP -----
pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("The Last Light")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)

# ----- LIGHT FUNCTION -----
def draw_light(surface, position, radius_w, radius_h, intensity=100):
    """Draw an oval/ellipse light effect at position on the given surface."""
    light_surf = pygame.Surface((radius_w*2, radius_h*2), pygame.SRCALPHA)
    pygame.draw.ellipse(light_surf, (255, 255, 200, intensity), (0, 0, radius_w*2, radius_h*2))
    surface.blit(light_surf, (position[0]-radius_w, position[1]-radius_h), special_flags=pygame.BLEND_RGBA_SUB)

# ----- LOAD MAP -----
tilemap = TileMap("map.json", 32)

# ----- ENTITY SETUP -----
player = None
orbs = []

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
orb_path = os.path.join(BASE_DIR, "assets", "entities", "Orb", "Free Smoke Fx  Pixel 04.png")

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
            orb_size = 24 
            orbs.append(Orb(x, y, width=orb_size, height=orb_size))

total_orbs = len(orbs)
print(f"Spawned {total_orbs} orbs.")

# ----- SHRINE MANAGER & MESSAGE MANAGER -----
message_manager = MessageManager(font)
shrine_manager = ShrineManager(tilemap, total_orbs)

main_shrine_light_radius = 50  # initial radius
main_shrine_max_radius = max(SCREEN_WIDTH, SCREEN_HEIGHT)  # max radius to fill screen
main_shrine_expand_speed = 200  # pixels per second

player_at_main_shrine = False

# ----- TEXT WRAPPING -----
def wrap_text(text, font, max_width):
    words = text.split(' ')
    lines = []
    current_line = ''
    for word in words:
        test_line = current_line + (' ' if current_line else '') + word
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    return lines

# ----- OPENING SCENE -----
def show_opening_scene():
    lines = [
        ("There is no light.", 1),
        ("Only the chill of the ever-fog.", 1),
        ("The sun is but a memory, swallowed by the great darkness.", 1),
        ("But you.", 2),
        ("You were born under a different star.", 1),
        ("Your heart holds a flame the darkness cannot quench.", 1),
        ("Your kin chose you, bringer of dawn.", 1),
        ("They chose you for courage, a shield against despair.", 1),
        ("They chose you for bravery, a blade against the shadows.",1),
        ("You are immune. The fog's taint cannot touch you.", 1),
        ("Restore what was lost.", 1),
        ("Retrieve the six spheres of dawn.", 1),
        ("Three mark the start. The others are scattered:", 1),
        ("The overgrown garden.", 1),
        ("The hollow square.",1),
        ("The forgotten plaza.", 1),
        ("Gather the six. Take them to the main shrine.", 4),
        ("Go. The fate of all light rests in your steps.", 0)
    ]

    screen.fill((0, 0, 0))
    pygame.display.flip()
    scene_font = pygame.font.SysFont(None, 28)
    displayed_lines = []
    skip_to_all = False  # First Enter → skip delays
    ready_to_start = False  # Second Enter → exit scene

    for line, delay in lines:
        displayed_lines.append(line)
        start_time = time.time()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    if not skip_to_all:
                        skip_to_all = True  # First Enter → skip delay, show all
                    else:
                        ready_to_start = True  # Second Enter → exit scene

            screen.fill((0, 0, 0))
            y_offset = 50
            lines_to_draw = displayed_lines if not skip_to_all else [l for l,_ in lines]
            for text_line in lines_to_draw:
                wrapped = wrap_text(text_line, scene_font, SCREEN_WIDTH - 40)
                for wrapped_line in wrapped:
                    surf = scene_font.render(wrapped_line, True, (255, 255, 255))
                    x = (SCREEN_WIDTH - surf.get_width()) // 2
                    screen.blit(surf, (x, y_offset))
                    y_offset += 30

            pygame.display.flip()

            # Break timing loop if not skipping and delay passed
            if not skip_to_all and (time.time() - start_time >= delay):
                break

            if ready_to_start:
                return  # Exit the scene and start the game

            clock.tick(60)

# ----- SHOW OPENING SCENE -----
show_opening_scene()

# ----- THEN START THE GAME LOOP -----
running = True
player_light_radius = 80
while running:
    dt = clock.tick(60) / 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # ---- PLAYER UPDATE ----
    if not getattr(player, "disable_input", False):
        player.handle_input()
    player.update(dt)

    # ---- ORBS UPDATE ----
    for orb in orbs:
        orb.update(dt)
        if not orb.collected and orb.check_collision(player.hitbox):
            orb.collected = True

    orbs_collected = sum(1 for orb in orbs if orb.collected)

    # ---- SHRINE UPDATE ----
    shrine_manager.update(player, message_manager, orbs_collected, dt)

    # ---- MESSAGE UPDATE ----
    message_manager.update()

    # ---- CAMERA CALCULATION ----
    camera_x = player.rect.centerx - SCREEN_WIDTH // 2
    camera_y = player.rect.centery - SCREEN_HEIGHT // 2
    camera_x = max(0, min(camera_x, tilemap.width * tilemap.tile_size - SCREEN_WIDTH))
    camera_y = max(0, min(camera_y, tilemap.height * tilemap.tile_size - SCREEN_HEIGHT))

    # ---- DRAW WORLD -----
    screen.fill((10, 10, 10))
    tilemap.draw(screen, camera_x, camera_y)
    for orb in orbs:
        orb.update(dt)
        orb.draw(screen, camera_x, camera_y, tile_size=tilemap.tile_size)

    shrine_manager.draw(screen)

    # ---- LIGHT & FOG ----
    fog = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    fog.fill((0, 0, 0, 220))

    # Player light
    player_pos = (int(player.rect.centerx - camera_x), int(player.rect.centery - camera_y))
    draw_light(fog, player_pos, int(player_light_radius), int(player_light_radius*0.8), intensity=80)

    # Shrines light
for shrine in shrine_manager.shrines + ([shrine_manager.main_shrine] if shrine_manager.main_shrine else []):
    if shrine is None:
        continue

    shrine_pos_screen = (
        int(shrine.rect.centerx - camera_x),
        int(shrine.rect.centery - camera_y - 35)
    )

    # Main shrine light expansion
    if shrine == shrine_manager.main_shrine and orbs_collected == total_orbs:
        # Check if player is near to start expansion
        if player.rect.colliderect(shrine.rect):
            player_at_main_shrine = True

        if player_at_main_shrine:
            main_shrine_light_radius += main_shrine_expand_speed * dt
            radius = min(main_shrine_light_radius, main_shrine_max_radius)
            draw_light(fog, shrine_pos_screen, radius, radius, intensity=150)
        else:
            # Regular shrine light before interaction
            draw_light(fog, shrine_pos_screen, 15, 40, intensity=120)
    else:
        # Regular shrines
        draw_light(fog, shrine_pos_screen, 15, 40, intensity=120)

    # Orbs light
    for orb in orbs:
        if orb.collected:
            continue
        orb_pos = (
            int(orb.tile_x * tilemap.tile_size - camera_x + tilemap.tile_size//2),
            int(orb.tile_y * tilemap.tile_size - camera_y + tilemap.tile_size//2 + getattr(orb, 'offset_y', 0))
        )
        draw_light(fog, orb_pos, 40, 40, intensity=120)

    screen.blit(fog, (0, 0))
    player.draw(screen, camera_x, camera_y)
    message_manager.draw(screen)

    # ---- UI: Orbs collected ----
    collected_count = sum(1 for o in orbs if o.collected)
    orb_text = font.render(f"Orbs: {collected_count}/{len(orbs)}", True, (255, 255, 255))
    screen.blit(orb_text, (SCREEN_WIDTH - orb_text.get_width() - 10, 10))

    pygame.display.flip()

pygame.quit()
sys.exit()
