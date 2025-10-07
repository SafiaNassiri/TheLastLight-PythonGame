# The Last Light
A 2D exploration and resource collection game built with **Pygame**.  

## Overview
The world is shrouded in darkness, and all life is fading.  
You are the last survivor, tasked with restoring the **Shrine of Light** by gathering scattered orbs across a hostile land.  
As you bring back light, the world slowly heals, but shadow creatures and environmental dangers stand in your way.  

## Gameplay
- Explore a labyrinthine 2D world filled with **enemies, hazards, and secrets**.  
- Collect **Light Orbs** and return them to the Shrine to expand its protective radius.  
- Manage a **stamina bar** – sprinting, dashing, and attacking consume stamina, making exploration strategic.
- Encounter different **enemy types**:
  - Chasers – fast, fragile, relentless.  
  - Patrol Guards – predictable routes, dangerous in groups.  
  - Shadow Lurkers – invisible until close.  
  - Light Drainers – temporarily weaken your light radius.  
- Avoid **environmental hazards** like pits, spikes, collapsing floors, and moving walls.  
- Unlock shortcuts with **keys and gates**, and find **mini-shrines** for temporary safe zones.  
- Experience dynamic **sound design**:
  - Heartbeat when enemies are near.  
  - Whispers in the dark when light is low.  
  - Music layers in new instruments as you restore more orbs.  

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
 - OneShot - game setting concept
