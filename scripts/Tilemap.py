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
        path = path.replace("\\", "/")  # fix slashes
        if path not in self.sheet_cache:
            if not os.path.exists(path):
                raise FileNotFoundError(f"Tilesheet {path} not found")
            self.sheet_cache[path] = pygame.image.load(path).convert_alpha()
        return self.sheet_cache[path]

    def draw(self, surface, camera_x=0, camera_y=0):
        for lname, layer in self.layers.items():
            if not layer:
                continue
            for tile in layer:
                if isinstance(tile, dict) and "sheet" in tile:
                    sheet = self.load_sheet(tile["sheet"])
                    tile_id = tile["id"]
                    tiles_per_row = sheet.get_width() // self.tile_size
                    tx = (tile_id % tiles_per_row) * self.tile_size
                    ty = (tile_id // tiles_per_row) * self.tile_size
                    surface.blit(
                        sheet,
                        (tile["x"]*self.tile_size - camera_x, tile["y"]*self.tile_size - camera_y),
                        pygame.Rect(tx, ty, self.tile_size, self.tile_size)
                    )
                elif isinstance(tile, str):  # spawn/placeholder
                    color_map = {"player": (0,255,0), "goblin": (255,0,0), "treasure": (0,0,255)}
                    color = color_map.get(tile, (255,255,255))
                    surf = pygame.Surface((self.tile_size, self.tile_size), pygame.SRCALPHA)
                    surf.fill(color)
                    surface.blit(surf, (tile["x"]*self.tile_size - camera_x, tile["y"]*self.tile_size - camera_y))
