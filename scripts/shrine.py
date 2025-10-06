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
        self.player_inside = False  # track if player is currently on shrine

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
                shrine.add_light()
                message_manager.add_message(shrine.lore)
            shrine.player_inside = colliding

        # Main shrine interaction
        if self.main_shrine:
            colliding = player.hitbox.colliderect(self.main_shrine.rect)
            if colliding and not self.main_shrine_player_inside:
                if orbs_collected == 0:
                    message_manager.add_message(
                        "The vessel is empty. The shadow still prevails. Seek the six fragments, Bringer of Dawn, and bring them home."
                    )
                elif orbs_collected < self.total_orbs:
                    message_manager.add_message(
                        "Your light grows, Bringer of Dawn. The vessel now holds enough power to speak, but not enough to shine. The full dawn still awaits completion."
                    )
                elif orbs_collected >= self.total_orbs:
                    # Trigger end sequence instead of quitting immediately
                    if not self.ending:
                        message_manager.add_message(
                            "The six Spheres are whole. The original light is reborn through your courage, Bringer of Dawn. Now, command the dawn!"
                        )
                        self.ending = True
                        player.disable_input = True

            self.main_shrine_player_inside = colliding

        # Handle end sequence animation
        if self.ending:
            self.end_timer += dt

            # Increase shrine radius
            self.main_shrine.end_radius += 300 * dt  # pixels per second

            # Fade to black after radius fills screen
            screen_diag = (pygame.display.get_surface().get_width() ** 2 +
                           pygame.display.get_surface().get_height() ** 2) ** 0.5
            if self.main_shrine.end_radius >= screen_diag / 2:
                self.fade_alpha = min(255, self.fade_alpha + 150 * dt)

            # Close game when fade is complete
            if self.fade_alpha >= 255:
                self.show_closing_scene()

    def draw(self, surface):
        for shrine in self.shrines:
            shrine.draw(surface)
            # Draw oval light around regular shrines
            oval_width, oval_height = 30, 50  # adjust for desired oval shape
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
