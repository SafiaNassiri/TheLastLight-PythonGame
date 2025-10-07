import pygame, json, os, sys

TILE_SIZE = 32
MAP_WIDTH, MAP_HEIGHT = 100, 100

pygame.init()
screen = pygame.display.set_mode((800, 600), pygame.RESIZABLE)
pygame.display.set_caption("Map Editor")
font = pygame.font.SysFont(None, 20)

# Camera & zoom
camera_x, camera_y = 0, 0
CAMERA_SPEED = 10
zoom = 1.0
is_fullscreen = False

# States
dragging = False
erasing = False
drag_start = None
erase_start = None

placing_spawn = False
selected_spawn_type = "player"
current_layer = "floor"

# Tile size config
sheet_configs = {
    "TX Tileset Grass.png": 32,
    "TX Tileset Stone Ground.png": 32,
    "TX Tileset Wall.png": 32,
    "TX Plant.png": 32,
    "TX Struct.png": 32,
    "TX Props with Shadow.png": 32
}

# Layers
def make_layer():
    return [[None for _ in range(MAP_WIDTH)] for _ in range(MAP_HEIGHT)]

layers = {
    "floor": make_layer(),
    "stairs/gateways": make_layer(),
    "wall": make_layer(),
    "props": make_layer(),
    "props2": make_layer(),
    "shrines": make_layer(),
    "main_shrine_marker": make_layer(),
    "spawner": make_layer(),
    "plants": make_layer(),
    "orb_spawn": make_layer(),
    "spawnpoints": make_layer(),
    "shrine_logic": make_layer()
}

layer_order = [
    "floor","stairs/gateways","wall","props","shrines",
    "props2","main_shrine_marker","spawner","plants",
    "orb_spawn","shrine_logic","spawnpoints"
]

# Spawn marker colors
spawn_marker_colors = {
    "player": (0, 255, 0, 160),
    "orb": (255, 200, 0, 160),
    "shrine": (255, 0, 0, 160),
    "main_shrine": (100, 200, 255, 160)
}

spawn_layer_map = {
    "player": "spawnpoints",
    "orb": "orb_spawn",
    "shrine": "shrine_logic",
    "main_shrine": "main_shrine_marker"
}

# Load tilesheets
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
            tiles = []
            cols = img.get_width() // tile_size
            rows = img.get_height() // tile_size
            for y in range(rows):
                for x in range(cols):
                    rect = pygame.Rect(x * tile_size, y * tile_size, tile_size, tile_size)
                    tiles.append(img.subsurface(rect).copy())
            if tiles:
                sheets.append({
                    "path": full,
                    "basename": fname,
                    "tiles": tiles,
                    "tile_size": tile_size,
                    "cols": cols,
                    "rows": rows,
                    "full_img": img
                })
    return sheets

sheets = load_sheets()
if not sheets:
    raise FileNotFoundError("No tilesheets found under assets/tiles/")
current_sheet = 0
tileset = sheets[current_sheet]["tiles"]
selected_tile = 0

# Load/Save map
def load_map_sparse(filename="map.json"):
    if not os.path.exists(filename): return
    with open(filename, "r") as f: data = json.load(f)
    for lname in layers: layers[lname] = make_layer()
    for lname, tiles in data.get("layers", {}).items():
        if lname not in layers: continue
        for t in tiles:
            x, y = t["x"], t["y"]
            if lname in ("spawnpoints","orb_spawn","main_shrine_marker","shrine_logic"):
                layers[lname][y][x] = t["type"]
            else:
                layers[lname][y][x] = {"sheet": t["sheet"], "id": t["id"]}

def save_map_sparse(filename="map.json"):
    map_data = {"width": MAP_WIDTH, "height": MAP_HEIGHT, "layers": {}}
    for lname, layer in layers.items():
        map_data["layers"][lname] = []
        for y, row in enumerate(layer):
            for x, tile in enumerate(row):
                if tile is None: continue
                if lname in ("spawnpoints","orb_spawn","main_shrine_marker","shrine_logic"):
                    map_data["layers"][lname].append({"x": x,"y": y,"type": tile})
                else:
                    map_data["layers"][lname].append({"x": x,"y": y,"sheet": tile["sheet"],"id": tile["id"]})

    with open(filename, "w") as f: json.dump(map_data, f, indent=4)
    print(f"Map saved as {filename}!")

load_map_sparse()

# Help
help_lines = [
    "[1..5] Switch sheet",
    "[A/W/S/D] Move camera",
    "[Mouse wheel] Zoom in/out",
    "[Z] Reset zoom | [R] Recenter camera",
    "[T] Toggle spawn placement | [Y] Cycle spawn type",
    "[L] Switch layer | [C] Next sheet",
    "[F11] Toggle fullscreen",
    "Left Click: Place tile/spawn",
    "Right Click: Erase",
    "[P] Save map",
    "Click tilesheet preview to select tile"
]

# Main loop
running = True
clock = pygame.time.Clock()
while running:
    dt = clock.tick(60)/1000
    view_w, view_h = screen.get_size()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Keypresses
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p: save_map_sparse()
            elif event.key == pygame.K_t:
                placing_spawn = not placing_spawn
                current_layer = spawn_layer_map[selected_spawn_type] if placing_spawn else "floor"
            elif event.key == pygame.K_y and placing_spawn:
                types = list(spawn_marker_colors.keys())
                idx = types.index(selected_spawn_type)
                selected_spawn_type = types[(idx+1)%len(types)]
                current_layer = spawn_layer_map[selected_spawn_type]
            elif event.key == pygame.K_l:
                idx = layer_order.index(current_layer)
                current_layer = layer_order[(idx+1)%len(layer_order)]
            elif event.key == pygame.K_c:
                current_sheet = (current_sheet+1)%len(sheets)
                tileset = sheets[current_sheet]["tiles"]
                selected_tile = 0
                print("Switched sheet:", sheets[current_sheet]["basename"])
            elif event.key == pygame.K_F11:
                is_fullscreen = not is_fullscreen
                screen = pygame.display.set_mode((0,0),pygame.FULLSCREEN) if is_fullscreen else pygame.display.set_mode((800,600),pygame.RESIZABLE)

        # Mouse
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx,my = event.pos

            # Tilesheet viewer click (bottom-left)
            viewer_w, viewer_h = 320, 320
            viewer_x, viewer_y = 10, view_h - viewer_h - 10
            sheet = sheets[current_sheet]
            cols, rows = sheet["cols"], sheet["rows"]
            cell_w, cell_h = viewer_w/cols, viewer_h/rows
            if viewer_x <= mx <= viewer_x+viewer_w and viewer_y <= my <= viewer_y+viewer_h:
                sel_col = int((mx - viewer_x)/cell_w)
                sel_row = int((my - viewer_y)/cell_h)
                sel_col = min(max(sel_col,0), cols-1)
                sel_row = min(max(sel_row,0), rows-1)
                selected_tile = sel_row*cols + sel_col
                print(f"Selected tile {selected_tile} from sheet preview")
                continue

            # Map painting
            tx_map, ty_map = int((mx+camera_x)/(TILE_SIZE*zoom)), int((my+camera_y)/(TILE_SIZE*zoom))
            if 0 <= tx_map < MAP_WIDTH and 0 <= ty_map < MAP_HEIGHT:
                if event.button == 1:
                    if current_layer in ("spawnpoints","orb_spawn","main_shrine_marker","shrine_logic"):
                        layers[current_layer][ty_map][tx_map] = selected_spawn_type
                    else:
                        layers[current_layer][ty_map][tx_map] = {"sheet": sheets[current_sheet]["path"], "id": selected_tile}
                elif event.button == 3:
                    layers[current_layer][ty_map][tx_map] = None
        elif event.type == pygame.MOUSEWHEEL:
            zoom = max(0.25,min(2.0, zoom + event.y*0.1))

    # Movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_a]: camera_x -= CAMERA_SPEED
    if keys[pygame.K_d]: camera_x += CAMERA_SPEED
    if keys[pygame.K_w]: camera_y -= CAMERA_SPEED
    if keys[pygame.K_s]: camera_y += CAMERA_SPEED

    # Draw map
    screen.fill((30,30,30))
    for lname in layer_order:
        for y,row in enumerate(layers[lname]):
            for x,t in enumerate(row):
                if t is None: continue
                if lname in ("spawnpoints","orb_spawn","main_shrine_marker","shrine_logic"):
                    color = spawn_marker_colors.get(t,(255,255,255,150))
                    rect = pygame.Surface((TILE_SIZE*zoom,TILE_SIZE*zoom),pygame.SRCALPHA)
                    rect.fill(color)
                    screen.blit(rect,(x*TILE_SIZE*zoom - camera_x, y*TILE_SIZE*zoom - camera_y))
                else:
                    sheet_path, tile_id = t["sheet"], t["id"]
                    sheet_obj = next((s for s in sheets if os.path.basename(s["path"])==os.path.basename(sheet_path)), None)
                    if sheet_obj and 0<=tile_id<len(sheet_obj["tiles"]):
                        img = pygame.transform.scale(sheet_obj["tiles"][tile_id],(int(TILE_SIZE*zoom),int(TILE_SIZE*zoom)))
                        screen.blit(img,(x*TILE_SIZE*zoom - camera_x, y*TILE_SIZE*zoom - camera_y))

    # Grid
    for gx in range(MAP_WIDTH+1):
        pygame.draw.line(screen,(60,60,60),(gx*TILE_SIZE*zoom - camera_x,0),(gx*TILE_SIZE*zoom - camera_x,view_h))
    for gy in range(MAP_HEIGHT+1):
        pygame.draw.line(screen,(60,60,60),(0, gy*TILE_SIZE*zoom - camera_y),(view_w, gy*TILE_SIZE*zoom - camera_y))

    # HUD
    ui_text = f"[Spawn Mode] {selected_spawn_type}" if placing_spawn else f"[Tile Mode] Layer: {current_layer}"
    screen.blit(font.render(ui_text,True,(255,255,255)),(10,8))

    # Help
    for i,line in enumerate(help_lines):
        screen.blit(font.render(line,True,(200,200,200)),(10,30+i*18))

    # Tilesheet viewer (bottom-left)
    sheet = sheets[current_sheet]
    viewer_w, viewer_h = 320, 320
    viewer_x, viewer_y = 10, view_h - viewer_h - 10
    viewer_bg = pygame.Surface((viewer_w+4, viewer_h+4),pygame.SRCALPHA)
    viewer_bg.fill((50,50,50,160))
    screen.blit(viewer_bg,(viewer_x-2, viewer_y-2))
    full_img = sheet["full_img"]
    cols, rows = sheet["cols"], sheet["rows"]
    if cols>0 and rows>0:
        scaled_sheet = pygame.transform.smoothscale(full_img.subsurface((0,0,cols*sheet["tile_size"], rows*sheet["tile_size"])), (viewer_w, viewer_h))
        screen.blit(scaled_sheet,(viewer_x, viewer_y))
        cell_w, cell_h = viewer_w/cols, viewer_h/rows
        for c in range(cols+1):
            x = viewer_x + int(c*cell_w)
            pygame.draw.line(screen,(50,50,50),(x,viewer_y),(x,viewer_y+viewer_h))
        for r in range(rows+1):
            y = viewer_y + int(r*cell_h)
            pygame.draw.line(screen,(50,50,50),(viewer_x,y),(viewer_x+viewer_w,y))
        sel_col = selected_tile % cols
        sel_row = selected_tile // cols
        if sel_row < rows:
            hl_rect = pygame.Rect(viewer_x + sel_col*cell_w, viewer_y + sel_row*cell_h, cell_w, cell_h)
            pygame.draw.rect(screen,(255,235,59),hl_rect,3)
    screen.blit(font.render("Sheet Preview (click to select)", True, (255,255,255)),(viewer_x,viewer_y-18))

    pygame.display.flip()

pygame.quit()
sys.exit()
