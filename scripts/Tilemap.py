# scripts/Tilemap.py
import pygame, os, json

class TileMap:
    def __init__(self, map_file, tile_size=32):
        self.tile_size = tile_size
        self.layers = {}
        self.sheet_cache = {}

        # Load map JSON
        if not os.path.exists(map_file):
            raise FileNotFoundError(f"Map file {map_file} not found")
        with open(map_file) as f:
            data = json.load(f)

        self.width = data.get("width", 0)
        self.height = data.get("height", 0)
        self.layers = data.get("layers", {})

    def load_sheet(self, path):
        """Load and cache tilesheet."""
        if path not in self.sheet_cache:
            if not os.path.exists(path):
                raise FileNotFoundError(f"Tilesheet {path} not found")
            self.sheet_cache[path] = pygame.image.load(path).convert_alpha()
        return self.sheet_cache[path]

    def draw(self, surface):
        for lname, layer in self.layers.items():
            for y, row in enumerate(layer):
                for x, tile in enumerate(row):
                    if tile is None:
                        continue
                    # Spawn points (strings) – draw colored rect
                    if isinstance(tile, str):
                        color_map = {
                            "player": (0, 255, 0, 128),
                            "goblin": (255, 0, 0, 128),
                            "treasure": (0, 0, 255, 128)
                        }
                        color = color_map.get(tile, (255,255,255,128))
                        surf = pygame.Surface((self.tile_size, self.tile_size), pygame.SRCALPHA)
                        surf.fill(color)
                        surface.blit(surf, (x*self.tile_size, y*self.tile_size))
                    # Normal tile
                    elif isinstance(tile, dict):
                        sheet = self.load_sheet(tile["sheet"])
                        tile_id = tile["id"]
                        tiles_per_row = sheet.get_width() // self.tile_size
                        tx = (tile_id % tiles_per_row) * self.tile_size
                        ty = (tile_id // tiles_per_row) * self.tile_size
                        surface.blit(sheet, (x*self.tile_size, y*self.tile_size), pygame.Rect(tx, ty, self.tile_size, self.tile_size))
