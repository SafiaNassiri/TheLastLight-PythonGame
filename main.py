import pygame
import os
import sys
import time
import math
from scripts.Tilemap import TileMap
from scripts.player import Player
from scripts.orb import Orb
from scripts.shrine import ShrineManager
from scripts.message_manager import MessageManager

# GAME SETUP
pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("The Last Light")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)

# LIGHT FUNCTION
def draw_light(surface, position, radius_w, radius_h, intensity=100):
    light_surf = pygame.Surface((radius_w*2, radius_h*2), pygame.SRCALPHA)
    pygame.draw.ellipse(light_surf, (255, 255, 200, intensity), (0, 0, radius_w*2, radius_h*2))
    surface.blit(light_surf, (position[0]-radius_w, position[1]-radius_h), special_flags=pygame.BLEND_RGBA_SUB)

# LOAD MAP
tilemap = TileMap("map.json", 32)

# TEXT WRAPPING
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

# SOUND SETUP
pygame.mixer.init()

# Ambient background
ambient_sound = pygame.mixer.Sound("assets/sounds/825858__vrymaa__monastery-atmosphere-monk-chant-chimes.wav")
ambient_volume = 0.5
ambient_sound.set_volume(ambient_volume)
ambient_sound.play(-1)  # loop forever

# SFX
button_sound = pygame.mixer.Sound("assets/sounds/613405__josheb_policarpio__button-6.wav")
orb_sound = pygame.mixer.Sound("assets/sounds/432287__ari_glitch__magic-circle-short-ringing-sfx.mp3")
sfx_volume = 0.5
button_sound.set_volume(sfx_volume)
orb_sound.set_volume(sfx_volume)

# Sound state
sound_muted = False

# FUNCTIONS
def toggle_mute():
    global sound_muted
    sound_muted = not sound_muted
    if sound_muted:
        ambient_sound.set_volume(0)
        button_sound.set_volume(0)
        orb_sound.set_volume(0)
    else:
        ambient_sound.set_volume(ambient_volume)
        button_sound.set_volume(sfx_volume)
        orb_sound.set_volume(sfx_volume)

def change_ambient_volume(delta):
    global ambient_volume
    ambient_volume = max(0.0, min(1.0, ambient_volume + delta))
    if not sound_muted:
        ambient_sound.set_volume(ambient_volume)

def change_sfx_volume(delta):
    global sfx_volume
    sfx_volume = max(0.0, min(1.0, sfx_volume + delta))
    if not sound_muted:
        button_sound.set_volume(sfx_volume)
        orb_sound.set_volume(sfx_volume)

def play_button_sound():
    if not sound_muted:
        button_sound.play()

def play_orb_sound():
    if not sound_muted:
        orb_sound.play()

# Button code
class Button:
    def __init__(self, text, x, y, w, h, font=None):
        self.text = text
        self.rect = pygame.Rect(x, y, w, h)
        self.font = font or pygame.font.SysFont(None, 32)

    def draw(self, screen, selected=False):
        mouse_pos = pygame.mouse.get_pos()
        hovered = self.rect.collidepoint(mouse_pos)
        color = (255, 255, 255) if hovered or selected else (180, 180, 180)
        text_surf = self.font.render(self.text, True, color)
        screen.blit(text_surf, self.rect.topleft)

    def handle_event(self, event, selected=False):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN and selected:
            return True
        return False

    def update_hover(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)

# SCENES
#  opening scene
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
        ("They chose you for bravery, a blade against the shadows.", 1),
        ("You are immune. The fog's taint cannot touch you.", 1),
        ("Restore what was lost.", 1),
        ("Retrieve the twelve spheres of dawn.", 1),
        ("Three mark the start. The others are scattered.", 1),
        ("Gather the twelve. Take them to the main shrine.", 4),
        ("Go. The fate of all light rests in your steps.", 0)
    ]

    screen.fill((0, 0, 0))
    pygame.display.flip()
    scene_font = pygame.font.SysFont(None, 28)
    displayed_lines = []
    skip_to_end = False
    scene_done = False

    # Button setup
    button_font = pygame.font.SysFont(None, 24)
    continue_button = Button(
        "Continue",
        SCREEN_WIDTH - 160,
        SCREEN_HEIGHT - 60,
        140,
        40,
        font=button_font
    )

    # --- MAIN LOOP FOR OPENING SCENE ---
    for line, delay in lines:
        if skip_to_end:
            break  # skip line-by-line animation
        displayed_lines.append(line)
        start_time = time.time()

        while time.time() - start_time < delay:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        skip_to_end = True
                    elif event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()

            # Draw current progress
            screen.fill((0, 0, 0))
            y_offset = 60  # text starts higher on screen now
            for text_line in displayed_lines:
                wrapped = wrap_text(text_line, scene_font, SCREEN_WIDTH - 40)
                for wrapped_line in wrapped:
                    surf = scene_font.render(wrapped_line, True, (255, 255, 255))
                    x = (SCREEN_WIDTH - surf.get_width()) // 2
                    screen.blit(surf, (x, y_offset))
                    y_offset += 30

            pygame.display.flip()
            clock.tick(60)

    # After all lines or skipped — show all lines and button
    displayed_lines = [l for l, _ in lines]
    waiting_for_continue = True

    while waiting_for_continue:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            # Let Button handle both Enter and Click
            if continue_button.handle_event(event, selected=True):
                play_button_sound()
                return  # proceed to game

        # Draw full scene + button
        screen.fill((0, 0, 0))
        y_offset = 60  # consistent higher text position
        for text_line in displayed_lines:
            wrapped = wrap_text(text_line, scene_font, SCREEN_WIDTH - 40)
            for wrapped_line in wrapped:
                surf = scene_font.render(wrapped_line, True, (255, 255, 255))
                x = (SCREEN_WIDTH - surf.get_width()) // 2
                screen.blit(surf, (x, y_offset))
                y_offset += 30

        continue_button.draw(screen, selected=True)
        pygame.display.flip()
        clock.tick(60)

# main menu
def main_menu():
    menu_font = pygame.font.SysFont(None, 48)
    title_font = pygame.font.SysFont(None, 72, bold=True)
    options = ["Play", "How to Play", "Options", "Quit"]
    selected = 0
    option_rects = []

    title_text = "THE LAST LIGHT"
    spaced_title = " ".join(title_text)

    while True:
        screen.fill((0, 0, 0))
        option_rects.clear()

        # Draw title
        title_surf = title_font.render(spaced_title, True, (255, 255, 255))
        title_x = (SCREEN_WIDTH - title_surf.get_width()) // 2
        title_y = 80
        screen.blit(title_surf, (title_x, title_y))

        # Draw menu options and build rects for mouse interaction
        for i, option in enumerate(options):
            color = (255, 255, 255) if i == selected else (150, 150, 150)
            surf = menu_font.render(option, True, color)
            x = (SCREEN_WIDTH - surf.get_width()) // 2
            y = 250 + i * 70
            screen.blit(surf, (x, y))
            option_rects.append(pygame.Rect(x, y, surf.get_width(), surf.get_height()))

        pygame.display.flip()

        # Handle input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                elif event.key == pygame.K_RETURN:
                    play_button_sound()
                    if options[selected] == "Play":
                        return  # start the game
                    elif options[selected] == "Options":
                        show_options_menu()
                    elif options[selected] == "How to Play":
                        show_how_to_play()
                    elif options[selected] == "Quit":
                        pygame.quit()
                        sys.exit()
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

            elif event.type == pygame.MOUSEMOTION:
                # Hover -> update selection so Enter also triggers hovered item
                for i, rect in enumerate(option_rects):
                    if rect.collidepoint(event.pos):
                        selected = i

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i, rect in enumerate(option_rects):
                    if rect.collidepoint(event.pos):
                        play_button_sound()

                        # Process clicked item
                        if options[i] == "Play":
                            return  # exits menu → game starts
                        elif options[i] == "Options":
                            show_options_menu()
                            # refresh selection visuals after returning
                            selected = 0
                        elif options[i] == "How to Play":
                            show_how_to_play()
                            selected = 0
                        elif options[i] == "Quit":
                            pygame.quit()
                            sys.exit()

# SHOW OPTIOSN MENU
def show_options_menu():
    options_font = pygame.font.SysFont(None, 36)
    selected = 0
    option_items = [
        "Ambient Volume: {:.0%} (LEFT/RIGHT to adjust)".format(ambient_volume),
        "SFX Volume: {:.0%} (LEFT/RIGHT to adjust)".format(sfx_volume),
        "Back"
    ]
    option_rects = []

    while True:
        screen.fill((0, 0, 0))
        y = 200
        option_items[0] = "Ambient Volume: {:.0%} (LEFT/RIGHT to adjust)".format(ambient_volume)
        option_items[1] = "SFX Volume: {:.0%} (LEFT/RIGHT to adjust)".format(sfx_volume)
        option_rects.clear()

        # Draw options
        for i, item in enumerate(option_items):
            color = (255, 255, 255) if i == selected else (150, 150, 150)
            surf = options_font.render(item, True, color)
            x = (SCREEN_WIDTH - surf.get_width()) // 2
            screen.blit(surf, (x, y))
            option_rects.append(pygame.Rect(x, y, surf.get_width(), surf.get_height()))
            y += 60

        pygame.display.flip()

        # Handle input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(option_items)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(option_items)
                elif event.key == pygame.K_RETURN:
                    play_button_sound()
                    if option_items[selected].startswith("Back"):
                        return
                elif event.key == pygame.K_LEFT:
                    if selected == 0:
                        change_ambient_volume(-0.1)
                    elif selected == 1:
                        change_sfx_volume(-0.1)
                elif event.key == pygame.K_RIGHT:
                    if selected == 0:
                        change_ambient_volume(0.1)
                    elif selected == 1:
                        change_sfx_volume(0.1)
            elif event.type == pygame.MOUSEMOTION:
                for i, rect in enumerate(option_rects):
                    if rect.collidepoint(event.pos):
                        selected = i
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i, rect in enumerate(option_rects):
                    if rect.collidepoint(event.pos):
                        play_button_sound()
                        if option_items[i].startswith("Back"):
                            return

# HOW TO PLAY SCREEN
def show_how_to_play():
    instructions = [
        "HOW TO PLAY",
        "",
        "- Move with WASD",
        "- Collect all the orbs",
        "- Take them to the main shrine",
        "- Navigate the dark land to your destination",
        "",
        "- Press M to mute",
        "- Press ESC to quit game at any time",
    ]
    instr_font = pygame.font.SysFont(None, 32)
    back_font = pygame.font.SysFont(None, 28)
    selected = 0  # 0 = Back button

    while True:
        screen.fill((0, 0, 0))
        y_offset = 100

        # Draw instructions
        for line in instructions:
            surf = instr_font.render(line, True, (255, 255, 255))
            x = (SCREEN_WIDTH - surf.get_width()) // 2
            screen.blit(surf, (x, y_offset))
            y_offset += 40

        # Draw Back button
        back_color = (255, 255, 255) if selected == 0 else (150, 150, 150)
        back_text = "Back"
        back_surf = back_font.render(back_text, True, back_color)
        back_rect = back_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80))
        screen.blit(back_surf, back_rect.topleft)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key in (pygame.K_UP, pygame.K_DOWN):
                    # Only one option, so toggle selection
                    selected = 0
                elif event.key == pygame.K_RETURN:
                    play_button_sound()
                    if selected == 0:  # Back button selected
                        return
            elif event.type == pygame.MOUSEMOTION:
                if back_rect.collidepoint(event.pos):
                    selected = 0
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back_rect.collidepoint(event.pos):
                    play_button_sound()
                    return

        clock.tick(60)

# THANK YOU SCREEN
def show_thank_you_screen():
    thank_font = pygame.font.SysFont(None, 64, bold=True)
    sub_font = pygame.font.SysFont(None, 32)
    timer = 0
    duration = 5

    while timer < duration:
        dt = clock.tick(60) / 1000
        timer += dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

        screen.fill((0, 0, 0))
        text_surf = thank_font.render("THANK YOU FOR PLAYING", True, (255, 255, 255))
        sub_surf = sub_font.render("Press ESC to quit", True, (200, 200, 200))
        screen.blit(text_surf, ((SCREEN_WIDTH - text_surf.get_width()) // 2, SCREEN_HEIGHT // 2 - 50))
        screen.blit(sub_surf, ((SCREEN_WIDTH - sub_surf.get_width()) // 2, SCREEN_HEIGHT // 2 + 20))
        pygame.display.flip()

# GAME FUNCTION
def start_game():
    # Reset entities
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

    # MAIN GAME LOOP
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
                elif event.key == pygame.K_m:  # M to mute/unmute
                    toggle_mute()
                elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:  # Increase ambient volume
                    change_ambient_volume(0.1)
                elif event.key == pygame.K_MINUS:  # Decrease ambient volume
                    change_ambient_volume(-0.1)

        # PLAYER UPDATE
        if not getattr(player, "disable_input", False):
            player.handle_input()
        player.update(dt)

        # ORBS UPDATE
        for orb in orbs:
            orb.update(dt)
            orb.offset_y = math.sin(time_accumulator * 2 + orb.tile_x + orb.tile_y) * 5
            if not orb.collected and orb.check_collision(player.hitbox):
                orb.collected = True
                play_orb_sound()
        orbs_collected = sum(1 for orb in orbs if orb.collected)

        # SHRINE UPDATE
        shrine_manager.update(player, message_manager, orbs_collected, dt)

        # CAMERA CALCULATION
        camera_x = player.rect.centerx - SCREEN_WIDTH // 2
        camera_y = player.rect.centery - SCREEN_HEIGHT // 2
        camera_x = max(0, min(camera_x, tilemap.width * tilemap.tile_size - SCREEN_WIDTH))
        camera_y = max(0, min(camera_y, tilemap.height * tilemap.tile_size - SCREEN_HEIGHT))

        # DRAW WORLD & LIGHT
        screen.fill((10, 10, 10))
        tilemap.draw(screen, camera_x, camera_y)
        for orb in orbs:
            orb.draw(screen, camera_x, camera_y, tile_size=tilemap.tile_size)
        shrine_manager.draw(screen)

        fog = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        fog.fill((0, 0, 0, 220))

        player_pos = (int(player.rect.centerx - camera_x), int(player.rect.centery - camera_y))
        draw_light(fog, player_pos, int(player_light_radius), int(player_light_radius*0.8), intensity=80)

        # Shrine light
        for shrine in shrine_manager.shrines + ([shrine_manager.main_shrine] if shrine_manager.main_shrine else []):
            if shrine is None: continue
            shrine_pos_screen = (
                int(shrine.rect.centerx - camera_x),
                int(shrine.rect.centery - camera_y - 35)
            )
            if shrine == shrine_manager.main_shrine and orbs_collected == total_orbs:
                if player.rect.colliderect(shrine.rect):
                    player_at_main_shrine = True
                if player_at_main_shrine:
                    main_shrine_light_radius += main_shrine_expand_speed * dt
                    radius = min(main_shrine_light_radius, main_shrine_max_radius)
                    draw_light(fog, shrine_pos_screen, radius, radius, intensity=150)
                else:
                    draw_light(fog, shrine_pos_screen, 15, 40, intensity=120)
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

        # CHECK COMPLETION
        # Trigger end sequence when player is at main shrine and all orbs collected
        if player_at_main_shrine and orbs_collected == total_orbs and not game_completed:
            game_completed = True  # ensure this block runs only once

            # Show final shrine message while light expands
            message_manager.add_message(
                "The six Spheres are whole. The original light is reborn through your courage, Bringer of Dawn. Now, command the dawn!",
                duration_seconds=4
            )

            while main_shrine_light_radius < main_shrine_max_radius:
                dt = clock.tick(60) / 1000
                main_shrine_light_radius += main_shrine_expand_speed * dt
                radius = min(main_shrine_light_radius, main_shrine_max_radius)

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()

                # Draw world
                screen.fill((10, 10, 10))
                tilemap.draw(screen, camera_x, camera_y)
                player.draw(screen, camera_x, camera_y)

                # Fog + expanding shrine light
                fog.fill((0, 0, 0, 220))
                draw_light(fog,
                        (shrine_manager.main_shrine.rect.centerx - camera_x,
                            shrine_manager.main_shrine.rect.centery - camera_y - 35),
                        int(radius), int(radius),
                        intensity=150)
                screen.blit(fog, (0, 0))

                # Draw message
                message_manager.update()
                message_manager.draw(screen)

                # Orbs counter (optional)
                orb_text = font.render(f"Orbs: {orbs_collected}/{len(orbs)}", True, (255, 255, 255))
                screen.blit(orb_text, (SCREEN_WIDTH - orb_text.get_width() - 10, 10))

                pygame.display.flip()

            # Once fully expanded, show final thank-you screen
            show_thank_you_screen()
            running = False

# OUTER LOOP
while True:
    main_menu()
    show_opening_scene()
    start_game()  # plays one round of the game; returns to main menu after finish
