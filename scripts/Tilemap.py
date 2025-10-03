# tilemap.py
import pygame
import json

class TileMap:
    def __init__(self, map_file, tileset_image, tile_size):
        self.tile_size = tile_size
        self.tileset = pygame.image.load(tileset_image).convert_alpha()
        self.tiles = []
        self.load_map(map_file)

    def load_map(self, map_file):
        with open(map_file, 'r') as f:
            data = json.load(f)
        self.width = data['width']
        self.height = data['height']
        self.tiles = data['tiles']  # 2D list: [[0,1,2],[3,4,0],...]

    def draw(self, surface):
        for y, row in enumerate(self.tiles):
            for x, tile_id in enumerate(row):
                if tile_id is None:  # Empty tile
                    continue
                tile_rect = pygame.Rect(tile_id * self.tile_size, 0, self.tile_size, self.tile_size)
                surface.blit(self.tileset, (x*self.tile_size, y*self.tile_size), tile_rect)
