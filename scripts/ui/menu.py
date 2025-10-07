import pygame, sys
from scripts.sounds import *
from scripts.ui.button import Button
from scripts.utils import wrap_text

def main_menu(screen, clock, SCREEN_WIDTH, SCREEN_HEIGHT, start_game, show_opening_scene, show_how_to_play):
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
                        show_options_menu(screen, clock, SCREEN_WIDTH, SCREEN_HEIGHT)
                    elif options[selected] == "How to Play":
                        show_how_to_play(screen, clock, SCREEN_WIDTH, SCREEN_HEIGHT)
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
                            show_options_menu(screen, clock, SCREEN_WIDTH, SCREEN_HEIGHT)
                            selected = 0
                        elif options[i] == "How to Play":
                            show_how_to_play(screen, clock, SCREEN_WIDTH, SCREEN_HEIGHT)
                            selected = 0
                        elif options[i] == "Quit":
                            pygame.quit()
                            sys.exit()

def show_options_menu(screen, clock, SCREEN_WIDTH, SCREEN_HEIGHT):
    import scripts.sounds as sounds  # make sure we import the module to use functions
    options_font = pygame.font.SysFont(None, 36)
    selected = 0
    option_items = ["Ambient Volume", "SFX Volume", "Back"]
    option_rects = []

    while True:
        screen.fill((0, 0, 0))
        y = 200
        option_rects.clear()

        # Draw options with current volume
        for i, item in enumerate(option_items):
            if item == "Ambient Volume":
                text = f"{item}: {int(sounds.ambient_volume*100)}% (LEFT/RIGHT to adjust)"
            elif item == "SFX Volume":
                text = f"{item}: {int(sounds.sfx_volume*100)}% (LEFT/RIGHT to adjust)"
            else:
                text = item

            color = (255, 255, 255) if i == selected else (150, 150, 150)
            surf = options_font.render(text, True, color)
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
                    sounds.play_button_sound()
                    if option_items[selected] == "Back":
                        return
                elif event.key == pygame.K_LEFT:
                    if option_items[selected] == "Ambient Volume":
                        sounds.change_ambient_volume(-0.05)
                        sounds.play_button_sound()
                    elif option_items[selected] == "SFX Volume":
                        sounds.change_sfx_volume(-0.05)
                        sounds.play_button_sound()
                elif event.key == pygame.K_RIGHT:
                    if option_items[selected] == "Ambient Volume":
                        sounds.change_ambient_volume(0.05)
                        sounds.play_button_sound()
                    elif option_items[selected] == "SFX Volume":
                        sounds.change_sfx_volume(0.05)
                        sounds.play_button_sound()
            elif event.type == pygame.MOUSEMOTION:
                for i, rect in enumerate(option_rects):
                    if rect.collidepoint(event.pos):
                        selected = i
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for i, rect in enumerate(option_rects):
                    if rect.collidepoint(event.pos):
                        sounds.play_button_sound()
                        if option_items[i] == "Back":
                            return

        clock.tick(60)

def show_how_to_play(screen, clock, SCREEN_WIDTH, SCREEN_HEIGHT):
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
