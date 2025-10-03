# main.py
import pygame
import json
import math
from scripts.Tilemap import TileMap
from scripts.player import Player
from scripts.orb import Orb
from scripts.shrine import Shrine
from scripts.enemy import Enemy

pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)

# ----- LOAD MAP -----
tilemap = TileMap("map.json", 32)

# ----- ENTITIES -----
player = None
shrine = None
orbs = []
enemies = []

spawn_layer = tilemap.layers.get("spawn", [])
for y, row in enumerate(spawn_layer):
    for x, tile in enumerate(row):
        if tile is None:
            continue
        world_x, world_y = x * tilemap.tile_size, y * tilemap.tile_size
        if tile == "player":
            player = Player(world_x, world_y, "player_spritesheet.png", tilemap)
        elif tile == "goblin":
            enemies.append(Enemy(world_x, world_y, "enemy_spritesheet.png", tilemap))
        elif tile == "treasure":
            orbs.append(Orb(world_x, world_y, "orb.png"))
        elif tile == "shrine":
            shrine = Shrine(world_x, world_y, "shrine.png", max_light=5)

# ----- GAME LOOP -----
running = True
messages = []
message_timer = 0

while running:
    dt = clock.tick(60)/1000
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # ----- HANDLE PLAYER INPUT -----
    keys = pygame.key.get_pressed()
    dx = dy = 0
    if keys[pygame.K_a]: dx = -player.speed
    if keys[pygame.K_d]: dx = player.speed
    if keys[pygame.K_w]: dy = -player.speed
    if keys[pygame.K_s]: dy = player.speed

    # Tentative move
    new_x = player.rect.x + dx
    new_y = player.rect.y + dy

    # Distance to shrine (if exists)
    if shrine:
        dist_to_shrine = math.hypot((new_x + player.rect.width/2) - shrine.rect.centerx,
                                    (new_y + player.rect.height/2) - shrine.rect.centery)
        if dist_to_shrine <= shrine.radius:
            player.rect.x = new_x
            player.rect.y = new_y
    else:
        player.rect.x = new_x
        player.rect.y = new_y

    # ----- UPDATE ENTITIES -----
    for enemy in enemies:
        enemy.update(player.rect)
    for orb in orbs:
        orb.update()
        if orb.check_collision(player.rect) and shrine:
            shrine.add_light()
            messages.append(f"Shrine light: {shrine.light}/{shrine.max_light}")
            message_timer = 180
    if shrine:
        shrine.update()

    # ----- DRAW -----
    screen.fill((20, 20, 20))
    tilemap.draw(screen)

    if shrine:
        shrine.draw(screen)
    for orb in orbs:
        orb.draw(screen)
    for enemy in enemies:
        enemy.draw(screen)
    if player:
        player.draw(screen)

    # Draw fog-of-war / light radius
    if shrine:
        shrine.draw_light_mask(screen)

    # Draw messages
    if messages and message_timer > 0:
        text_surf = font.render(messages[-1], True, (255, 255, 200))
        screen.blit(text_surf, (10, 10))
        message_timer -= 1

    pygame.display.flip()

pygame.quit()
