import pygame, os, json

class TileMap:
    # Layers to draw in game (draw order matters!)
    VISIBLE_LAYERS = [
        "floor",
        "wall",
        "props",
        "shrines",   # draw shrines first
        "spawner",
        "props2",
    ]
    # Layers considered solid for collision
    SOLID_LAYERS = ["wall", "props", "shrines"]

    # Layers that store logic markers (no sheet/id)
    LOGIC_LAYERS = ["spawnpoints", "orb_spawn", "main_shrine_marker", "shrine_logic"]

    def __init__(self, map_file, tile_size=32):
        self.tile_size = tile_size
        self.layers = {}
        self.sheet_cache = {}   # full sheet surfaces
        self.subtiles = {}      # individual tile surfaces per sheet

        # Load JSON map
        if not os.path.exists(map_file):
            raise FileNotFoundError(f"Map file {map_file} not found")
        with open(map_file, encoding="utf-8") as f:
            data = json.load(f)

        self.width = data.get("width", 0)
        self.height = data.get("height", 0)

        # Initialize empty 2D layers
        for lname in data.get("layers", {}):
            self.layers[lname] = [[None for _ in range(self.width)] for _ in range(self.height)]

        # Fill tiles from saved map
        for lname, tile_list in data.get("layers", {}).items():
            layer_grid = self.layers[lname]
            for t in tile_list:
                x, y = t.get("x"), t.get("y")
                if x is None or y is None:
                    continue
                if 0 <= x < self.width and 0 <= y < self.height:
                    if lname in self.LOGIC_LAYERS:
                        layer_grid[y][x] = t.get("type", None)
                    else:
                        # Make sure "sheet" and "id" exist, else skip
                        sheet = t.get("sheet")
                        tid = t.get("id")
                        if sheet is not None and tid is not None:
                            layer_grid[y][x] = {"sheet": sheet.replace("\\","/"), "id": tid}

    def load_sheet(self, path):
        """Load full tilesheet and cache it."""
        if path not in self.sheet_cache:
            if not os.path.exists(path):
                raise FileNotFoundError(f"Tilesheet {path} not found")
            sheet = pygame.image.load(path).convert_alpha()
            self.sheet_cache[path] = sheet
        return self.sheet_cache[path]

    def get_subtiles(self, sheet_path):
        """Split a sheet into individual tile surfaces and cache."""
        if sheet_path in self.subtiles:
            return self.subtiles[sheet_path]

        sheet = self.load_sheet(sheet_path)
        w, h = sheet.get_width(), sheet.get_height()
        tiles = []
        for y in range(0, h, self.tile_size):
            for x in range(0, w, self.tile_size):
                rect = pygame.Rect(x, y, self.tile_size, self.tile_size)
                tiles.append(sheet.subsurface(rect).copy())
        self.subtiles[sheet_path] = tiles
        return tiles

    def draw(self, surface, camera_x=0, camera_y=0):
        """Draw visible layers on screen in proper order."""
        # Enforce correct draw order: props2 always on top of shrines
        draw_order = ["floor", "wall", "props", "shrines", "props2", "spawner"]
        for lname in draw_order:
            layer = self.layers.get(lname)
            if not layer:
                continue
            for y, row in enumerate(layer):
                for x, t in enumerate(row):
                    if t is None:
                        continue
                    if isinstance(t, dict) and "sheet" in t:
                        tiles = self.get_subtiles(t["sheet"])
                        idx = t["id"]
                        if 0 <= idx < len(tiles):
                            surface.blit(
                                tiles[idx],
                                (x*self.tile_size - camera_x, y*self.tile_size - camera_y)
                            )

    def is_solid(self, rect):
        """Check if a player's rect collides with solid tiles."""
        foot_y = rect.bottom - 1
        points_to_check = [
            (rect.left + 2, foot_y),
            (rect.right - 3, foot_y),
            (rect.centerx, foot_y)
        ]

        for px, py in points_to_check:
            tile_x = px // self.tile_size
            tile_y = py // self.tile_size

            # Out-of-bounds is solid
            if tile_x < 0 or tile_x >= self.width or tile_y < 0 or tile_y >= self.height:
                return True

            # Check floor
            floor_layer = self.layers.get("floor", [])
            if not floor_layer[tile_y][tile_x]:
                return True

            # Check other solid layers
            for lname in self.SOLID_LAYERS:
                layer = self.layers.get(lname, [])
                if layer and layer[tile_y][tile_x]:
                    return True

        return False
