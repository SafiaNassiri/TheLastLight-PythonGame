# The Last Light
A 2D exploration and resource collection game built with **Pygame**.  

## Overview
The world is shrouded in darkness, and all life is fading.  
You are the last survivor, tasked with restoring the **Shrine of Light** by gathering scattered orbs across a hostile land.  
As you bring back light, the world slowly heals, but shadow creatures and environmental dangers stand in your way.  

## Gameplay
- Explore a map 2D world filled with **enemies, hazards, and secrets**.  
- Collect **Light Orbs** and return them to the Shrine to expand its protective radius.

## Features (Planned & Implemented)
- [x] Create an editor.py for drawing Maps
- [x] Basic player movement  
- [x] Collectible orbs  
- [X] Shrine restoration  
- [x] Mini-shrines and lore objects
- [x] Main Menu and End Scene
- [x] Background and SFX sounds

## Project Structure
```text
TheLastLight/
├── __pycache__
├── asstes/
│   ├── entities/
│   │   ├── Player/
│   ├── sounds/
│   ├──tiles/
│   │   ├── Environment/
│   │   ├── Props/
├── scripts/
│   ├── ui/
│   ├── __pycache__/
│   ├── lighting.py
│   ├── message_manager.py
│   ├── orb.py
│   ├── player.py
│   ├── shrine.py
│   ├── sounds.py
│   ├── Tilemap.py
│   ├── utils.py
├── editor.py
├── main.py
├── map.json
└── README.md
```

## Inspiration
 - Hollow Knight – exploration + atmosphere
 - Don’t Starve – survival tension and darkness mechanics
 - Dark Souls – shrine/light as safe zones and progress markers
 - OneShot — game setting concept
