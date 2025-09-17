import pygame
import random
import math
from scripts.player import Player
from scripts.enemy import Enemy
from scripts.orb import Orb
from scripts.shrine import Shrine

# Initialize Pygame
pygame.init()

# Screen setup
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("The Last Light")
clock = pygame.time.Clock()
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)

# World size
WORLD_WIDTH, WORLD_HEIGHT = 2000, 1200
TILE_SIZE = 50
ROWS = WORLD_HEIGHT // TILE_SIZE
COLS = WORLD_WIDTH // TILE_SIZE

# ===== Generate a simple connected maze =====
walls = []

# Simple corridor maze generator
for r in range(ROWS):
    for c in range(COLS):
        if r == 0 or r == ROWS-1 or c == 0 or c == COLS-1:
            walls.append(pygame.Rect(c*TILE_SIZE, r*TILE_SIZE, TILE_SIZE, TILE_SIZE))
        else:
            # Keep corridors open
            if random.random() < 0.1:  # 10% chance of wall
                walls.append(pygame.Rect(c*TILE_SIZE, r*TILE_SIZE, TILE_SIZE, TILE_SIZE))

# Function to get empty spawn spots
def get_empty_spot():
    while True:
        x = random.randint(0, WORLD_WIDTH-40)
        y = random.randint(0, WORLD_HEIGHT-40)
        new_rect = pygame.Rect(x, y, 40, 40)
        if all(not new_rect.colliderect(w) for w in walls):
            return x, y

# Spawn player safely
player_x, player_y = get_empty_spot()
player = Player(player_x, player_y)

# Spawn enemies
enemies = []
for _ in range(10):
    ex, ey = get_empty_spot()
    enemies.append(Enemy(ex, ey))

# Spawn orbs
orbs = []
for _ in range(15):
    ox, oy = get_empty_spot()
    orbs.append(Orb(ox, oy))

# Spawn shrine
shrine_x, shrine_y = get_empty_spot()
shrine = Shrine(shrine_x, shrine_y, 40, len(orbs))

# Camera offset
def get_camera_offset(player):
    camera_x = player.rect.centerx - WIDTH // 2
    camera_y = player.rect.centery - HEIGHT // 2
    camera_x = max(0, min(camera_x, WORLD_WIDTH - WIDTH))
    camera_y = max(0, min(camera_y, WORLD_HEIGHT - HEIGHT))
    return camera_x, camera_y

# Main loop
running = True
while running:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    player.move(keys, walls)

    # Enemy movement
    for enemy in enemies:
        enemy.move(player, walls)

    # Collect orbs
    for orb in orbs[:]:
        if player.rect.colliderect(orb.rect):
            orbs.remove(orb)
            player.orbs_carried += 1
            shrine.collect_orb()
            for msg in shrine.check_milestones():
                print(msg)

    # Interact with shrine
    if player.rect.colliderect(pygame.Rect(shrine.x-shrine.radius, shrine.y-shrine.radius, shrine.radius*2, shrine.radius*2)):
        if keys[pygame.K_e] and shrine.collected_orbs >= shrine.total_orbs:
            print("You activated the Shrine! Game Complete!")
            running = False

    camera_x, camera_y = get_camera_offset(player)
    screen.fill(BLACK)

    # Draw walls
    for wall in walls:
        pygame.draw.rect(screen, GRAY, pygame.Rect(
            wall.x - camera_x, wall.y - camera_y, wall.width, wall.height
        ))

    # Draw orbs
    for orb in orbs:
        orb.draw(screen, camera_x, camera_y)

    # Draw shrine
    shrine.draw(screen, camera_x, camera_y)

    # Draw player with gradient light
    player.draw(screen, camera_x, camera_y)

    # Draw enemies visible only within player's light radius
    for enemy in enemies:
        dx = enemy.rect.centerx - player.rect.centerx
        dy = enemy.rect.centery - player.rect.centery
        distance = math.hypot(dx, dy)
        if distance <= player.light_radius:
            fade = max(50, 255 - int((distance / player.light_radius) * 255))
            enemy_color = (*enemy.color[:3], fade)
            enemy_surface = pygame.Surface((enemy.rect.width, enemy.rect.height), pygame.SRCALPHA)
            enemy_surface.fill(enemy_color)
            screen.blit(enemy_surface, (enemy.rect.x - camera_x, enemy.rect.y - camera_y))

    # Display collected orbs
    font = pygame.font.SysFont(None, 36)
    text = font.render(f"Orbs collected: {shrine.collected_orbs}/{len(orbs)}", True, WHITE)
    screen.blit(text, (10, 10))

    pygame.display.flip()

pygame.quit()
