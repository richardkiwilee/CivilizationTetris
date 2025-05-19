import pygame
import sys
import time
from Tetris.game.terrain import *
from Tetris.game.manager import Manager
from Tetris.game.desktop import Desktop

class TetrisUI:
    # Define colors for different terrains
    TERRAIN_COLORS = {
        Terrain.Building: (128, 128, 128),  # Gray
        Terrain.Plain: (150, 200, 50),      # Light green
        Terrain.Forest: (34, 139, 34),      # Forest green
        Terrain.River: (0, 191, 255),       # Deep sky blue
        Terrain.Farmland: (218, 165, 32),   # Golden rod
        Terrain.Mountain: (139, 137, 137),  # Gray
        Terrain.Barren: (210, 180, 140),    # Tan
        Terrain.Fertile: (124, 252, 0),     # Lawn green
        Terrain.Urban: (169, 169, 169),     # Dark gray
    }
    
    def __init__(self, manager):
        pygame.init()
        self.manager = manager
        self.cell_size = 50
        self.grid_size = 12
        self.margin = 2
        
        # Calculate window size based on grid
        window_size = (self.grid_size * (self.cell_size + self.margin), 
                      self.grid_size * (self.cell_size + self.margin))
        self.screen = pygame.display.set_mode(window_size)
        pygame.display.set_caption('Civilization Tetris')
        
        # Colors
        self.background_color = (30, 30, 30)
        self.grid_color = (50, 50, 50)
        self.invalid_color = (255, 0, 0)  # Red for invalid positions
        self.empty_color = (20, 20, 20)
        
        # Control variables
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Key state tracking
        self.key_states = {
            pygame.K_w: False,
            pygame.K_s: False,
            pygame.K_a: False,
            pygame.K_d: False,
            pygame.K_r: False,
            pygame.K_SPACE: False
        }
        self.key_repeat_delay = 150  # ms before key repeat
        self.key_repeat_interval = 50  # ms between repeats
        self.last_key_time = {k: 0 for k in self.key_states}

    def draw_grid(self):
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                x = col * (self.cell_size + self.margin)
                y = row * (self.cell_size + self.margin)
                cell = self.manager.Desktop.GetCell(row, col)
                
                # Default color for empty cells
                color = self.empty_color
                
                # If cell has terrain, use terrain color
                if cell and cell.terrain:
                    color = self.TERRAIN_COLORS.get(cell.terrain, self.empty_color)
                
                pygame.draw.rect(self.screen, color, 
                               (x, y, self.cell_size, self.cell_size))

    def draw_current_puzzle(self, x, y, puzzle, rotate):
        if not puzzle:
            return
            
        # Get all cells that would be occupied by the puzzle
        puzzle_cells = self.manager.GetPuzzleCells(x, y, puzzle, rotate)
        
        for px, py in puzzle_cells:
            if 0 <= px < self.grid_size and 0 <= py < self.grid_size:
                screen_x = py * (self.cell_size + self.margin)
                screen_y = px * (self.cell_size + self.margin)
                
                # Check if position is valid
                is_valid = self.manager.Placeable(None, x, y, puzzle, rotate)
                color = self.invalid_color if not is_valid else self.TERRAIN_COLORS.get(puzzle.terrain, self.empty_color)
                
                pygame.draw.rect(self.screen, color,
                               (screen_x, screen_y, self.cell_size, self.cell_size))

    def handle_keyboard_input(self, current_x, current_y, current_puzzle, current_rotate):
        new_x, new_y, new_rotate = current_x, current_y, current_rotate
        action = None
        current_time = pygame.time.get_ticks()

        # Process events to update key states
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key in self.key_states:
                    self.key_states[event.key] = True
                    self.last_key_time[event.key] = current_time
            elif event.type == pygame.KEYUP:
                if event.key in self.key_states:
                    self.key_states[event.key] = False

        # Handle key states with repeat delay
        keys = pygame.key.get_pressed()
        for key in self.key_states:
            if keys[key]:
                time_since_last = current_time - self.last_key_time[key]
                if time_since_last >= self.key_repeat_delay:
                    # Reset timer for repeat interval
                    self.last_key_time[key] = current_time - (self.key_repeat_delay - self.key_repeat_interval)
                    
                    # Handle movement
                    if key == pygame.K_w:
                        new_x -= 1
                    elif key == pygame.K_s:
                        new_x += 1
                    elif key == pygame.K_a:
                        new_y -= 1
                    elif key == pygame.K_d:
                        new_y += 1
                    elif key == pygame.K_r:
                        new_rotate = (new_rotate + 1) % 4
                    elif key == pygame.K_SPACE:
                        action = 'place'
            
        # Validate new position
        if not (0 <= new_x < self.grid_size and 0 <= new_y < self.grid_size):
            new_x, new_y = current_x, current_y
            
        return new_x, new_y, new_rotate, action

    def run(self, current_x, current_y, current_puzzle, current_rotate):
        # Handle events first
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                sys.exit()
        
        # Handle keyboard input
        new_x, new_y, new_rotate, action = self.handle_keyboard_input(
            current_x, current_y, current_puzzle, current_rotate)
        
        # Clear the screen with background color
        self.screen.fill(self.background_color)
        
        # Draw the base grid
        self.draw_grid()
        
        # Draw the current puzzle if it exists
        if current_puzzle:
            self.draw_current_puzzle(new_x, new_y, current_puzzle, new_rotate)
        
        # Update the display
        pygame.display.flip()
        
        # Cap the frame rate
        self.clock.tick(60)
        
        # Return the new state
        return self.running, new_x, new_y, new_rotate, action

def create_test_puzzle():
    # Create a test puzzle with an L shape
    puzzle = Puzzle(PuzzleType.Terrain, Shape.L, Terrain.Plain)
    puzzle.cells = {(0, 0), (1, 0), (2, 0), (2, 1)}  # L shape
    return puzzle

def main():
    # Initialize the game manager and desktop
    manager = Manager()
    manager.Desktop = Desktop(12, 12)
    
    # Initialize the UI
    ui = TetrisUI(manager)
    
    # Initial position and puzzle
    current_x, current_y = 0, 0
    current_rotate = 0
    current_puzzle = create_test_puzzle()
    
    # Main game loop
    while True:
        # Run one frame of the UI
        running, new_x, new_y, new_rotate, action = ui.run(
            current_x, current_y, current_puzzle, current_rotate)
        
        if not running:
            break
        
        # Update position
        current_x, current_y = new_x, new_y
        current_rotate = new_rotate
        
        # Handle placement action
        if action == 'place':
            if manager.Placeable(None, current_x, current_y, current_puzzle, current_rotate):
                manager.Place(None, current_x, current_y, current_puzzle, current_rotate)
                # Create a new puzzle after placement
                current_puzzle = create_test_puzzle()
                current_x, current_y = 0, 0
                current_rotate = 0

if __name__ == '__main__':
    main()
