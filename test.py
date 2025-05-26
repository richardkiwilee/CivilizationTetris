import pygame
import random
import time
from enum import Enum
from typing import Optional, Dict, Any

# 初始化pygame字体系统
pygame.font.init()

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
            image_path = f'Asset/Icons/TerrainsTypes/icon_{terrain_name}.png'
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
FILL_BLOCK = 7 # 定义 FILL_BLOCK * FILL_BLOCK是一个正方形的小分组
BLOCK_COUNT = 4 # 定义每行和每列有多少个 FILL_BLOCK
GRID_WIDTH = BLOCK_COUNT * FILL_BLOCK
GRID_HEIGHT = BLOCK_COUNT * FILL_BLOCK
TOOLBAR_HEIGHT = 100  # Height of the bottom toolbar
TOP_MARGIN = 50  # Height of top margin
# UI Constants
PLAYER_SLOTS = 4  # Number of player slots
PLAYER_SLOT_HEIGHT = 180  # Height of each player slot (increased to accommodate resources and effects)
PLAYER_SLOT_WIDTH = 200  # Width of player slots area
RESOURCE_ICON_SIZE = 20  # Size of resource icons
EFFECT_SLOT_SIZE = 40  # Size of special effect slots
BUTTON_HEIGHT = 40
BUTTON_WIDTH = 120
BUTTON_MARGIN = 10

# Resource layout
RESOURCE_TYPES = [
    ('food', 'Asset/Icons/ResourcesIcons/icon_food.png'),
    ('wood', 'Asset/Icons/ResourcesIcons/icon_wood.png'),
    ('stone', 'Asset/Icons/ResourcesIcons/icon_stone.png'),
    ('gold', 'Asset/Icons/ResourcesIcons/icon_gold.png'),
    ('faith', 'Asset/Icons/ResourcesIcons/icon_faith.png'),
    ('citizen', 'Asset/Icons/ResourcesIcons/icon_citizen.png'),
    ('order', 'Asset/Icons/ResourcesIcons/icon_decree.png')
]

# Screen dimensions
SCREEN_WIDTH = BLOCK_SIZE * GRID_WIDTH + PLAYER_SLOT_WIDTH  # Main grid + player slots
SCREEN_HEIGHT = TOP_MARGIN + BLOCK_SIZE * GRID_HEIGHT + TOOLBAR_HEIGHT

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
        self.resource_images = self.load_resource_images()
        self.toolbar_pieces = self.generate_toolbar_pieces()
        self.selected_piece = None
        self.mouse_pos = (0, 0)
        # Tooltip related attributes
        self.hover_start_time = 0
        self.hover_piece: Optional[Dict[str, Any]] = None
        self.show_tooltip = False
        # 使用系统默认字体以支持中文
        self.tooltip_font = pygame.font.SysFont('simhei', 24)  # 使用黑体
        # Button related attributes
        self.button_font = pygame.font.SysFont('simhei', 24)  # 使用相同的中文字体
        button_x = BLOCK_SIZE * GRID_WIDTH + (PLAYER_SLOT_WIDTH - BUTTON_WIDTH) // 2  # 放在玩家槽下方中央
        self.buttons = [
            {'text': 'End Turn', 'rect': pygame.Rect(button_x, SCREEN_HEIGHT - TOOLBAR_HEIGHT + 20, BUTTON_WIDTH, BUTTON_HEIGHT)},
            {'text': 'Settings', 'rect': pygame.Rect(button_x, SCREEN_HEIGHT - TOOLBAR_HEIGHT + 70, BUTTON_WIDTH, BUTTON_HEIGHT)}
        ]
        self.reset_game()

    def load_resource_images(self):
        images = {}
        for resource_name, resource_path in RESOURCE_TYPES:
            try:
                img = pygame.image.load(resource_path)
                img = pygame.transform.scale(img, (RESOURCE_ICON_SIZE, RESOURCE_ICON_SIZE))
                images[resource_name] = img
            except pygame.error as e:
                print(f'Warning: Could not load image for {resource_name}: {e}')
                images[resource_name] = None
        return images

    def draw_player_slot(self, slot_index, player_name='Player 1', resources=None):
        if resources is None:
            resources = {'food': 0, 'wood': 0, 'stone': 0, 'gold': 0, 'faith': 0, 'citizen': 0, 'order': 0}

        x = BLOCK_SIZE * GRID_WIDTH
        y = TOP_MARGIN + slot_index * PLAYER_SLOT_HEIGHT
        slot_rect = pygame.Rect(x, y, PLAYER_SLOT_WIDTH, PLAYER_SLOT_HEIGHT)
        
        # Draw slot background
        pygame.draw.rect(self.screen, WHITE, slot_rect)
        pygame.draw.rect(self.screen, BLACK, slot_rect, 1)

        # Draw player name
        name_font = pygame.font.Font(None, 24)
        name_text = name_font.render(player_name, True, BLACK)
        self.screen.blit(name_text, (x + 5, y + 5))

        # Draw resources
        resource_font = pygame.font.Font(None, 20)
        left_resources = ['food', 'wood', 'stone']
        right_resources = ['gold', 'faith', 'citizen', 'order']
        
        # Left column resources
        for i, resource in enumerate(left_resources):
            icon_y = y + 30 + i * (RESOURCE_ICON_SIZE + 5)
            if self.resource_images.get(resource):
                self.screen.blit(self.resource_images[resource], (x + 5, icon_y))
            value_text = resource_font.render(str(resources[resource]), True, BLACK)
            self.screen.blit(value_text, (x + RESOURCE_ICON_SIZE + 10, icon_y + 2))

        # Right column resources
        for i, resource in enumerate(right_resources):
            icon_y = y + 30 + i * (RESOURCE_ICON_SIZE + 5)
            if self.resource_images.get(resource):
                self.screen.blit(self.resource_images[resource], (x + PLAYER_SLOT_WIDTH//2, icon_y))
            value_text = resource_font.render(str(resources[resource]), True, BLACK)
            self.screen.blit(value_text, (x + PLAYER_SLOT_WIDTH//2 + RESOURCE_ICON_SIZE + 5, icon_y + 2))

        # Draw special effects slots
        effects_y = y + PLAYER_SLOT_HEIGHT - EFFECT_SLOT_SIZE - 5
        for i in range(4):
            effect_x = x + 5 + i * (EFFECT_SLOT_SIZE + 5)
            effect_rect = pygame.Rect(effect_x, effects_y, EFFECT_SLOT_SIZE, EFFECT_SLOT_SIZE)
            pygame.draw.rect(self.screen, WHITE, effect_rect)
            pygame.draw.rect(self.screen, BLACK, effect_rect, 1)

    def reset_game(self):
        self.grid = [[{'terrain': None} for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.current_piece = None
        self.preview_piece = None
        self.game_over = False
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
        grid_y = ((y - TOP_MARGIN) // BLOCK_SIZE)
        return grid_x, grid_y

    def is_mouse_in_grid(self, mouse_pos):
        # Check if mouse is in the game grid area
        x, y = mouse_pos
        return (0 <= x < GRID_WIDTH * BLOCK_SIZE and
                TOP_MARGIN <= y < TOP_MARGIN + GRID_HEIGHT * BLOCK_SIZE)

    def is_mouse_in_toolbar(self, mouse_pos):
        # Check if mouse is in the toolbar area (only left side where pieces are)
        x, y = mouse_pos
        toolbar_y = TOP_MARGIN + GRID_HEIGHT * BLOCK_SIZE
        return (0 <= x < BLOCK_SIZE * GRID_WIDTH and
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
        # Create new rotated shape and always allow rotation
        new_shape = list(zip(*piece['shape'][::-1]))
        piece['shape'] = new_shape


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

    def draw_piece(self, piece, x, y, alpha=255):
        for i, row in enumerate(piece['shape']):
            for j, cell in enumerate(row):
                if cell:
                    if self.terrain_images[piece['terrain']] is not None:
                        surface = self.terrain_images[piece['terrain']].copy()
                        surface.set_alpha(alpha)
                        self.screen.blit(surface, (x + j * BLOCK_SIZE, y + i * BLOCK_SIZE))
                    else:
                        pygame.draw.rect(self.screen, (128, 128, 128),
                                       [x + j * BLOCK_SIZE, y + i * BLOCK_SIZE, BLOCK_SIZE - 1, BLOCK_SIZE - 1])

    def draw(self):
        self.screen.fill(CREAM)

        # Draw grid
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                # Draw cell borders (single line)
                pygame.draw.rect(self.screen, BLACK,
                             (x * BLOCK_SIZE, y * BLOCK_SIZE + TOP_MARGIN,
                              BLOCK_SIZE - 1, BLOCK_SIZE - 1), 1)
                
                # Draw terrain if exists
                terrain = self.grid[y][x]['terrain']
                if terrain:
                    img = self.terrain_images.get(terrain)
                    if img:
                        self.screen.blit(img, 
                                        (x * BLOCK_SIZE, 
                                         y * BLOCK_SIZE + TOP_MARGIN))
        
        # Draw block group borders (double line)
        for block_y in range(BLOCK_COUNT):
            for block_x in range(BLOCK_COUNT):
                # Calculate the position of the block group
                start_x = block_x * FILL_BLOCK * BLOCK_SIZE
                start_y = block_y * FILL_BLOCK * BLOCK_SIZE + TOP_MARGIN
                width = FILL_BLOCK * BLOCK_SIZE
                height = FILL_BLOCK * BLOCK_SIZE
                
                # Draw outer line
                pygame.draw.rect(self.screen, BLACK,
                               (start_x, start_y, width, height), 2)
                # Draw inner line (offset by 2 pixels)
                pygame.draw.rect(self.screen, BLACK,
                               (start_x + 2, start_y + 2, width - 4, height - 4), 1)

        # Draw player slots
        for i in range(PLAYER_SLOTS):
            self.draw_player_slot(i, f'Player {i+1}')

        # Draw toolbar background
        toolbar_y = TOP_MARGIN + GRID_HEIGHT * BLOCK_SIZE
        pygame.draw.rect(self.screen, WHITE,
                       (0, toolbar_y, SCREEN_WIDTH, TOOLBAR_HEIGHT))

        # Draw toolbar pieces in the left side
        available_width = BLOCK_SIZE * GRID_WIDTH  # 使用整个左侧区域
        piece_spacing = available_width // (len(self.toolbar_pieces) + 1)
        for idx, piece in enumerate(self.toolbar_pieces):
            x = piece_spacing * (idx + 1) - (len(piece['shape'][0]) * BLOCK_SIZE) // 2
            y = toolbar_y + (TOOLBAR_HEIGHT - len(piece['shape']) * BLOCK_SIZE) // 2
            
            if piece['is_valid']:
                self.draw_piece(piece, x, y)
            else:
                self.draw_piece(piece, x, y, alpha=128)

        # Draw buttons
        for button in self.buttons:
            pygame.draw.rect(self.screen, BLACK, button['rect'], 2)
            text = self.button_font.render(button['text'], True, BLACK)
            text_rect = text.get_rect(center=button['rect'].center)
            self.screen.blit(text, text_rect)

        # Draw selected piece following mouse if exists
        if self.selected_piece and self.is_mouse_in_grid(self.mouse_pos):
            grid_x, grid_y = self.get_grid_pos_from_mouse(self.mouse_pos)
            x = grid_x * BLOCK_SIZE
            y = grid_y * BLOCK_SIZE + TOP_MARGIN
            self.draw_piece(self.selected_piece, x, y, alpha=128)

        # Draw tooltip if needed
        if self.show_tooltip and self.hover_piece:
            # self.draw_tooltip()   # 这里不需要对普通的地形有提示
            pass

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
        text = f"地形: {description}"  # 确保使用中文字体
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

    def draw_tooltip(self):
        if not self.hover_piece or not hasattr(self.hover_piece, 'get'):
            return
            
        terrain = self.hover_piece.get('terrain')
        if not terrain:
            return
            
        # Render tooltip text
        text = f'Terrain: {terrain.name}'
        text_surface = self.tooltip_font.render(text, True, BLACK)
        text_rect = text_surface.get_rect()
        
        # Position tooltip near mouse but ensure it stays on screen
        x, y = self.mouse_pos
        padding = 5
        
        # Adjust position to keep tooltip on screen
        if x + text_rect.width + padding * 2 > SCREEN_WIDTH:
            x = SCREEN_WIDTH - text_rect.width - padding * 2
        if y + text_rect.height + padding * 2 > SCREEN_HEIGHT:
            y = y - text_rect.height - padding * 2
        
        # Draw tooltip background and border
        pygame.draw.rect(self.screen, CREAM, (x, y, text_rect.width + padding * 2, text_rect.height + padding * 2))
        pygame.draw.rect(self.screen, BLACK, (x, y, text_rect.width + padding * 2, text_rect.height + padding * 2), 1)
        self.screen.blit(text_surface, (x + padding, y + padding))

    def get_hovered_piece(self, mouse_pos):
        x, y = mouse_pos
        
        # Check toolbar pieces
        if self.is_mouse_in_toolbar(mouse_pos):
            toolbar_y = TOP_MARGIN + GRID_HEIGHT * BLOCK_SIZE
            piece_spacing = BLOCK_SIZE * GRID_WIDTH // (len(self.toolbar_pieces) + 1)
            for idx, piece in enumerate(self.toolbar_pieces):
                piece_x = piece_spacing * (idx + 1) - (len(piece['shape'][0]) * BLOCK_SIZE) // 2
                piece_y = toolbar_y + (TOOLBAR_HEIGHT - len(piece['shape']) * BLOCK_SIZE) // 2
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
        # Get mouse position
        x, y = self.mouse_pos
        toolbar_y = TOP_MARGIN + GRID_HEIGHT * BLOCK_SIZE

        # Calculate piece positions using only the left side width
        available_width = BLOCK_SIZE * GRID_WIDTH
        piece_spacing = available_width // (len(self.toolbar_pieces) + 1)
        
        # Check each piece
        for idx, piece in enumerate(self.toolbar_pieces):
            piece_x = piece_spacing * (idx + 1) - (len(piece['shape'][0]) * BLOCK_SIZE) // 2
            piece_y = toolbar_y + (TOOLBAR_HEIGHT - len(piece['shape']) * BLOCK_SIZE) // 2
            piece_width = len(piece['shape'][0]) * BLOCK_SIZE
            piece_height = len(piece['shape']) * BLOCK_SIZE

            # Check if click is within piece bounds
            if (piece_x <= x < piece_x + piece_width and
                piece_y <= y < piece_y + piece_height):
                if piece['is_valid']:
                    self.selected_piece = piece
                break

    def handle_grid_click(self):
        if not self.selected_piece:
            return
            
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
            # Find the selected piece in toolbar_pieces and replace it
            for i, piece in enumerate(self.toolbar_pieces):
                if piece == self.selected_piece:
                    self.toolbar_pieces[i] = self.new_piece()
                    break
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
                        # 右键取消选择
                        self.selected_piece = None
                elif event.type == pygame.MOUSEWHEEL and not self.game_over:
                    if self.selected_piece:
                        # 使用滚轮旋转
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
