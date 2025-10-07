import pygame, sys, math, time
from scripts.Tilemap import TileMap
from scripts.player import Player
from scripts.orb import Orb
from scripts.shrine import ShrineManager
from scripts.message_manager import MessageManager
from scripts.sounds import *
from scripts.lighting import draw_light
from scripts.ui.menu import main_menu
from scripts.ui.scenes import show_opening_scene, show_thank_you_screen, show_how_to_play

pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)

tilemap = TileMap("map.json", 32)
play_ambient()


def start_game():
    player = None
    orbs = []

    # Spawn player
    spawn_layer = tilemap.layers.get("spawnpoints", [])
    for y, row in enumerate(spawn_layer):
        for x, tile_type in enumerate(row):
            if tile_type and tile_type.lower() == "player":
                world_x = x * tilemap.tile_size
                world_y = y * tilemap.tile_size
                player = Player(world_x, world_y, tilemap)
    if player is None:
        raise RuntimeError("No player spawn found!")

    # Spawn orbs
    orb_layer = tilemap.layers.get("orb_spawn", [])
    for y, row in enumerate(orb_layer):
        for x, marker in enumerate(row):
            if marker and marker.lower() == "orb":
                orb_size = 24
                orbs.append(Orb(x, y, width=orb_size, height=orb_size))
    total_orbs = len(orbs)

    message_manager = MessageManager(font)
    shrine_manager = ShrineManager(tilemap, total_orbs)

    main_shrine_light_radius = 50
    main_shrine_max_radius = max(SCREEN_WIDTH, SCREEN_HEIGHT)
    main_shrine_expand_speed = 200
    player_at_main_shrine = False
    player_light_radius = 80
    time_accumulator = 0
    running = True
    game_completed = False

    while running:
        dt = clock.tick(60) / 1000
        time_accumulator += dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_m:
                    toggle_mute()
                elif event.key in (pygame.K_PLUS, pygame.K_EQUALS):
                    change_ambient_volume(0.1)
                elif event.key == pygame.K_MINUS:
                    change_ambient_volume(-0.1)

        # Player update
        if not getattr(player, "disable_input", False):
            player.handle_input()
        player.update(dt)

        # Orbs update
        for orb in orbs:
            orb.update(dt)
            orb.offset_y = math.sin(time_accumulator * 2 + orb.tile_x + orb.tile_y) * 5
            if not orb.collected and orb.check_collision(player.hitbox):
                orb.collected = True
                play_orb_sound()
        orbs_collected = sum(1 for orb in orbs if orb.collected)

        # Shrine update
        shrine_manager.update(player, message_manager, orbs_collected, dt)

        # Camera
        camera_x = max(0, min(player.rect.centerx - SCREEN_WIDTH // 2,
                              tilemap.width * tilemap.tile_size - SCREEN_WIDTH))
        camera_y = max(0, min(player.rect.centery - SCREEN_HEIGHT // 2,
                              tilemap.height * tilemap.tile_size - SCREEN_HEIGHT))

        # Draw world
        screen.fill((10, 10, 10))
        tilemap.draw(screen, camera_x, camera_y)
        for orb in orbs:
            orb.draw(screen, camera_x, camera_y, tile_size=tilemap.tile_size)
        shrine_manager.draw(screen)

        fog = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        fog.fill((0, 0, 0, 220))

        player_pos = (int(player.rect.centerx - camera_x), int(player.rect.centery - camera_y))
        draw_light(fog, player_pos, int(player_light_radius), int(player_light_radius * 0.8), intensity=80)

        # Shrine lights
        for shrine in shrine_manager.shrines + ([shrine_manager.main_shrine] if shrine_manager.main_shrine else []):
            if shrine is None: continue
            shrine_pos_screen = (
                int(shrine.rect.centerx - camera_x),
                int(shrine.rect.centery - camera_y - 35)
            )
            if shrine == shrine_manager.main_shrine and orbs_collected == total_orbs:
                if player.rect.colliderect(shrine.rect):
                    player_at_main_shrine = True
                radius = main_shrine_light_radius if player_at_main_shrine else 15
                draw_light(fog, shrine_pos_screen, radius, radius, intensity=150 if player_at_main_shrine else 120)
            else:
                draw_light(fog, shrine_pos_screen, 15, 40, intensity=120)

        # Orbs light
        for orb in orbs:
            if orb.collected: continue
            orb_pos = (
                int(orb.tile_x * tilemap.tile_size - camera_x + tilemap.tile_size//2),
                int(orb.tile_y * tilemap.tile_size - camera_y + tilemap.tile_size//2 + getattr(orb, 'offset_y', 0))
            )
            inner_radius = 8 + 4 * math.sin(time_accumulator * 4 + orb.tile_x + orb.tile_y)
            draw_light(fog, orb_pos, 40, 40, intensity=120)
            pygame.draw.circle(fog, (255, 200, 50, 180), orb_pos, int(inner_radius))

        screen.blit(fog, (0, 0))
        player.draw(screen, camera_x, camera_y)
        message_manager.update()
        message_manager.draw(screen)

        orb_text = font.render(f"Orbs: {orbs_collected}/{len(orbs)}", True, (255, 255, 255))
        screen.blit(orb_text, (SCREEN_WIDTH - orb_text.get_width() - 10, 10))

        pygame.display.flip()

        # Check completion
        if player_at_main_shrine and orbs_collected == total_orbs and not game_completed:
            game_completed = True
            message_manager.add_message(
                "The six Spheres are whole. The original light is reborn through your courage, Bringer of Dawn. Now, command the dawn!",
                duration_seconds=4
            )
            while main_shrine_light_radius < main_shrine_max_radius:
                dt = clock.tick(60) / 1000
                main_shrine_light_radius += 200 * dt
                radius = min(main_shrine_light_radius, main_shrine_max_radius)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                        pygame.quit()
                        sys.exit()
                screen.fill((10, 10, 10))
                tilemap.draw(screen, camera_x, camera_y)
                player.draw(screen, camera_x, camera_y)
                fog.fill((0, 0, 0, 220))
                draw_light(fog, (shrine_manager.main_shrine.rect.centerx - camera_x, shrine_manager.main_shrine.rect.centery - camera_y - 35), int(radius), int(radius), intensity=150)
                screen.blit(fog, (0, 0))
                message_manager.update()
                message_manager.draw(screen)
                pygame.display.flip()
            show_thank_you_screen(screen, clock, SCREEN_WIDTH, SCREEN_HEIGHT)
            running = False


# Outer loop
while True:
    main_menu(screen, clock, SCREEN_WIDTH, SCREEN_HEIGHT, start_game, show_opening_scene, show_how_to_play)
    show_opening_scene(screen, clock, SCREEN_WIDTH, SCREEN_HEIGHT)
    start_game()
