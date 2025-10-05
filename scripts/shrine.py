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

        # Define custom messages per shrine_logic tile
        # Format: {(tile_x, tile_y): "unique message"}
        custom_messages = {
            (10, 82): "A cold wind brushes past your face, carrying whispers of forgotten paths.",
            (14, 86): "The shrine hums softly as you step on it, illuminating your feet in a pale blue glow.",
            (18, 82): "A faint warmth spreads from the shrine, revealing ancient markings on the ground.",
            (47, 66): "The shrine flickers for a moment, and you feel a subtle pulse beneath your steps.",
            (81, 77): "You sense a quiet presence watching from the shadows, only the shrine’s light comforting you.",
            (25, 14): "The air grows still as you approach; the shrine glows stronger as if acknowledging your presence."
        }

        # Regular shrines: spawn only where "shrine_logic" layer has a marker
        shrine_logic_layer = tilemap.layers.get("shrine_logic", [])
        for y, row in enumerate(shrine_logic_layer):
            for x, tile in enumerate(row):
                if tile:
                    world_x = x * tilemap.tile_size
                    world_y = y * tilemap.tile_size

                    # Assign unique message if defined, else default
                    lore_msg = custom_messages.get(
                        (x, y),
                        f"You step onto a Shrine at ({x},{y}) and feel a faint warmth..."
                    )

                    self.shrines.append(
                        Shrine(world_x, world_y, max_light=5, name=f"Shrine {len(self.shrines)+1}", lore=lore_msg)
                    )

        # Main shrine: spawn on the "main_shrine_marker" layer
        main_layer = tilemap.layers.get("main_shrine_marker", [])
        for y, row in enumerate(main_layer):
            for x, tile in enumerate(row):
                if tile:
                    world_x = x * tilemap.tile_size
                    world_y = y * tilemap.tile_size
                    self.main_shrine = Shrine(world_x, world_y, max_light=10, name="Main Shrine")
                    self.main_shrine.player_inside = False

    def update(self, player, message_manager, orbs_collected):
        # Regular shrines
        for shrine in self.shrines:
            colliding = player.hitbox.colliderect(shrine.rect)
            if colliding and not shrine.player_inside:
                # Player just stepped onto this shrine tile
                shrine.add_light()
                message_manager.add_message(shrine.lore)
            shrine.player_inside = colliding  # update for next frame

        # Main shrine
        if self.main_shrine:
            colliding = player.hitbox.colliderect(self.main_shrine.rect)
            if colliding and not self.main_shrine_player_inside:
                # Player just entered main shrine
                if orbs_collected == 0:
                    message_manager.add_message("The Main Shrine remains dormant. You have no light orbs!")
                elif orbs_collected < self.total_orbs:
                    message_manager.add_message(f"The Main Shrine senses {orbs_collected}/{self.total_orbs} orbs collected. More light is needed!")
                else:
                    message_manager.add_message("All orbs collected! The Main Shrine awakens and the world is restored!")
                    pygame.display.flip()
                    pygame.time.wait(2000)
                    pygame.quit()
                    sys.exit()
            self.main_shrine_player_inside = colliding

    def draw(self, surface):
        for shrine in self.shrines:
            shrine.draw(surface)
        if self.main_shrine:
            self.main_shrine.draw(surface)
