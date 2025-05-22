import pygame
import os
import random
import math
from enum import Enum

# Initialize Pygame
pygame.init()

# Constants
TEXTURE_SIZE = 30
SAVE_DIR = "Asset/terrain"

def ensure_save_dir():
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)

def create_building_texture():
    surface = pygame.Surface((TEXTURE_SIZE, TEXTURE_SIZE))
    surface.fill((50, 50, 50))  # Dark gray background
    
    # Draw window patterns
    for i in range(2):
        for j in range(2):
            x = 5 + i * 12
            y = 5 + j * 12
            pygame.draw.rect(surface, (200, 200, 100), (x, y, 8, 8))  # Windows
    
    return surface

def create_plain_texture():
    surface = pygame.Surface((TEXTURE_SIZE, TEXTURE_SIZE))
    surface.fill((144, 238, 144))  # Light green background
    
    # Add grass details
    for _ in range(15):
        x = random.randint(0, TEXTURE_SIZE-1)
        y = random.randint(0, TEXTURE_SIZE-1)
        pygame.draw.line(surface, (34, 139, 34), 
                        (x, y), (x, y-3), 1)  # Grass blades
    
    return surface

def create_forest_texture():
    surface = pygame.Surface((TEXTURE_SIZE, TEXTURE_SIZE))
    surface.fill((34, 139, 34))  # Dark green background
    
    # Draw simple tree shapes
    for _ in range(3):
        x = random.randint(5, TEXTURE_SIZE-5)
        y = random.randint(5, TEXTURE_SIZE-5)
        pygame.draw.polygon(surface, (22, 99, 22),
                          [(x, y), (x-4, y+6), (x+4, y+6)])
    
    return surface

def create_river_texture():
    surface = pygame.Surface((TEXTURE_SIZE, TEXTURE_SIZE))
    surface.fill((0, 0, 255))  # Blue background
    
    # Add wave patterns
    for y in range(0, TEXTURE_SIZE, 4):
        for x in range(TEXTURE_SIZE):
            wave = math.sin(x/5 + y/3) * 2
            pygame.draw.line(surface, (100, 149, 255),
                           (x, y + wave), (x, y + wave + 1))
    
    return surface

def create_farmland_texture():
    surface = pygame.Surface((TEXTURE_SIZE, TEXTURE_SIZE))
    surface.fill((218, 165, 32))  # Golden background
    
    # Draw grid pattern for crops
    for i in range(0, TEXTURE_SIZE, 6):
        pygame.draw.line(surface, (198, 145, 12), (i, 0), (i, TEXTURE_SIZE))
        pygame.draw.line(surface, (198, 145, 12), (0, i), (TEXTURE_SIZE, i))
    
    return surface

def create_mountain_texture():
    surface = pygame.Surface((TEXTURE_SIZE, TEXTURE_SIZE))
    surface.fill((128, 128, 128))  # Gray background
    
    # Draw mountain peaks
    points = [(0, TEXTURE_SIZE), (10, 5), (20, 15), (TEXTURE_SIZE, TEXTURE_SIZE)]
    pygame.draw.polygon(surface, (100, 100, 100), points)
    
    return surface

def create_barren_texture():
    surface = pygame.Surface((TEXTURE_SIZE, TEXTURE_SIZE))
    surface.fill((139, 69, 19))  # Brown background
    
    # Add crack patterns
    for _ in range(4):
        x1 = random.randint(0, TEXTURE_SIZE)
        y1 = random.randint(0, TEXTURE_SIZE)
        x2 = x1 + random.randint(-10, 10)
        y2 = y1 + random.randint(-10, 10)
        pygame.draw.line(surface, (119, 49, 0), (x1, y1), (x2, y2), 1)
    
    return surface

def create_fertile_texture():
    surface = pygame.Surface((TEXTURE_SIZE, TEXTURE_SIZE))
    surface.fill((255, 255, 255))  # White background
    
    # Add mixed patterns of plains, forest and river
    for x in range(TEXTURE_SIZE):
        for y in range(TEXTURE_SIZE):
            if random.random() < 0.2:
                color = random.choice([
                    (144, 238, 144, 100),  # Light green
                    (34, 139, 34, 100),    # Dark green
                    (0, 0, 255, 100)       # Blue
                ])
                surface.set_at((x, y), color)
    
    return surface

def create_urban_texture():
    surface = pygame.Surface((TEXTURE_SIZE, TEXTURE_SIZE))
    surface.fill((192, 192, 192))  # Silver background
    
    # Draw building patterns
    for i in range(3):
        for j in range(3):
            x = i * 10
            y = j * 10
            width = 8
            height = random.randint(6, 8)
            pygame.draw.rect(surface, (128, 128, 128),
                           (x, y, width, height))
    
    return surface

def generate_all_textures():
    ensure_save_dir()
    
    # Generate and save all textures
    textures = {
        'building': create_building_texture(),
        'plain': create_plain_texture(),
        'forest': create_forest_texture(),
        'river': create_river_texture(),
        'farmland': create_farmland_texture(),
        'mountain': create_mountain_texture(),
        'barren': create_barren_texture(),
        'fertile': create_fertile_texture(),
        'urban': create_urban_texture()
    }
    
    for name, texture in textures.items():
        pygame.image.save(texture, f"{SAVE_DIR}/{name.lower()}.png")
        print(f"Generated {name} texture")

if __name__ == '__main__':
    generate_all_textures()
    print("All textures generated successfully!")
