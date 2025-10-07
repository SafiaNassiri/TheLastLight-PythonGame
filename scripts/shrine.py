import pygame
import sys

class Shrine:
    def __init__(self, x, y, max_light=5, name="Shrine", lore=""):
        self.rect = pygame.Rect(x, y, 32, 32)
        self.light = 0
        self.max_light = max_light
        self.name = name
        self.color = (100, 200, 255)
        self.activated = False
        self.lore = lore
        self.message_shown = False
        self.player_inside = False  # track if player is currently at shrine

        # For end sequence visual
        self.end_radius = 0

    def draw(self, surface):
        color = (255, 255, 100) if self.activated else self.color
        pygame.draw.rect(surface, color, self.rect)

    def add_light(self):
        if self.light < self.max_light:
            self.light += 1
            if self.light >= self.max_light:
                self.activated = True
            return True
        return False


class ShrineManager:
    def __init__(self, tilemap, total_orbs):
        self.shrines = []
        self.main_shrine = None
        self.total_orbs = total_orbs
        self.main_shrine_player_inside = False

        # End sequence variables
        self.ending = False
        self.end_timer = 0 
        self.shrine_radius = 50
        self.fade_alpha = 0

        # Define custom messages per shrine_logic tile
        custom_messages = {
            (10, 82): "A brave heart is the only compass needed in the dark.",
            (14, 86): "The Fog cannot claim what is immune to doubt. Your path is lit from within.",
            (18, 82): "Take this first light. The longest journey begins not with a step, but with a promise.",
            (47, 66): "Where time has ceased, the sun's persistence waits beneath the broken hour.",
            (81, 77):  "Silence reigns in this forgotten place, but memory is stored in this shard of dawn.",
            (25, 14): "Life finds a way, even in shadows; this light blossoms from forgotten stone."
        }

        # Regular shrines
        shrine_logic_layer = tilemap.layers.get("shrine_logic", [])
        for y, row in enumerate(shrine_logic_layer):
            for x, tile in enumerate(row):
                if tile:
                    world_x = x * tilemap.tile_size
                    world_y = y * tilemap.tile_size
                    lore_msg = custom_messages.get(
                        (x, y),
                        f"You step onto a Shrine at ({x},{y}) and feel a faint warmth..."
                    )
                    self.shrines.append(
                        Shrine(world_x, world_y, max_light=5, name=f"Shrine {len(self.shrines)+1}", lore=lore_msg)
                    )

        # Main shrine
        main_layer = tilemap.layers.get("main_shrine_marker", [])
        for y, row in enumerate(main_layer):
            for x, tile in enumerate(row):
                if tile:
                    world_x = x * tilemap.tile_size
                    world_y = y * tilemap.tile_size
                    self.main_shrine = Shrine(world_x, world_y, max_light=10, name="Main Shrine")
                    self.main_shrine.player_inside = False

    def update(self, player, message_manager, orbs_collected, dt):
        # Regular shrine interactions
        for shrine in self.shrines:
            colliding = player.hitbox.colliderect(shrine.rect)
            if colliding and not shrine.player_inside:
                if shrine.add_light() or not shrine.message_shown:
                    message_manager.add_message(shrine.lore, duration_seconds=1.5)
                    shrine.message_shown = True
            shrine.player_inside = colliding

        # Main shrine interaction
        if self.main_shrine:
            colliding = player.hitbox.colliderect(self.main_shrine.rect)

            if colliding and not self.ending:
                # Determine message based on orbs collected
                if orbs_collected == 0:
                    text = "The vessel is empty. The shadow still prevails. Seek the six fragments, Bringer of Dawn, and bring them home."
                elif orbs_collected < self.total_orbs:
                    text = "You've gathered some light but it isn't enough yet. You grow nearer to the dawn, brave one."
                else:  # orbs_collected == total_orbs
                    text = "The six Spheres are whole. The original light is reborn through your courage, Bringer of Dawn. Now, command the dawn!"
                    self.ending = True
                    player.disable_input = True

                # Show message only once per shrine visit
                if not self.main_shrine.message_shown:
                    message_manager.add_message(text, duration_seconds=2)
                    self.main_shrine.message_shown = True

            # Reset message_shown if player leaves shrine
            if not colliding:
                self.main_shrine.message_shown = False

            self.main_shrine_player_inside = colliding

        # End sequence animation
        if self.ending:
            self.end_timer += dt
            self.main_shrine.end_radius += 300 * dt  # px per second

            # Fade to black when radius covers the screen diagonal
            screen_diag = (pygame.display.get_surface().get_width() ** 2 +
                        pygame.display.get_surface().get_height() ** 2) ** 0.5
            if self.main_shrine.end_radius >= screen_diag / 2:
                self.fade_alpha = min(255, self.fade_alpha + 150 * dt)

            # Trigger closing scene when fade is complete
            if self.fade_alpha >= 255:
                self.show_closing_scene()

    def draw(self, surface):
        for shrine in self.shrines:
            shrine.draw(surface)
            # Draw oval light around regular shrines
            oval_width, oval_height = 30, 50
            light_surf = pygame.Surface((oval_width*2, oval_height*2), pygame.SRCALPHA)
            pygame.draw.ellipse(light_surf, (255, 255, 200, 120), (0, 0, oval_width*2, oval_height*2))
            shrine_center = shrine.rect.center
            surface.blit(light_surf, (shrine_center[0]-oval_width, shrine_center[1]-oval_height), special_flags=pygame.BLEND_RGBA_ADD)

        if self.main_shrine:
            self.main_shrine.draw(surface)
            # Draw main shrine light as circle
            if self.ending and self.main_shrine.end_radius > 0:
                pygame.draw.circle(surface, (255, 255, 200),
                                self.main_shrine.rect.center,
                                int(self.main_shrine.end_radius))
            else:
                # Regular main shrine glow before end sequence
                radius = 50
                light_surf = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
                pygame.draw.circle(light_surf, (255, 255, 200, 120), (radius, radius), radius)
                shrine_center = self.main_shrine.rect.center
                surface.blit(light_surf, (shrine_center[0]-radius, shrine_center[1]-radius), special_flags=pygame.BLEND_RGBA_ADD)

        # Fade overlay for end sequence
        if self.ending and self.fade_alpha > 0:
            fade_surf = pygame.Surface(surface.get_size())
            fade_surf.fill((0, 0, 0))
            fade_surf.set_alpha(int(self.fade_alpha))
            surface.blit(fade_surf, (0, 0))

    def show_closing_scene(self):
        closing_screen = pygame.display.get_surface()
        closing_screen.fill((0, 0, 0))
        font = pygame.font.Font(None, 64)
        text = font.render("Thank you for playing", True, (255, 255, 255))
        rect = text.get_rect(center=closing_screen.get_rect().center)
        closing_screen.blit(text, rect)
        pygame.display.flip()
        pygame.time.wait(4000)
        pygame.quit()
        sys.exit()
