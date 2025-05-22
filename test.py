import pygame
import random
import time
from enum import Enum

# Initialize Pygame
pygame.init()

# Load terrain images
def load_terrain_images():
    images = {}
    for terrain in Terrain:
        try:
            image_path = f'Asset/terrain/{terrain.name.lower()}.png'
            img = pygame.image.load(image_path)
            # Scale image to block size
            img = pygame.transform.scale(img, (BLOCK_SIZE - 1, BLOCK_SIZE - 1))
            images[terrain] = img
        except pygame.error:
            print(f'Warning: Could not load image for {terrain.name}')
            images[terrain] = None
    return images

class Terrain(Enum):
    Building = 0    # 建筑 黑色
    Plain = 1       # 平原 浅绿色
    Forest = 2      # 森林 深绿色
    River = 3       # 河流 蓝色
    Farmland = 4    # 农田 金黄色
    Mountain = 5    # 山地 灰色
    Barren = 6      # 贫瘠 浅褐色
    Fertile = 7     # 肥沃, 同时视为平原、森林、河流  白色
    Urban = 8       # 城市 深棕色


# Colors
BLACK = (0, 0, 0)  # Building
WHITE = (255, 255, 255)
CREAM = (255, 253, 245)  # 奶白色背景
LIGHT_GREEN = (144, 238, 144)  # Plain
DARK_GREEN = (34, 139, 34)  # Forest
BLUE = (0, 0, 255)  # River
GOLDEN = (218, 165, 32)  # Farmland
GRAY = (128, 128, 128)  # Mountain
BROWN = (139, 69, 19)  # Barren
PURPLE = (128, 0, 128)  # Fertile
SILVER = (192, 192, 192)  # Urban
RED = (255, 0, 0)  # Invalid placement

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

TERRAIN_COLORS = {
    Terrain.Building: BLACK,
    Terrain.Plain: LIGHT_GREEN,
    Terrain.Forest: DARK_GREEN,
    Terrain.River: BLUE,
    Terrain.Farmland: GOLDEN,
    Terrain.Mountain: GRAY,
    Terrain.Barren: BROWN,
    Terrain.Fertile: PURPLE,
    Terrain.Urban: SILVER
}

class Tetris:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Tetris')
        self.clock = pygame.time.Clock()
        self.terrain_images = load_terrain_images()
        self.toolbar_pieces = self.generate_toolbar_pieces()
        self.selected_piece = None
        self.mouse_pos = (0, 0)
        self.reset_game()

    def reset_game(self):
        self.grid = [[{'terrain': None, 'color': None} for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
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
                'color': TERRAIN_COLORS[terrain],
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
            'color': TERRAIN_COLORS[terrain],
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
                            'terrain': self.preview_piece['terrain'],
                            'color': self.preview_piece['color']
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

    def create_transparent_surface(self, terrain, alpha=128):
        if self.terrain_images[terrain] is not None:
            # Create a copy of the image and set its alpha
            surface = self.terrain_images[terrain].copy()
            surface.set_alpha(alpha)
            return surface
        else:
            # Fallback to colored rectangle if image is not available
            surface = pygame.Surface((BLOCK_SIZE - 1, BLOCK_SIZE - 1))
            surface.fill(TERRAIN_COLORS[terrain])
            surface.set_alpha(alpha)
            return surface

    def draw(self):
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

    def run(self):
        while True:
            self.clock.tick(30)
            self.mouse_pos = pygame.mouse.get_pos()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return

                # Handle mouse clicks
                elif event.type == pygame.MOUSEBUTTONDOWN and not self.game_over:
                    if event.button == 1:  # Left click
                        if self.is_mouse_in_toolbar(self.mouse_pos):
                            # Try to select a piece from toolbar
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
                        elif self.is_mouse_in_grid(self.mouse_pos) and self.selected_piece:
                            # Try to place the selected piece
                            grid_x, grid_y = self.get_grid_pos_from_mouse(self.mouse_pos)
                            preview = {
                                'shape': self.selected_piece['shape'],
                                'terrain': self.selected_piece['terrain'],
                                'color': self.selected_piece['color'],
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
                    
                    elif event.button == 3:  # Right click
                        # Cancel selection
                        self.selected_piece = None
                
                # Handle mouse wheel for rotation of selected piece
                elif event.type == pygame.MOUSEWHEEL and not self.game_over and self.selected_piece:
                    if event.y != 0:  # y > 0 is scroll up, y < 0 is scroll down
                        self.rotate_piece(self.selected_piece)

            self.draw()

if __name__ == '__main__':
    game = Tetris()
    game.run()
