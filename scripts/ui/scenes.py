import pygame, sys, time
from scripts.utils import wrap_text
from scripts.ui.button import Button
from scripts.sounds import play_button_sound

def show_opening_scene(screen, clock, SCREEN_WIDTH, SCREEN_HEIGHT):
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
        ("Retrieve the six spheres of dawn.", 1),
        ("Three mark the start. The others are scattered:", 1),
        ("The overgrown garden.", 1),
        ("The hollow square.", 1),
        ("The forgotten plaza.", 1),
        ("Gather the six. Take them to the main shrine.", 4),
        ("Go. The fate of all light rests in your steps.", 0)
    ]

    screen.fill((0, 0, 0))
    pygame.display.flip()
    scene_font = pygame.font.SysFont(None, 28)
    displayed_lines = []
    skip_to_end = False

    # Button setup
    button_font = pygame.font.SysFont(None, 24)
    button_text = "Continue →"
    button_surf = button_font.render(button_text, True, (255, 255, 255))
    button_rect = button_surf.get_rect(bottomright=(SCREEN_WIDTH - 20, SCREEN_HEIGHT - 20))

    # Main loop for opening text
    for line, delay in lines:
        if skip_to_end:
            break
        displayed_lines.append(line)
        start_time = time.time()

        while time.time() - start_time < delay:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    skip_to_end = True

            screen.fill((0, 0, 0))
            y_offset = 60  # <-- slightly higher
            for text_line in displayed_lines:
                wrapped = wrap_text(text_line, scene_font, SCREEN_WIDTH - 40)
                for wrapped_line in wrapped:
                    surf = scene_font.render(wrapped_line, True, (255, 255, 255))
                    x = (SCREEN_WIDTH - surf.get_width()) // 2
                    screen.blit(surf, (x, y_offset))
                    y_offset += 30

            pygame.display.flip()
            clock.tick(60)

    # After all lines — show "Continue"
    displayed_lines = [l for l, _ in lines]
    waiting_for_continue = True
    while waiting_for_continue:
        mouse_pos = pygame.mouse.get_pos()
        hovered = button_rect.collidepoint(mouse_pos)
        color = (255, 255, 255) if hovered else (180, 180, 180)
        button_surf = button_font.render(button_text, True, color)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                play_button_sound()
                return
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if hovered:
                    play_button_sound()
                    return

        screen.fill((0, 0, 0))
        y_offset = 60
        for text_line in displayed_lines:
            wrapped = wrap_text(text_line, scene_font, SCREEN_WIDTH - 40)
            for wrapped_line in wrapped:
                surf = scene_font.render(wrapped_line, True, (255, 255, 255))
                x = (SCREEN_WIDTH - surf.get_width()) // 2
                screen.blit(surf, (x, y_offset))
                y_offset += 30

        screen.blit(button_surf, button_rect.topleft)
        pygame.display.flip()
        clock.tick(60)

def show_how_to_play(screen, clock, SCREEN_WIDTH, SCREEN_HEIGHT):
    instructions = [
        "HOW TO PLAY", "",
        "- Move with WASD",
        "- Collect all the orbs",
        "- Take them to the main shrine",
        "- Navigate the dark land to your destination", "",
        "- Press M to mute",
        "- Press ESC to quit game at any time",
    ]
    instr_font = pygame.font.SysFont(None, 32)
    back_font = pygame.font.SysFont(None, 28)
    selected = 0

    while True:
        screen.fill((0, 0, 0))
        y_offset = 100
        for line in instructions:
            surf = instr_font.render(line, True, (255, 255, 255))
            screen.blit(surf, ((SCREEN_WIDTH - surf.get_width()) // 2, y_offset))
            y_offset += 40

        # Back button
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
                if event.key in (pygame.K_RETURN, pygame.K_ESCAPE):
                    play_button_sound()
                    return
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if back_rect.collidepoint(event.pos):
                    play_button_sound()
                    return

        clock.tick(60)

def show_thank_you_screen(screen, clock, SCREEN_WIDTH, SCREEN_HEIGHT):
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
