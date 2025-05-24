import pygame
import random
import time
from enum import Enum
from typing import Optional, Dict, Any

# Initialize Pygame
pygame.init()

# Basic colors for UI
WHITE = (255, 255, 255)  # 玩家信息栏背景
BLACK = (0, 0, 0)    # 文字颜色
CREAM = (255, 253, 245)  # 游戏区域背景色
RED = (255, 0, 0)    # 无效放置提示

class Terrain(Enum):
    BUILDING = 0      # 建筑
    FIELD = 1         # 农田
    FOREST = 2        # 森林
    MOUNTAIN = 3      # 山地
    NEIGHBORHOOD = 4   # 社区
    PLAIN = 5         # 平原
    RIVER = 6         # 河流
    SWAMP = 7         # 沼泽

# Load terrain images
def load_terrain_images():
    images = {}
    for terrain in Terrain:
        try:
            # 将枚举名转换为文件名格式
            terrain_name = terrain.name.lower()
            image_path = f'Asset/TerrainsTypes/icon_{terrain_name}.png'
            img = pygame.image.load(image_path)
            
            # Scale image to fit block size while maintaining aspect ratio
            img_width = img.get_width()
            img_height = img.get_height()
            scale = min((BLOCK_SIZE - 1) / img_width, (BLOCK_SIZE - 1) / img_height)
            new_width = int(img_width * scale)
            new_height = int(img_height * scale)
            img = pygame.transform.scale(img, (new_width, new_height))
            
            # Create a surface with the block size
            surface = pygame.Surface((BLOCK_SIZE - 1, BLOCK_SIZE - 1), pygame.SRCALPHA)
            # Center the scaled image on the surface
            x = (BLOCK_SIZE - 1 - new_width) // 2
            y = (BLOCK_SIZE - 1 - new_height) // 2
            surface.blit(img, (x, y))
            
            images[terrain] = surface
        except pygame.error as e:
            print(f'Warning: Could not load image for {terrain_name}: {e}')
            images[terrain] = None
    return images

# Game Constants 
BLOCK_SIZE = 30
GRID_WIDTH = 26
GRID_HEIGHT = 26
PLAYER_BAR_HEIGHT = 50  # Height of the player score bar
TOOLBAR_HEIGHT = 100  # Height of the bottom toolbar
SCREEN_WIDTH = BLOCK_SIZE * (GRID_WIDTH + 8)  # Extra space for next piece and score
SCREEN_HEIGHT = PLAYER_BAR_HEIGHT + BLOCK_SIZE * GRID_HEIGHT + TOOLBAR_HEIGHT

# Tetromino shapes
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1], [1, 1]],  # O
    [[1, 1, 1], [0, 1, 0]],  # T
    [[1, 1, 1], [1, 0, 0]],  # L
    [[1, 1, 1], [0, 0, 1]],  # J
    [[1, 1, 0], [0, 1, 1]],  # S
    [[0, 1, 1], [1, 1, 0]]   # Z
]

# 移除 TERRAIN_COLORS 因为我们现在使用图标而不是颜色

class Tetris:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Tetris')
        self.clock = pygame.time.Clock()
        self.terrain_images = load_terrain_images()
        self.toolbar_pieces = self.generate_toolbar_pieces()
        self.selected_piece = None
        self.mouse_pos = (0, 0)
        # Tooltip related attributes
        self.hover_start_time = 0
        self.hover_piece: Optional[Dict[str, Any]] = None
        self.show_tooltip = False
        self.tooltip_font = pygame.font.Font(None, 24)
        self.reset_game()

    def reset_game(self):
        self.grid = [[{'terrain': None} for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = None
        self.preview_piece = None
        self.game_over = False
        self.score = 0
        self.level = 1
        self.lines_cleared = 0
        self.toolbar_pieces = self.generate_toolbar_pieces()
        self.selected_piece = None

    def generate_toolbar_pieces(self):
        # Generate 5 random pieces for the toolbar
        pieces = []
        for _ in range(5):
            shape_idx = random.randint(0, len(SHAPES) - 1)
            terrain = random.choice(list(Terrain))
            pieces.append({
                'shape': SHAPES[shape_idx],
                'terrain': terrain,
                'is_valid': True
            })
        return pieces

    def get_grid_pos_from_mouse(self, mouse_pos):
        # Convert mouse position to grid position
        x, y = mouse_pos
        grid_x = (x // BLOCK_SIZE)
        grid_y = ((y - PLAYER_BAR_HEIGHT) // BLOCK_SIZE)
        return grid_x, grid_y

    def is_mouse_in_grid(self, mouse_pos):
        # Check if mouse is in the game grid area
        x, y = mouse_pos
        return (0 <= x < GRID_WIDTH * BLOCK_SIZE and
                PLAYER_BAR_HEIGHT <= y < PLAYER_BAR_HEIGHT + GRID_HEIGHT * BLOCK_SIZE)

    def is_mouse_in_toolbar(self, mouse_pos):
        # Check if mouse is in the toolbar area
        x, y = mouse_pos
        toolbar_y = PLAYER_BAR_HEIGHT + GRID_HEIGHT * BLOCK_SIZE
        return (0 <= x < SCREEN_WIDTH and
                toolbar_y <= y < toolbar_y + TOOLBAR_HEIGHT)

    def new_piece(self):
        # Returns dictionary containing piece information
        shape_idx = random.randint(0, len(SHAPES) - 1)
        terrain = random.choice(list(Terrain))
        new_shape = SHAPES[shape_idx]
        return {
            'shape': new_shape,
            'terrain': terrain,
            'is_valid': True,
            'x': GRID_WIDTH // 2 - len(new_shape[0]) // 2,
            'y': 0
        }

    def valid_move(self, piece, x, y):
        for i, row in enumerate(piece['shape']):
            for j, cell in enumerate(row):
                if cell:
                    # Check if the piece would be outside the boundaries
                    if not (0 <= x + j < GRID_WIDTH and 0 <= y + i < GRID_HEIGHT):
                        return False
                    # Check if the position is already occupied
                    if self.grid[y + i][x + j]['terrain'] is not None:
                        return False
        return True

    def rotate_piece(self, piece):
        # Create new rotated shape
        new_shape = list(zip(*piece['shape'][::-1]))
        
        # If piece is selected and mouse is in grid, check if rotation is valid at current mouse position
        if self.selected_piece and self.is_mouse_in_grid(self.mouse_pos):
            grid_x, grid_y = self.get_grid_pos_from_mouse(self.mouse_pos)
            if self.valid_move({'shape': new_shape, 'x': grid_x, 'y': grid_y}, grid_x, grid_y):
                piece['shape'] = new_shape
        else:
            # For pieces in toolbar, always allow rotation
            piece['shape'] = new_shape

    def update_score(self):
        # Just increment score when piece is placed
        self.score += 10

    def lock_piece(self):
        if not self.check_valid_placement(self.preview_piece) or self.check_overlap(self.preview_piece):
            return
        
        for i, row in enumerate(self.preview_piece['shape']):
            for j, cell in enumerate(row):
                if cell:
                    if self.preview_piece['y'] + i >= 0:
                        self.grid[self.preview_piece['y'] + i][self.preview_piece['x'] + j] = {
                            'terrain': self.preview_piece['terrain']
                        }
        
        self.update_score()
        self.preview_piece = self.new_piece()
        if not self.check_valid_placement(self.preview_piece):
            self.game_over = True

    def check_valid_placement(self, piece):
        # 检查是否在游戏区域内，包括上边界
        for i, row in enumerate(piece['shape']):
            for j, cell in enumerate(row):
                if cell:
                    x, y = piece['x'] + j, piece['y'] + i
                    if not (0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT):
                        return False
        return True
    
    def check_overlap(self, piece):
        # 检查是否与已放置的方块重叠
        for i, row in enumerate(piece['shape']):
            for j, cell in enumerate(row):
                if cell:
                    x, y = piece['x'] + j, piece['y'] + i
                    if y >= 0 and self.grid[y][x]['terrain'] is not None:
                        return True
        return False

    def create_transparent_surface(self, terrain, alpha=255):
        # Create a transparent surface for preview
        if terrain in self.terrain_images and self.terrain_images[terrain] is not None:
            surface = self.terrain_images[terrain].copy()
            surface.set_alpha(alpha)
            return surface
        else:
            # Fallback to empty surface if image is not available
            surface = pygame.Surface((BLOCK_SIZE - 1, BLOCK_SIZE - 1), pygame.SRCALPHA)
            surface.fill((128, 128, 128, alpha))  # 使用灰色作为后备
            return surface

    def draw(self):
        # Clear screen
        self.screen.fill(CREAM)  # 使用奶白色背景
        
        # Draw player score bar
        pygame.draw.rect(self.screen, WHITE, [0, 0, SCREEN_WIDTH, PLAYER_BAR_HEIGHT])
        pygame.draw.line(self.screen, BLACK, (0, PLAYER_BAR_HEIGHT), (SCREEN_WIDTH, PLAYER_BAR_HEIGHT), 2)
        
        # Draw grid
        for i in range(GRID_HEIGHT):
            for j in range(GRID_WIDTH):
                pygame.draw.rect(self.screen, WHITE,
                               [j * BLOCK_SIZE, i * BLOCK_SIZE + PLAYER_BAR_HEIGHT, BLOCK_SIZE, BLOCK_SIZE], 1)
                if self.grid[i][j]['terrain'] is not None:
                    terrain = self.grid[i][j]['terrain']
                    if self.terrain_images[terrain] is not None:
                        self.screen.blit(self.terrain_images[terrain],
                                        (j * BLOCK_SIZE, i * BLOCK_SIZE + PLAYER_BAR_HEIGHT))
                    else:
                        pygame.draw.rect(self.screen, TERRAIN_COLORS[terrain],
                                       [j * BLOCK_SIZE, i * BLOCK_SIZE + PLAYER_BAR_HEIGHT, BLOCK_SIZE - 1, BLOCK_SIZE - 1])

        # Draw toolbar background
        toolbar_y = PLAYER_BAR_HEIGHT + GRID_HEIGHT * BLOCK_SIZE
        pygame.draw.rect(self.screen, WHITE, [0, toolbar_y, SCREEN_WIDTH, TOOLBAR_HEIGHT])
        pygame.draw.line(self.screen, BLACK, (0, toolbar_y), (SCREEN_WIDTH, toolbar_y), 2)

        # Draw toolbar pieces
        piece_spacing = SCREEN_WIDTH // (len(self.toolbar_pieces) + 1)
        for idx, piece in enumerate(self.toolbar_pieces):
            x = piece_spacing * (idx + 1) - (len(piece['shape'][0]) * BLOCK_SIZE) // 2
            y = toolbar_y + (TOOLBAR_HEIGHT - len(piece['shape']) * BLOCK_SIZE) // 2
            
            for i, row in enumerate(piece['shape']):
                for j, cell in enumerate(row):
                    if cell:
                        if self.terrain_images[piece['terrain']] is not None:
                            self.screen.blit(self.terrain_images[piece['terrain']],
                                            (x + j * BLOCK_SIZE, y + i * BLOCK_SIZE))
                        else:
                            pygame.draw.rect(self.screen, piece['color'],
                                           [x + j * BLOCK_SIZE, y + i * BLOCK_SIZE, BLOCK_SIZE - 1, BLOCK_SIZE - 1])

        # Draw selected piece following mouse if exists
        if self.selected_piece and self.is_mouse_in_grid(self.mouse_pos):
            grid_x, grid_y = self.get_grid_pos_from_mouse(self.mouse_pos)
            preview = {
                **self.selected_piece,
                'x': grid_x,
                'y': grid_y
            }
            is_valid = self.check_valid_placement(preview) and not self.check_overlap(preview)
            if is_valid:
                preview_surface = self.create_transparent_surface(self.selected_piece['terrain'], alpha=160)
            else:
                # For invalid placement, use red rectangle
                preview_surface = pygame.Surface((BLOCK_SIZE - 1, BLOCK_SIZE - 1))
                preview_surface.fill(RED)
                preview_surface.set_alpha(160)
            
            for i, row in enumerate(self.selected_piece['shape']):
                for j, cell in enumerate(row):
                    if cell:
                        self.screen.blit(
                            preview_surface,
                            ((grid_x + j) * BLOCK_SIZE,
                             (grid_y + i) * BLOCK_SIZE + PLAYER_BAR_HEIGHT)
                        )

        # Draw score and level
        font = pygame.font.Font(None, 36)
        score_text = font.render(f'Score: {self.score}', True, BLACK)
        level_text = font.render(f'Level: {self.level}', True, BLACK)
        self.screen.blit(score_text, (GRID_WIDTH * BLOCK_SIZE + 10, 20))
        self.screen.blit(level_text, (GRID_WIDTH * BLOCK_SIZE + 10, 60))

        if self.game_over:
            game_over_text = font.render('GAME OVER', True, RED)
            self.screen.blit(game_over_text, (GRID_WIDTH * BLOCK_SIZE + 10, 100))
            restart_text = font.render('Press R to restart', True, WHITE)
            self.screen.blit(restart_text, (GRID_WIDTH * BLOCK_SIZE + 10, 140))

        pygame.display.flip()

    def render_tooltip(self, terrain, pos):
        # Create tooltip text with terrain description
        descriptions = {
            Terrain.BUILDING: "建筑",
            Terrain.FIELD: "农田",
            Terrain.FOREST: "森林",
            Terrain.MOUNTAIN: "山地",
            Terrain.NEIGHBORHOOD: "社区",
            Terrain.PLAIN: "平原",
            Terrain.RIVER: "河流",
            Terrain.SWAMP: "沼泽"
        }
        description = descriptions.get(terrain, terrain.name)
        text = f"地形: {description}"
        text_surface = self.tooltip_font.render(text, True, (0, 0, 0))
        text_rect = text_surface.get_rect()
        
        # Position tooltip to the right of the cursor
        x, y = pos
        x += 20  # Offset from cursor
        
        # Create background rectangle
        padding = 5
        bg_rect = pygame.Rect(x, y, text_rect.width + padding * 2, text_rect.height + padding * 2)
        
        # Keep tooltip on screen
        if bg_rect.right > SCREEN_WIDTH:
            x = SCREEN_WIDTH - text_rect.width - padding * 2
        if bg_rect.bottom > SCREEN_HEIGHT:
            y = SCREEN_HEIGHT - text_rect.height - padding * 2
        
        # Draw tooltip
        pygame.draw.rect(self.screen, CREAM, (x, y, text_rect.width + padding * 2, text_rect.height + padding * 2))
        pygame.draw.rect(self.screen, BLACK, (x, y, text_rect.width + padding * 2, text_rect.height + padding * 2), 1)
        self.screen.blit(text_surface, (x + padding, y + padding))

    def get_hovered_piece(self, mouse_pos):
        x, y = mouse_pos
        
        # Check toolbar pieces
        if self.is_mouse_in_toolbar(mouse_pos):
            toolbar_y = PLAYER_BAR_HEIGHT + GRID_HEIGHT * BLOCK_SIZE
            for i, piece in enumerate(self.toolbar_pieces):
                piece_x = i * (BLOCK_SIZE * 4)
                piece_y = toolbar_y
                piece_width = len(piece['shape'][0]) * BLOCK_SIZE
                piece_height = len(piece['shape']) * BLOCK_SIZE
                
                if piece_x <= x < piece_x + piece_width and piece_y <= y < piece_y + piece_height:
                    return piece
        
        # Check grid pieces
        if self.is_mouse_in_grid(mouse_pos):
            grid_x, grid_y = self.get_grid_pos_from_mouse(mouse_pos)
            if 0 <= grid_x < GRID_WIDTH and 0 <= grid_y < GRID_HEIGHT:
                cell = self.grid[grid_y][grid_x]
                if cell['terrain'] is not None:
                    return cell
        
        return None

    def handle_toolbar_click(self):
        piece_spacing = SCREEN_WIDTH // (len(self.toolbar_pieces) + 1)
        # Calculate the center positions of each piece
        for idx, piece in enumerate(self.toolbar_pieces):
            piece_center_x = piece_spacing * (idx + 1)
            piece_width = len(piece['shape'][0]) * BLOCK_SIZE
            piece_x = piece_center_x - piece_width // 2
            # Check if click is within piece bounds
            if piece_x <= self.mouse_pos[0] < piece_x + piece_width:
                self.selected_piece = {
                    **self.toolbar_pieces[idx],
                    'toolbar_idx': idx  # Store the index for later
                }
                break

    def handle_grid_click(self):
        grid_x, grid_y = self.get_grid_pos_from_mouse(self.mouse_pos)
        preview = {
            'shape': self.selected_piece['shape'],
            'terrain': self.selected_piece['terrain'],
            'x': grid_x,
            'y': grid_y
        }
        if self.check_valid_placement(preview) and not self.check_overlap(preview):
            self.preview_piece = preview
            self.lock_piece()
            # Replace the used piece with a new random one
            toolbar_idx = self.selected_piece['toolbar_idx']
            self.toolbar_pieces[toolbar_idx] = self.new_piece()
            self.selected_piece = None

    def run(self):
        running = True
        while running:
            self.clock.tick(60)
            current_time = time.time()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEMOTION:
                    new_pos = event.pos
                    if new_pos != self.mouse_pos:
                        self.mouse_pos = new_pos
                        # Check for hovered piece
                        current_hover_piece = self.get_hovered_piece(new_pos)
                        
                        if current_hover_piece != self.hover_piece:
                            self.hover_piece = current_hover_piece
                            self.hover_start_time = current_time
                            self.show_tooltip = False
                elif event.type == pygame.MOUSEBUTTONDOWN and not self.game_over:
                    if event.button == 1:  # Left click
                        if self.is_mouse_in_toolbar(self.mouse_pos):
                            # Try to select a piece from toolbar
                            self.handle_toolbar_click()
                        elif self.selected_piece and self.is_mouse_in_grid(self.mouse_pos):
                            # Try to place the selected piece
                            self.handle_grid_click()
                    elif event.button == 3:  # Right click
                        if self.selected_piece:
                            self.rotate_piece(self.selected_piece)

            # Update tooltip visibility
            if self.hover_piece and not self.show_tooltip:
                if current_time - self.hover_start_time >= 2.0:  # 2 seconds hover time
                    self.show_tooltip = True

            # Draw everything
            self.draw()
            
            # Draw tooltip if needed (only for BUILDING terrain)
            if (self.show_tooltip and self.hover_piece and 
                'terrain' in self.hover_piece and 
                self.hover_piece['terrain'] == Terrain.BUILDING):
                self.render_tooltip(self.hover_piece['terrain'], self.mouse_pos)

            pygame.display.flip()

if __name__ == '__main__':
    game = Tetris()
    game.run()
