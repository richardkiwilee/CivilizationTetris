import pygame
import random
import time

# Initialize Pygame
pygame.init()

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
CYAN = (0, 255, 255)
YELLOW = (255, 255, 0)
MAGENTA = (255, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)

# Game Constants
BLOCK_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20
SCREEN_WIDTH = BLOCK_SIZE * (GRID_WIDTH + 8)  # Extra space for next piece and score
SCREEN_HEIGHT = BLOCK_SIZE * GRID_HEIGHT

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

COLORS = [CYAN, YELLOW, MAGENTA, ORANGE, BLUE, GREEN, RED]

class Tetris:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption('Tetris')
        self.clock = pygame.time.Clock()
        self.reset_game()

    def reset_game(self):
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = self.new_piece()
        self.game_over = False
        self.score = 0
        self.level = 1
        self.lines_cleared = 0


    def new_piece(self):
        # Returns dictionary containing piece information
        shape_idx = random.randint(0, len(SHAPES) - 1)
        return {
            'shape': SHAPES[shape_idx],
            'color': COLORS[shape_idx],
            'x': GRID_WIDTH // 2 - len(SHAPES[shape_idx][0]) // 2,
            'y': 0
        }

    def valid_move(self, piece, x, y):
        for i, row in enumerate(piece['shape']):
            for j, cell in enumerate(row):
                if cell:
                    if not (0 <= x + j < GRID_WIDTH and
                           y + i < GRID_HEIGHT and
                           (y + i < 0 or self.grid[y + i][x + j] == 0)):
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

    def lock_piece(self, piece):
        for i, row in enumerate(piece['shape']):
            for j, cell in enumerate(row):
                if cell:
                    if piece['y'] + i >= 0:
                        self.grid[piece['y'] + i][piece['x'] + j] = piece['color']
        self.update_score()
        self.current_piece = self.new_piece()
        if not self.valid_move(self.current_piece, self.current_piece['x'], self.current_piece['y']):
            self.game_over = True

    def draw(self):
        self.screen.fill(BLACK)
        
        # Draw grid
        for i in range(GRID_HEIGHT):
            for j in range(GRID_WIDTH):
                pygame.draw.rect(self.screen, WHITE,
                               [j * BLOCK_SIZE, i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE], 1)
                if self.grid[i][j]:
                    pygame.draw.rect(self.screen, self.grid[i][j],
                                   [j * BLOCK_SIZE, i * BLOCK_SIZE, BLOCK_SIZE - 1, BLOCK_SIZE - 1])

        # Draw current piece
        if self.current_piece:
            for i, row in enumerate(self.current_piece['shape']):
                for j, cell in enumerate(row):
                    if cell:
                        pygame.draw.rect(
                            self.screen,
                            self.current_piece['color'],
                            [(self.current_piece['x'] + j) * BLOCK_SIZE,
                             (self.current_piece['y'] + i) * BLOCK_SIZE,
                             BLOCK_SIZE - 1, BLOCK_SIZE - 1]
                        )

        # Draw score and level
        font = pygame.font.Font(None, 36)
        score_text = font.render(f'Score: {self.score}', True, WHITE)
        level_text = font.render(f'Level: {self.level}', True, WHITE)
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
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                
                if event.type == pygame.KEYDOWN:
                    if not self.game_over:
                        if event.key == pygame.K_a:
                            if self.valid_move(self.current_piece, self.current_piece['x'] - 1, self.current_piece['y']):
                                self.current_piece['x'] -= 1
                        elif event.key == pygame.K_d:
                            if self.valid_move(self.current_piece, self.current_piece['x'] + 1, self.current_piece['y']):
                                self.current_piece['x'] += 1
                        elif event.key == pygame.K_s:
                            if self.valid_move(self.current_piece, self.current_piece['x'], self.current_piece['y'] + 1):
                                self.current_piece['y'] += 1
                        elif event.key == pygame.K_w:
                            if self.valid_move(self.current_piece, self.current_piece['x'], self.current_piece['y'] - 1):
                                self.current_piece['y'] -= 1
                        elif event.key == pygame.K_r:
                            self.rotate_piece(self.current_piece)
                        elif event.key == pygame.K_SPACE:
                            self.lock_piece(self.current_piece)
                    
                    if event.key == pygame.K_r and self.game_over:
                        self.reset_game()

            self.draw()
            self.clock.tick(60)

if __name__ == '__main__':
    game = Tetris()
    game.run()