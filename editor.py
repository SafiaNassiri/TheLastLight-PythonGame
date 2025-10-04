# editor.py
import pygame, json, os, sys

TILE_SIZE = 32
MAP_WIDTH, MAP_HEIGHT = 100, 100

pygame.init()
screen = pygame.display.set_mode((800, 600), pygame.RESIZABLE)
pygame.display.set_caption("Map Editor")
font = pygame.font.SysFont(None, 20)

# -----------------------------
# Camera & zoom
camera_x, camera_y = 0, 0
CAMERA_SPEED = 10
zoom = 1.0  # initial zoom

# fullscreen flag
is_fullscreen = False

# -----------------------------
# Drag painting state
dragging = False
drag_start = None  # (tx, ty)
erasing = False
erase_start = None

# -----------------------------
# Tile size per sheet
sheet_configs = {
    "TX Tileset Grass.png": 32,
    "TX Tileset Stone Ground.png": 32,
    "TX Tileset Wall.png": 32,
    "TX Plant.png": 32,
    "TX Struct.png": 32,
    "TX Props with Shadow.png": 32
}

# -----------------------------
# Map layers
layers = {
    "wall": [[None for _ in range(MAP_WIDTH)] for _ in range(MAP_HEIGHT)],
    "floor": [[None for _ in range(MAP_WIDTH)] for _ in range(MAP_HEIGHT)],
    "stairs/gateways": [[None for _ in range(MAP_WIDTH)] for _ in range(MAP_HEIGHT)],
    "props": [[None for _ in range(MAP_WIDTH)] for _ in range(MAP_HEIGHT)],
    "shrines": [[None for _ in range(MAP_WIDTH)] for _ in range(MAP_HEIGHT)],
    "spawnpoints": [[None for _ in range(MAP_WIDTH)] for _ in range(MAP_HEIGHT)],
    "plants": [[None for _ in range(MAP_WIDTH)] for _ in range(MAP_HEIGHT)]
}
layer_order = ["floor","wall","stairs/gateways","props","shrines","plants","spawnpoints"]
current_layer = "floor"

spawn_marker_colors = {
    "player": (0, 255, 0, 128),
    "knight": (255, 0, 0, 128),
    "skeleton": (0, 0, 255, 128)
}
placing_spawn = False
selected_spawn_type = "player"

# -----------------------------
# Tile name mapping
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
        for fname in sorted(files):
            if not fname.lower().endswith((".png", ".jpg", ".jpeg")):
                continue
            full = os.path.join(root, fname)
            try:
                img = pygame.image.load(full).convert_alpha()
            except Exception as e:
                print("Failed to load", full, e)
                continue

            tile_size = sheet_configs.get(fname, 32)

            sheet_tiles = []
            max_x = (img.get_width() // tile_size) * tile_size
            max_y = (img.get_height() // tile_size) * tile_size
            cols = max_x // tile_size
            rows = max_y // tile_size

            for y in range(0, max_y, tile_size):
                for x in range(0, max_x, tile_size):
                    rect = pygame.Rect(x, y, tile_size, tile_size)
                    sub = img.subsurface(rect).copy()
                    sheet_tiles.append(sub)

            if sheet_tiles:
                sheets.append({
                    "path": full,
                    "basename": fname,
                    "display_name": get_tile_name(fname),
                    "tiles": sheet_tiles,
                    "tile_size": tile_size,
                    "full_img": img,
                    "cols": cols,
                    "rows": rows
                })
    return sheets

sheets = load_sheets()
if not sheets:
    raise FileNotFoundError("No tilesheet files found under assets/tiles/")

print("Loaded sheets:")
for i, s in enumerate(sheets):
    print(i, "-", s["basename"], "->", s["display_name"], f"({len(s['tiles'])} tiles, {s['cols']}x{s['rows']})")

# -----------------------------
# Load sparse map
def load_map_sparse(filename="map.json"):
    if not os.path.exists(filename):
        return
    with open(filename, "r") as f:
        data = json.load(f)
    print(f"Loaded map from {filename}!")

    for lname in layers:
        layers[lname] = [[None for _ in range(MAP_WIDTH)] for _ in range(MAP_HEIGHT)]

    for lname, tiles in data.get("layers", {}).items():
        for t in tiles:
            x, y = t["x"], t["y"]
            if 0 <= x < MAP_WIDTH and 0 <= y < MAP_HEIGHT:
                if lname == "spawnpoints":
                    layers[lname][y][x] = t["type"]
                else:
                    layers[lname][y][x] = {"sheet": t["sheet"], "id": t["id"]}
load_map_sparse()

# -----------------------------
# Hotkeys
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
    "[1..5] Switch sheet",
    "[A/W/S/D] Move camera",
    "[Mouse wheel] Zoom in/out",
    "[Z] Reset zoom | [R] Recenter camera",
    "[T] Toggle spawn placement | [Y] Cycle spawn type",
    "[L] Switch layer",
    "[[ / ]] Cycle tiles",
    "[C] Next sheet",
    "[F11] Toggle fullscreen",
    "Left Click: Place tile/spawn",
    "Right Click: Erase",
    "[P] Save map",
    "Click tilesheet preview to select tile"
]

# -----------------------------
# Sparse save
def save_map_sparse(filename="map.json"):
    map_data = {"width": MAP_WIDTH, "height": MAP_HEIGHT, "layers": {}}
    for lname, layer in layers.items():
        map_data["layers"][lname] = []
        for y, row in enumerate(layer):
            for x, tile in enumerate(row):
                if tile is not None:
                    if lname == "spawnpoints":
                        map_data["layers"][lname].append({"x": x, "y": y, "type": tile})
                    else:
                        map_data["layers"][lname].append({
                            "x": x, "y": y,
                            "sheet": tile["sheet"],
                            "id": tile["id"]
                        })
    with open(filename, "w") as f:
        json.dump(map_data, f, indent=4)
    print(f"Map saved as {filename}!")

# -----------------------------
# Main loop
running = True
clock = pygame.time.Clock()

while running:
    dt = clock.tick(60) / 1000
    view_w, view_h = screen.get_size()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            # handle key presses (same as before)
            if event.key == pygame.K_LEFTBRACKET:
                selected_tile = (selected_tile - 1) % len(tileset)
            elif event.key == pygame.K_RIGHTBRACKET:
                selected_tile = (selected_tile + 1) % len(tileset)
            elif event.key == pygame.K_c:
                current_sheet = (current_sheet + 1) % len(sheets)
                tileset = sheets[current_sheet]["tiles"]
                selected_tile = 0
            elif event.key in hotkey_to_basename:
                fname = hotkey_to_basename[event.key]
                for i, s in enumerate(sheets):
                    if s["basename"] == fname:
                        current_sheet = i
                        tileset = s["tiles"]
                        selected_tile = 0
                        break
            elif event.key == pygame.K_z:
                zoom = 1.0
            elif event.key == pygame.K_r:
                camera_x, camera_y = 0, 0
            elif event.key == pygame.K_t:
                placing_spawn = not placing_spawn
                current_layer = "spawnpoints" if placing_spawn else "floor"
                print("Spawn placement:", placing_spawn)
            elif event.key == pygame.K_y:
                types = list(spawn_marker_colors.keys())
                idx = types.index(selected_spawn_type)
                selected_spawn_type = types[(idx + 1) % len(types)]
                print("Selected spawn type:", selected_spawn_type)
            elif event.key == pygame.K_l:
                idx = layer_order.index(current_layer)
                current_layer = layer_order[(idx + 1) % len(layer_order)]
                placing_spawn = (current_layer == "spawnpoints")
                print("Active layer:", current_layer)
            elif event.key == pygame.K_p:
                save_map_sparse()
            elif event.key == pygame.K_F11:
                fullscreen = not pygame.display.get_surface().get_flags() & pygame.FULLSCREEN
                if fullscreen:
                    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                else:
                    screen = pygame.display.set_mode((800, 600), pygame.RESIZABLE)

        elif event.type == pygame.MOUSEWHEEL:
            zoom += 0.1 * event.y
            zoom = max(0.25, min(2.0, zoom))

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            viewer_w, viewer_h = 320, 320
            viewer_x, viewer_y = 10, view_h - viewer_h - 10
            sheet = sheets[current_sheet]
            cols = sheet["cols"]
            rows = sheet["rows"]

            # Check if clicked inside tilesheet viewer
            if viewer_x <= mx <= viewer_x + viewer_w and viewer_y <= my <= viewer_y + viewer_h:
                cell_w = viewer_w / cols
                cell_h = viewer_h / rows
                col = int((mx - viewer_x) // cell_w)
                row = int((my - viewer_y) // cell_h)
                tile_index = row * cols + col
                if 0 <= tile_index < len(sheet["tiles"]):
                    selected_tile = tile_index
            else:
                # Click on map canvas
                if event.button in (1, 3):
                    tx = int((mx + camera_x) / (TILE_SIZE * zoom))
                    ty = int((my + camera_y) / (TILE_SIZE * zoom))
                if event.button == 1 and 0 <= tx < MAP_WIDTH and 0 <= ty < MAP_HEIGHT:
                    dragging = True
                    drag_start = (tx, ty)
                elif event.button == 3 and 0 <= tx < MAP_WIDTH and 0 <= ty < MAP_HEIGHT:
                    erasing = True
                    erase_start = (tx, ty)

        elif event.type == pygame.MOUSEBUTTONUP:
            mx, my = event.pos
            tx, ty = int((mx + camera_x) / (TILE_SIZE*zoom)), int((my + camera_y) / (TILE_SIZE*zoom))
            
            # LEFT CLICK: finish drawing
            if event.button == 1 and dragging:
                dragging = False
                x0, x1 = min(drag_start[0], tx), max(drag_start[0], tx)
                y0, y1 = min(drag_start[1], ty), max(drag_start[1], ty)
                for y in range(y0, y1 + 1):
                    for x in range(x0, x1 + 1):
                        if current_layer == "spawnpoints":
                            layers["spawnpoints"][y][x] = selected_spawn_type
                        else:
                            layers[current_layer][y][x] = {"sheet": sheets[current_sheet]["path"], "id": selected_tile}
            # RIGHT CLICK: finish drawing
            elif event.button == 3 and erasing:
                erasing = False
                x0, x1 = min(erase_start[0], tx), max(erase_start[0], tx)
                y0, y1 = min(erase_start[1],ty), max(erase_start[1], ty)
                for y in range(y0, y1 + 1):
                    for x in range(x0, x1 + 1):
                        layers[current_layer][y][x] = None


    # Continuous camera movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_a]: camera_x -= CAMERA_SPEED
    if keys[pygame.K_d]: camera_x += CAMERA_SPEED
    if keys[pygame.K_w]: camera_y -= CAMERA_SPEED
    if keys[pygame.K_s]: camera_y += CAMERA_SPEED

    # Draw
    screen.fill((30,30,30))
    for lname in layer_order:
        layer = layers[lname]
        for y, row in enumerate(layer):
            for x, t in enumerate(row):
                if t is None:
                    continue
                if lname == "spawnpoints":
                    color = spawn_marker_colors[t]
                    rect = pygame.Surface((TILE_SIZE*zoom, TILE_SIZE*zoom), pygame.SRCALPHA)
                    rect.fill(color)
                    screen.blit(rect, (x*TILE_SIZE*zoom - camera_x, y*TILE_SIZE*zoom - camera_y))
                else:
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

    # Draw drag rectangle preview
    if dragging and drag_start:
        mx, my = pygame.mouse.get_pos()
        tx, ty = int((mx + camera_x) / (TILE_SIZE*zoom)), int((my + camera_y) / (TILE_SIZE*zoom))
        x0, x1 = min(drag_start[0], tx), max(drag_start[0], tx)
        y0, y1 = min(drag_start[1], ty), max(drag_start[1], ty)
        s = pygame.Surface(((x1-x0+1)*TILE_SIZE*zoom, (y1-y0+1)*TILE_SIZE*zoom), pygame.SRCALPHA)
        s.fill((255, 255, 0, 80))
        screen.blit(s, (x0*TILE_SIZE*zoom - camera_x, y0*TILE_SIZE*zoom - camera_y))
    if erasing and erase_start:
        mx, my = pygame.mouse.get_pos()
        tx, ty = int((mx + camera_x) / (TILE_SIZE*zoom)), int((my + camera_y) / (TILE_SIZE*zoom))
        x0, x1 = min(erase_start[0], tx), max(erase_start[0], tx)
        y0, y1 = min(erase_start[1], ty), max(erase_start[1], ty)
        s = pygame.Surface(((x1-x0+1)*TILE_SIZE*zoom, (y1-y0+1)*TILE_SIZE*zoom), pygame.SRCALPHA)
        s.fill((255, 0, 0, 80))
        screen.blit(s, (x0*TILE_SIZE*zoom - camera_x, y0*TILE_SIZE*zoom - camera_y))


    # Draw grid
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
    tileset = sheet["tiles"]
    ui_text = f"Layer: {current_layer} | Sheet: {sheet['basename']} ({sheet['display_name']}) | Tile {selected_tile+1}/{len(tileset)} | Zoom: {zoom:.2f}"
    if placing_spawn:
        ui_text += f" | Spawn mode: {selected_spawn_type}"
    screen.blit(font.render(ui_text, True, (255,255,255)), (10, 8))

    # Preview bottom-right
    pv_x, pv_y = view_w - (TILE_SIZE*2 + 20), view_h - (TILE_SIZE*2 + 20)
    # translucent background
    bg_surf = pygame.Surface((TILE_SIZE*zoom + 10, TILE_SIZE*zoom + 20), pygame.SRCALPHA)
    bg_surf.fill((50, 50, 50, 160))  # semi-transparent gray
    screen.blit(bg_surf, (pv_x - 5, pv_y - 5))
    if tileset:
        preview = pygame.transform.scale(tileset[selected_tile], (int(TILE_SIZE*zoom), int(TILE_SIZE*zoom)))
        screen.blit(preview, (pv_x, pv_y))
        pygame.draw.rect(screen, (255,255,255), (pv_x, pv_y, TILE_SIZE*zoom, TILE_SIZE*zoom), 1)
        screen.blit(font.render(sheet["display_name"], True, (255,255,255)), (pv_x, pv_y + TILE_SIZE*zoom + 3))

    # Help
    for i, line in enumerate(help_lines):
        screen.blit(font.render(line, True, (200,200,200)), (10, 30 + i*18))

    # Tilesheet viewer
    viewer_w, viewer_h = 320, 320
    viewer_x, viewer_y = 10, view_h - viewer_h - 10
    # translucent background
    viewer_bg = pygame.Surface((viewer_w + 4, viewer_h + 4), pygame.SRCALPHA)
    viewer_bg.fill((50, 50, 50, 160))  # semi-transparent gray
    screen.blit(viewer_bg, (viewer_x - 2, viewer_y - 2))

    full_img = sheet["full_img"]
    cols = sheet["cols"]
    rows = sheet["rows"]
    if cols > 0 and rows > 0:
        scaled_sheet = pygame.transform.smoothscale(full_img.subsurface((0,0,cols*sheet["tile_size"], rows*sheet["tile_size"])), (viewer_w, viewer_h))
        screen.blit(scaled_sheet, (viewer_x, viewer_y))
        cell_w = viewer_w / cols
        cell_h = viewer_h / rows
        for c in range(cols + 1):
            x = viewer_x + int(c * cell_w)
            pygame.draw.line(screen, (50,50,50), (x, viewer_y), (x, viewer_y + viewer_h))
        for r in range(rows + 1):
            y = viewer_y + int(r * cell_h)
            pygame.draw.line(screen, (50,50,50), (viewer_x, y), (viewer_x + viewer_w, y))
        sel_col = selected_tile % cols
        sel_row = selected_tile // cols
        if sel_row < rows:
            hl_rect = pygame.Rect(viewer_x + sel_col * cell_w, viewer_y + sel_row * cell_h, cell_w, cell_h)
            pygame.draw.rect(screen, (255, 235, 59), hl_rect, 3)
    screen.blit(font.render("Sheet Preview (click to select)", True, (255,255,255)), (viewer_x, viewer_y - 18))

    pygame.display.flip()

pygame.quit()
sys.exit()
