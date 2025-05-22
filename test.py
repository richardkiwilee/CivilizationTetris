import pygame
import random
import time
from enum import Enum

# Initialize Pygame
pygame.init()

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
SCREEN_WIDTH = BLOCK_SIZE * (GRID_WIDTH + 8)  # Extra space for next piece and score
SCREEN_HEIGHT = PLAYER_BAR_HEIGHT + BLOCK_SIZE * GRID_HEIGHT

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
        self.reset_game()

    def reset_game(self):
        self.grid = [[{'terrain': None, 'color': None} for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = None
        self.preview_piece = self.new_piece()
        self.game_over = False
        self.score = 0
        self.level = 1
        self.lines_cleared = 0

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
        if self.valid_move({'shape': new_shape, 'x': piece['x'], 'y': piece['y']},
                          piece['x'], piece['y']):
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

    def create_transparent_surface(self, color, alpha=128):
        surface = pygame.Surface((BLOCK_SIZE - 1, BLOCK_SIZE - 1))
        surface.fill(color)
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
                    pygame.draw.rect(self.screen, self.grid[i][j]['color'],
                                   [j * BLOCK_SIZE, i * BLOCK_SIZE + PLAYER_BAR_HEIGHT, BLOCK_SIZE - 1, BLOCK_SIZE - 1])

        # Draw preview piece
        if self.preview_piece:
            is_valid = self.check_valid_placement(self.preview_piece)
            has_overlap = self.check_overlap(self.preview_piece)
            preview_color = RED if has_overlap else self.preview_piece['color']
            preview_surface = self.create_transparent_surface(preview_color, alpha=160)
            
            for i, row in enumerate(self.preview_piece['shape']):
                for j, cell in enumerate(row):
                    if cell:
                        self.screen.blit(
                            preview_surface,
                            ((self.preview_piece['x'] + j) * BLOCK_SIZE,
                             (self.preview_piece['y'] + i) * BLOCK_SIZE + PLAYER_BAR_HEIGHT)
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
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                # Handle single-press keys (WASD and R)
                if event.type == pygame.KEYDOWN and not self.game_over:
                    if event.key == pygame.K_a:
                        if self.check_valid_placement({**self.preview_piece, 'x': self.preview_piece['x'] - 1}):
                            self.preview_piece['x'] -= 1
                    elif event.key == pygame.K_d:
                        if self.check_valid_placement({**self.preview_piece, 'x': self.preview_piece['x'] + 1}):
                            self.preview_piece['x'] += 1
                    elif event.key == pygame.K_s:
                        if self.check_valid_placement({**self.preview_piece, 'y': self.preview_piece['y'] + 1}):
                            self.preview_piece['y'] += 1
                    elif event.key == pygame.K_w:
                        if self.check_valid_placement({**self.preview_piece, 'y': self.preview_piece['y'] - 1}):
                            self.preview_piece['y'] -= 1
                    elif event.key == pygame.K_r:
                        self.rotate_piece(self.preview_piece)
                    elif event.key == pygame.K_SPACE:
                        self.lock_piece()
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_r and self.game_over:
                    self.reset_game()

            # Handle continuous movement with arrow keys
            if not self.game_over:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_LEFT]:
                    if self.check_valid_placement({**self.preview_piece, 'x': self.preview_piece['x'] - 1}):
                        self.preview_piece['x'] -= 1
                if keys[pygame.K_RIGHT]:
                    if self.check_valid_placement({**self.preview_piece, 'x': self.preview_piece['x'] + 1}):
                        self.preview_piece['x'] += 1
                if keys[pygame.K_DOWN]:
                    if self.check_valid_placement({**self.preview_piece, 'y': self.preview_piece['y'] + 1}):
                        self.preview_piece['y'] += 1

            self.draw()

if __name__ == '__main__':
    game = Tetris()
    game.run()
