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
tilemap = TileMap("map.json", "tileset.png", 32)

with open("map.json") as f:
    data = json.load(f)

# ----- ENTITIES -----
player = None
shrine = None
orbs = []
enemies = []

for obj in data.get("objects", []):
    x, y = obj["x"]*32, obj["y"]*32
    if obj["type"] == "player":
        player = Player(x, y, "player_spritesheet.png", tilemap)
    elif obj["type"] == "shrine":
        shrine = Shrine(x, y, "shrine.png", max_light=5)
    elif obj["type"] == "orb":
        orbs.append(Orb(x, y, "orb.png"))
    elif obj["type"] == "enemy":
        enemies.append(Enemy(x, y, "enemy_spritesheet.png", tilemap))

# ----- GAME LOOP -----
running = True
messages = []
message_timer = 0

while running:
    dt = clock.tick(60)/1000
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # ----- HANDLE PLAYER INPUT & LIMIT BY LIGHT RADIUS -----
    keys = pygame.key.get_pressed()
    dx = dy = 0
    if keys[pygame.K_a]: dx = -player.speed
    if keys[pygame.K_d]: dx = player.speed
    if keys[pygame.K_w]: dy = -player.speed
    if keys[pygame.K_s]: dy = player.speed

    # Tentative move
    new_x = player.rect.x + dx
    new_y = player.rect.y + dy

    # Distance to shrine
    dist_to_shrine = math.hypot((new_x + player.rect.width/2) - shrine.rect.centerx,
                                (new_y + player.rect.height/2) - shrine.rect.centery)

    if dist_to_shrine <= shrine.radius:
        player.rect.x = new_x
        player.rect.y = new_y

    # ----- UPDATE ENTITIES -----
    for enemy in enemies:
        enemy.update(player.rect)
    for orb in orbs:
        orb.update()
        if orb.check_collision(player.rect):
            shrine.add_light()
            messages.append(f"Shrine light: {shrine.light}/{shrine.max_light}")
            message_timer = 180

    shrine.update()

    # ----- DRAW -----
    screen.fill((20, 20, 20))
    tilemap.draw(screen)

    shrine.draw(screen)
    for orb in orbs:
        orb.draw(screen)
    for enemy in enemies:
        enemy.draw(screen)
    player.draw(screen)

    # Draw fog-of-war / light radius
    shrine.draw_light_mask(screen)

    # Draw messages
    if messages and message_timer > 0:
        text_surf = font.render(messages[-1], True, (255, 255, 200))
        screen.blit(text_surf, (10, 10))
        message_timer -= 1

    pygame.display.flip()

pygame.quit()
