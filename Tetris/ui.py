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
        
        # Key repeat settings
        pygame.key.set_repeat(200, 50)  # Initial delay 200ms, repeat every 50ms

    def draw_grid(self):
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                # 计算屏幕坐标
                screen_x = col * (self.cell_size + self.margin)
                screen_y = row * (self.cell_size + self.margin)
                
                # 获取格子内容
                cell = self.manager.Desktop.GetCell(row, col)
                
                # 默认颜色
                color = self.empty_color
                
                # 如果有地形，使用地形颜色
                if cell and cell.terrain:
                    color = self.TERRAIN_COLORS.get(cell.terrain, self.empty_color)
                
                # 绘制格子
                pygame.draw.rect(self.screen, color, 
                               (screen_x, screen_y, self.cell_size, self.cell_size))
                
                # 绘制格子边框
                pygame.draw.rect(self.screen, self.grid_color,
                               (screen_x, screen_y, self.cell_size, self.cell_size), 1)

    def draw_current_puzzle(self, x, y, puzzle, rotate):
        if not puzzle:
            return
            
        # 获取拼图占用的所有格子
        puzzle_cells = self.manager.GetPuzzleCells(x, y, puzzle, rotate)
        
        # 检查整个拼图的位置是否有效
        is_valid = self.manager.Placeable(None, x, y, puzzle, rotate)
        
        # 绘制拼图的每个格子
        for px, py in puzzle_cells:
            if 0 <= px < self.grid_size and 0 <= py < self.grid_size:
                # 计算屏幕坐标
                screen_x = py * (self.cell_size + self.margin)
                screen_y = px * (self.cell_size + self.margin)
                
                # 设置颜色
                color = self.invalid_color if not is_valid else self.TERRAIN_COLORS.get(puzzle.terrain, self.empty_color)
                
                # 绘制格子
                pygame.draw.rect(self.screen, color,
                               (screen_x, screen_y, self.cell_size, self.cell_size))
                
                # 绘制格子边框
                pygame.draw.rect(self.screen, (255, 255, 255),
                               (screen_x, screen_y, self.cell_size, self.cell_size), 1)

    def handle_keyboard_input(self, current_x, current_y, current_puzzle, current_rotate):
        new_x, new_y, new_rotate = current_x, current_y, current_rotate
        action = None

        # 处理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                # 处理按键移动
                if event.key == pygame.K_w:
                    new_x -= 1
                elif event.key == pygame.K_s:
                    new_x += 1
                elif event.key == pygame.K_a:
                    new_y -= 1
                elif event.key == pygame.K_d:
                    new_y += 1
                elif event.key == pygame.K_r:
                    new_rotate = (new_rotate + 1) % 4
                elif event.key == pygame.K_SPACE:
                    action = 'place'

                # 验证新位置和旋转是否有效
                if current_puzzle:
                    # 首先检查是否在网格范围内
                    if not (0 <= new_x < self.grid_size and 0 <= new_y < self.grid_size):
                        new_x, new_y = current_x, current_y
                    else:
                        # 检查新位置是否可放置
                        if not self.manager.Placeable(None, new_x, new_y, current_puzzle, new_rotate):
                            # 如果是旋转导致的无效位置，恢复旋转
                            if event.key == pygame.K_r:
                                new_rotate = current_rotate
                            # 如果是移动导致的无效位置，恢复位置
                            else:
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
