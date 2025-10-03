# editor.py
import pygame, json, os

TILE_SIZE = 32
MAP_WIDTH, MAP_HEIGHT = 100, 100

pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Map Editor")
font = pygame.font.SysFont(None, 20)

# -----------------------------
# Camera
camera_x, camera_y = 0, 0
CAMERA_SPEED = 10
zoom = 1.0  # initial zoom

# -----------------------------
# Map storage
tiles = [[None for _ in range(MAP_WIDTH)] for _ in range(MAP_HEIGHT)]

# -----------------------------
# Tile name mapping (optional)
tile_name_map = {
    "TX Plant.png": "Plant",
    "TX Struct.png": "Stairs",
    "TX Tileset Grass.png": "Grass",
    "TX Tileset Stone Ground.png": "Ground",
    "TX Tileset Wall.png": "Wall",
    "TX Props with Shadow.png": "Props"
}

def get_tile_name(filename):
    base = os.path.basename(filename)
    return tile_name_map.get(base, base.split('.')[0])

# -----------------------------
# Load all sheets
def load_sheets(base_dir="assets/tiles"):
    sheets = []
    for root, _, files in os.walk(base_dir):
        for fname in files:
            if not fname.lower().endswith((".png", ".jpg")):
                continue
            full = os.path.join(root, fname)
            try:
                img = pygame.image.load(full).convert_alpha()
            except Exception as e:
                print("Failed to load", full, e)
                continue
            sheet_tiles = []
            for y in range(0, img.get_height(), TILE_SIZE):
                for x in range(0, img.get_width(), TILE_SIZE):
                    sub = img.subsurface(pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)).copy()
                    if pygame.mask.from_surface(sub).count() > 0:
                        sheet_tiles.append(sub)
            if sheet_tiles:
                sheets.append({
                    "path": full,
                    "basename": fname,
                    "display_name": get_tile_name(fname),
                    "tiles": sheet_tiles
                })
    return sheets

sheets = load_sheets()
if not sheets:
    raise FileNotFoundError("No tilesheet files found under assets/tiles/")

print("Loaded sheets:")
for i, s in enumerate(sheets):
    print(i, "-", s["basename"], "->", s["display_name"], f"({len(s['tiles'])} tiles)")

# -----------------------------
# Hotkeys for quick sheet switching
hotkey_to_basename = {
    pygame.K_1: "TX Plant.png",
    pygame.K_2: "TX Struct.png",
    pygame.K_3: "TX Tileset Grass.png",
    pygame.K_4: "TX Tileset Wall.png",
    pygame.K_5: "TX Tileset Stone Ground.png"
}

current_sheet = 0
tileset = sheets[current_sheet]["tiles"]
selected_tile = 0

# -----------------------------
# Help text
help_lines = [
    "[1..5] Switch sheet (Plant, Stairs, Grass, Wall, Stone)",
    "[A/W/S/D] Move camera",
    "[Mouse wheel] Zoom in/out",
    "[Z] Reset zoom | [R] Recenter camera",
    "[[ / ]] Cycle tiles",
    "[C] Next sheet",
    "Left Click: Place tile",
    "Right Click: Erase tile",
    "[P] Save map"
]

# -----------------------------
# Main loop
running = True
clock = pygame.time.Clock()

while running:
    dt = clock.tick(60) / 1000  # delta time for smooth movement

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            # Cycle tiles
            if event.key == pygame.K_LEFTBRACKET:
                selected_tile = (selected_tile - 1) % len(tileset)
            elif event.key == pygame.K_RIGHTBRACKET:
                selected_tile = (selected_tile + 1) % len(tileset)

            # Next sheet
            elif event.key == pygame.K_c:
                current_sheet = (current_sheet + 1) % len(sheets)
                tileset = sheets[current_sheet]["tiles"]
                selected_tile = 0

            # Quick sheet hotkeys
            elif event.key in hotkey_to_basename:
                fname = hotkey_to_basename[event.key]
                for i, s in enumerate(sheets):
                    if s["basename"] == fname:
                        current_sheet = i
                        tileset = s["tiles"]
                        selected_tile = 0
                        break

            # Reset zoom
            elif event.key == pygame.K_z:
                zoom = 1.0

            # Recenter camera
            elif event.key == pygame.K_r:
                camera_x, camera_y = 0, 0

            # Save map
            elif event.key == pygame.K_p:
                map_data = {
                    "width": MAP_WIDTH,
                    "height": MAP_HEIGHT,
                    "tiles": tiles
                }
                with open("map.json", "w") as f:
                    json.dump(map_data, f, indent=4)
                print("Map saved!")

        elif event.type == pygame.MOUSEWHEEL:
            # Zoom in/out
            if event.y > 0:
                zoom = min(2.0, zoom + 0.1)
            else:
                zoom = max(0.25, zoom - 0.1)

    # Continuous camera movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_a]: camera_x -= CAMERA_SPEED
    if keys[pygame.K_d]: camera_x += CAMERA_SPEED
    if keys[pygame.K_w]: camera_y -= CAMERA_SPEED
    if keys[pygame.K_s]: camera_y += CAMERA_SPEED

    # Mouse placement
    mleft, mmid, mright = pygame.mouse.get_pressed()
    mx, my = pygame.mouse.get_pos()
    tx, ty = int((mx + camera_x) / (TILE_SIZE*zoom)), int((my + camera_y) / (TILE_SIZE*zoom))
    if 0 <= tx < MAP_WIDTH and 0 <= ty < MAP_HEIGHT:
        if mleft:
            tiles[ty][tx] = {"sheet": sheets[current_sheet]["path"], "id": selected_tile}
        elif mright:
            tiles[ty][tx] = None

    # -----------------------------
    # Draw
    screen.fill((30,30,30))

    # Draw placed tiles
    for y, row in enumerate(tiles):
        for x, t in enumerate(row):
            if t is None:
                continue
            sheet_path = t["sheet"]
            tile_id = t["id"]
            sheet_obj = None
            for s in sheets:
                if os.path.basename(s["path"]) == os.path.basename(sheet_path):
                    sheet_obj = s
                    break
            if sheet_obj and 0 <= tile_id < len(sheet_obj["tiles"]):
                img = pygame.transform.scale(sheet_obj["tiles"][tile_id], (int(TILE_SIZE*zoom), int(TILE_SIZE*zoom)))
                screen.blit(img, (x*TILE_SIZE*zoom - camera_x, y*TILE_SIZE*zoom - camera_y))

    # Draw grid
    view_w, view_h = screen.get_size()
    start_x = max(0, int(camera_x / (TILE_SIZE*zoom)))
    start_y = max(0, int(camera_y / (TILE_SIZE*zoom)))
    end_x = min(MAP_WIDTH, int((camera_x + view_w) / (TILE_SIZE*zoom)) + 2)
    end_y = min(MAP_HEIGHT, int((camera_y + view_h) / (TILE_SIZE*zoom)) + 2)

    for gx in range(start_x, end_x):
        px = gx * TILE_SIZE * zoom - camera_x
        pygame.draw.line(screen, (60,60,60), (px, 0), (px, view_h))
    for gy in range(start_y, end_y):
        py = gy * TILE_SIZE * zoom - camera_y
        pygame.draw.line(screen, (60,60,60), (0, py), (view_w, py))

    # UI
    sheet = sheets[current_sheet]
    ui_text = f"Sheet: {sheet['basename']} ({sheet['display_name']}) | Tile {selected_tile+1}/{len(tileset)} | Zoom: {zoom:.2f}"
    screen.blit(font.render(ui_text, True, (255,255,255)), (10, 8))

    # Preview bottom-right
    pv_x, pv_y = 700, 500
    if tileset:
        preview = pygame.transform.scale(tileset[selected_tile], (int(TILE_SIZE*zoom), int(TILE_SIZE*zoom)))
        screen.blit(preview, (pv_x, pv_y))
        pygame.draw.rect(screen, (255,255,255), (pv_x, pv_y, TILE_SIZE*zoom, TILE_SIZE*zoom), 1)
        screen.blit(font.render(sheet["display_name"], True, (255,255,255)), (pv_x, pv_y + TILE_SIZE*zoom + 3))

    # Help
    for i, line in enumerate(help_lines):
        screen.blit(font.render(line, True, (200,200,200)), (10, 30 + i*18))

    pygame.display.flip()

pygame.quit()
