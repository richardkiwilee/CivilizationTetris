import time
import grpc
import threading
import traceback
import sys
import json
import pygame
import argparse
import logging
from Tetris.game.action import PlayerAction, SystemResponse
from Tetris.game.terrain import Terrain, ShapeHelper
import Tetris.protocol.service_pb2 as pb2
import Tetris.protocol.service_pb2_grpc as rpc
from Tetris.server import GameStatus
from enum import Enum

# 配置日志记录器
logger = logging.getLogger('CivilizationTetris')
logger.setLevel(logging.DEBUG)

# 创建控制台处理器
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# 创建格式化器
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)

# 将处理器添加到日志记录器
logger.addHandler(console_handler)

# Initialize Pygame
pygame.init()
pygame.font.init()

logger.info("Pygame initialized")
# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
CREAM = (255, 253, 208)

# Game Constants
BLOCK_SIZE = 30
FILL_BLOCK = 7  # 定义 FILL_BLOCK * FILL_BLOCK是一个正方形的小分组
BLOCK_COUNT = 4  # 定义每行和每列有多少个 FILL_BLOCK
GRID_WIDTH = BLOCK_COUNT * FILL_BLOCK
GRID_HEIGHT = BLOCK_COUNT * FILL_BLOCK
TOOLBAR_HEIGHT = 150  # Height of the bottom toolbar
TOP_MARGIN = 50  # Height of top margin

# UI Constants
PLAYER_SLOTS = 4  # Number of player slots
PLAYER_SLOT_HEIGHT = 180  # Height of each player slot
PLAYER_SLOT_WIDTH = 200  # Width of player slots area
RESOURCE_ICON_SIZE = 20  # Size of resource icons
EFFECT_SLOT_SIZE = 40  # Size of special effect slots
BUTTON_WIDTH = 100  # Width of buttons
BUTTON_HEIGHT = 40  # Height of buttons

# Screen dimensions
SCREEN_WIDTH = BLOCK_SIZE * GRID_WIDTH + PLAYER_SLOT_WIDTH
SCREEN_HEIGHT = max(BLOCK_SIZE * GRID_HEIGHT + TOP_MARGIN, PLAYER_SLOTS * PLAYER_SLOT_HEIGHT) + TOOLBAR_HEIGHT
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

# Colors
WHITE = (255, 255, 255)  # 玩家信息栏背景
BLACK = (0, 0, 0)    # 文字颜色
CREAM = (255, 253, 245)  # 游戏区域背景色
RED = (255, 0, 0)    # 无效放置提示

PLAYER1_COLOR = (255, 0, 0)
PLAYER2_COLOR = (0, 255, 0)
PLAYER3_COLOR = (0, 0, 255)
PLAYER4_COLOR = (255, 255, 0)

class Client:
    def __init__(self, username: str, address='localhost', port=50051):
        logger.info(f"Initializing client for user: {username}")
        self.username = username
        # 创建 gRPC 通道和存根
        channel = grpc.insecure_channel(address + ':' + str(port))
        self.stub = rpc.LobbyStub(channel)
        logger.info("gRPC channel created")
        
        # Initialize Pygame window
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(f'Civilization Tetris - {username}')
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('simhei', 24)
        logger.info("Pygame window initialized")
        
        # Load resources
        self.resource_images = self.load_resource_images()
        self.terrain_images = self.load_terrain_images()
        logger.info("Resources and terrains loaded")
        
        # Game state
        self.running = True
        self.game_state = GameStatus.LOBBY.value
        self.game_state_lock = threading.Lock()
        self.state_callback = None  # Callback for game state updates
        self.players = {}
        self.toolbar_pieces = []
        self.needs_redraw = False
        
        # Button setup
        button_x = BLOCK_SIZE * GRID_WIDTH + (PLAYER_SLOT_WIDTH - BUTTON_WIDTH) // 2
        self.buttons = [
            {'text': 'Ready', 'rect': pygame.Rect(button_x, SCREEN_HEIGHT - TOOLBAR_HEIGHT + 20, BUTTON_WIDTH, BUTTON_HEIGHT)}
        ]
        
        # Initialize empty player slots
        self.players = {i: None for i in range(PLAYER_SLOTS)}
        
        # Initialize toolbar pieces
        self.toolbar_pieces = []
        self.selected_piece = None
        self.mouse_pos = (0, 0)
        
        # Login to server
        loginResp = self.sendMessage(PlayerAction.Login.value, self.username, None, None, None, None)
        if not loginResp:
            raise Exception('Login failed')
        logger.info("Login to server successfully")
        # Initialize current player's slot
        self.players[0] = {
            'name': self.username,
            'resources': {},
            'ready': False
        }

        # Start message listener thread
        self.message_thread = threading.Thread(target=self.__listen_for_messages)
        self.message_thread.daemon = True
        self.message_thread.start()
        logger.info("Start message listener thread successfully")
        # Initialize lobby
        self.sendMessage(PlayerAction.Sync.value, self.username, None, None, None, None)
        logger.info("Sync to server successfully")

    def set_state_callback(self, callback):
        """Set callback function for game state updates"""
        self.state_callback = callback

    def update_game_state(self, new_state):
        """Update game state and trigger callback if set"""
        with self.game_state_lock:
            self.game_state = new_state
            if self.state_callback:
                self.state_callback(new_state)

    def load_resource_images(self):
        """Load and scale resource icons"""
        images = {}
        for resource_name, image_path in RESOURCE_TYPES:
            try:
                img = pygame.image.load(image_path)
                img = pygame.transform.scale(img, (RESOURCE_ICON_SIZE, RESOURCE_ICON_SIZE))
                images[resource_name] = img
            except pygame.error as e:
                logger.error(f'Warning: Could not load image for {resource_name}: {e}')
                images[resource_name] = None
        return images
    
    def load_terrain_images(self):
        """Load and scale terrain icons"""
        terrains = {
            Terrain.Mountain.value: 'icon_mountain.png',    # 山地
            Terrain.Forest.value: 'icon_forest.png',     # 森林
            Terrain.Plain.value: 'icon_plain.png',  # 平原
            Terrain.Farmland.value: 'icon_field.png',     # 农田
            Terrain.Urban.value: 'icon_neighborhood.png', # 社区
            Terrain.River.value: 'icon_river.png',      # 河流
            Terrain.Barren.value: 'icon_barren.png',       # 贫瘠
            Terrain.Building.value: 'icon_building.png' # 建筑
        }
        
        images = {}
        for terrain_id, image_name in terrains.items():
            try:
                img = pygame.image.load(f'Asset/Icons/TerrainsTypes/{image_name}')
                img = pygame.transform.scale(img, (BLOCK_SIZE - 2, BLOCK_SIZE - 2))  # 留出1像素边框
                images[terrain_id] = img
            except pygame.error as e:
                logger.error(f'Warning: Could not load terrain image {image_name}: {e}')
                images[terrain_id] = None
        return images
    
    def draw_block(self, x, y, terrain_type, alpha=255):
        """Draw a single block at the specified position with given terrain type"""
        # Draw terrain image or fallback to gray rectangle
        terrain_image = self.terrain_images.get(terrain_type)
        
        if terrain_image is not None:
            surface = terrain_image.copy()
            surface.set_alpha(alpha)
            self.screen.blit(surface, (x, y))
        else:
            pygame.draw.rect(self.screen, (128, 128, 128),
                           [x, y, BLOCK_SIZE - 1, BLOCK_SIZE - 1])
    
    def draw_piece(self, piece, x, y, alpha=255):
        """Draw a puzzle piece at the specified position"""
        if not piece or 'shape' not in piece:
            logger.error("Invalid piece or missing shape")
            return
            
        # 获取形状的相对坐标
        cells = None
        if 'rotated_cells' in piece:
            cells = piece['rotated_cells']
        else:
            shape_helper = ShapeHelper()
            cells = shape_helper.GetShape(piece['shape'])
        
        if not cells:
            logger.error("Empty shape")
            return
            
        # If drawing a selected piece over the grid, snap to grid
        if self.selected_piece is piece and self.is_mouse_in_grid((x, y)):
            grid_x, grid_y = self.get_grid_pos_from_mouse((x, y))
            x = grid_x * BLOCK_SIZE
            y = grid_y * BLOCK_SIZE + TOP_MARGIN
            
        # 绘制每个方块
        for cell_x, cell_y in cells:
            # 计算实际的绘制位置
            block_x = x + cell_x * BLOCK_SIZE
            # 注意这里使用cell_y的负值，因为向下为负
            block_y = y - cell_y * BLOCK_SIZE
            self.draw_block(block_x, block_y, piece.get('terrain', 0), alpha)
    
    def draw_game_board(self):
        """Draw the game grid and placed pieces"""
        # Draw grid lines and terrain
        if self.game_state == GameStatus.IN_GAME.value and hasattr(self, 'game_manager'):
            try:
                desktop_data = json.loads(self.game_manager.get('Desktop', '[]'))
                players_data = self.game_manager.get('players', {})
                player_colors = [PLAYER1_COLOR, PLAYER2_COLOR, PLAYER3_COLOR, PLAYER4_COLOR]
                player_indices = {name: idx for idx, name in enumerate(players_data.keys())}
                
                for y, row in enumerate(desktop_data):
                    for x, cell in enumerate(row):
                        # Draw cell borders and background
                        rect = pygame.Rect(
                            x * BLOCK_SIZE,
                            TOP_MARGIN + y * BLOCK_SIZE,
                            BLOCK_SIZE - 1,
                            BLOCK_SIZE - 1
                        )
                        
                        # Set background color based on owner
                        if cell and cell.get('owner'):
                            owner = cell['owner']
                            if owner in player_indices:
                                bg_color = player_colors[player_indices[owner]]
                                # Draw background with some transparency
                                bg_surface = pygame.Surface((BLOCK_SIZE - 1, BLOCK_SIZE - 1))
                                bg_surface.fill(bg_color)
                                bg_surface.set_alpha(128)  # 50% transparency
                                self.screen.blit(bg_surface, rect)
                        
                        pygame.draw.rect(self.screen, BLACK, rect, 1)
                        
                        # Draw terrain if exists
                        if cell and cell.get('terrainType'):
                            terrain = cell['terrainType']
                            img = self.terrain_images.get(terrain)
                            if img:
                                self.screen.blit(img, 
                                                (x * BLOCK_SIZE, 
                                                 y * BLOCK_SIZE + TOP_MARGIN))
                                                    
                # Draw block group borders
                for block_y in range(BLOCK_COUNT):
                    for block_x in range(BLOCK_COUNT):
                        # Calculate block group position
                        start_x = block_x * FILL_BLOCK * BLOCK_SIZE
                        start_y = block_y * FILL_BLOCK * BLOCK_SIZE + TOP_MARGIN
                        width = FILL_BLOCK * BLOCK_SIZE
                        height = FILL_BLOCK * BLOCK_SIZE
                        
                        # Draw outer line
                        pygame.draw.rect(self.screen, BLACK,
                                       (start_x, start_y, width, height), 2)
                        # Draw inner line
                        pygame.draw.rect(self.screen, BLACK,
                                       (start_x + 2, start_y + 2, width - 4, height - 4), 1)
                                       
            except json.JSONDecodeError as e:
                logger.error(f"Error decoding desktop data: {e}")
            except Exception as e:
                logger.error(f"Error drawing board: {e}")
                logger.error(traceback.format_exc())
        else:
            # Draw empty grid if not in game
            for y in range(GRID_HEIGHT):
                for x in range(GRID_WIDTH):
                    # Draw cell borders
                    rect = pygame.Rect(
                        x * BLOCK_SIZE,
                        TOP_MARGIN + y * BLOCK_SIZE,
                        BLOCK_SIZE - 1,
                        BLOCK_SIZE - 1
                    )
                    pygame.draw.rect(self.screen, BLACK, rect, 1)
            
            # Draw block group borders
            for block_y in range(BLOCK_COUNT):
                for block_x in range(BLOCK_COUNT):
                    # Calculate block group position
                    start_x = block_x * FILL_BLOCK * BLOCK_SIZE
                    start_y = block_y * FILL_BLOCK * BLOCK_SIZE + TOP_MARGIN
                    width = FILL_BLOCK * BLOCK_SIZE
                    height = FILL_BLOCK * BLOCK_SIZE
                    
                    # Draw outer line
                    pygame.draw.rect(self.screen, BLACK,
                                   (start_x, start_y, width, height), 2)
                    # Draw inner line
                    pygame.draw.rect(self.screen, BLACK,
                                   (start_x + 2, start_y + 2, width - 4, height - 4), 1)
        
    def draw(self):
        """Draw the game state"""
        logger.debug("In Draw func")
        with self.game_state_lock:
            logger.debug(f"Game State: {self.game_state}; Toolbar Pieces: {len(self.toolbar_pieces)}")
            
            # Fill background
            self.screen.fill(CREAM)
            
            # Draw game grid and board pieces
            self.draw_game_board()
            
            # 如果选中了拼块并且鼠标在网格内，显示网格坐标
            if self.selected_piece and self.is_mouse_in_grid(self.mouse_pos):
                grid_x, grid_y = self.get_grid_pos_from_mouse(self.mouse_pos)
                # 在TOP_MARGIN区域显示坐标
                coord_text = f"Grid: ({grid_x}, {grid_y})"
                text_surface = self.font.render(coord_text, True, BLACK)
                text_rect = text_surface.get_rect()
                text_rect.centerx = GRID_WIDTH * BLOCK_SIZE // 2
                text_rect.centery = TOP_MARGIN // 2
                self.screen.blit(text_surface, text_rect)
            
            # Draw player slots on the right side
            logger.debug("Drawing player slots...")
            for i in range(PLAYER_SLOTS):
                if i in self.players and self.players[i]:
                    logger.debug(f"Player {i}: {self.players[i]['name']}")
                    self.draw_player_slot(i, self.players[i])
                else:
                    logger.debug(f"Player {i}: Empty")
                    self.draw_player_slot(i, None)
            
            # Draw toolbar at the bottom
            toolbar_y = SCREEN_HEIGHT - TOOLBAR_HEIGHT
            pygame.draw.rect(self.screen, WHITE, (0, toolbar_y, SCREEN_WIDTH, TOOLBAR_HEIGHT))
            pygame.draw.line(self.screen, BLACK, (0, toolbar_y), (SCREEN_WIDTH, toolbar_y))
            
            # Draw toolbar pieces in IN_GAME state
            if self.game_state == GameStatus.IN_GAME.value:
                logger.debug("=== Drawing Toolbar Pieces ===")
                # 预设5个固定的grid位置
                max_pieces = 5
                available_width = BLOCK_SIZE * GRID_WIDTH
                piece_spacing = available_width // (max_pieces + 1)
                
                logger.debug(f"Toolbar dimensions: width={available_width}, spacing={piece_spacing}")
                logger.debug(f"Current toolbar pieces: {len(self.toolbar_pieces) if self.toolbar_pieces else 0}")
                
                # 初始化ShapeHelper
                shape_helper = ShapeHelper()
                
                # 遍历所有可能的位置
                for idx in range(max_pieces):
                    if self.toolbar_pieces and idx < len(self.toolbar_pieces):
                        piece = self.toolbar_pieces[idx]
                        if piece and 'shape' in piece and piece['shape']:
                            # 获取形状的相对坐标
                            cells = shape_helper.GetShape(piece['shape'])
                            if not cells:
                                continue
                                
                            # 计算形状的边界
                            min_x = min(x for x, _ in cells)
                            max_x = max(x for x, _ in cells)
                            min_y = min(y for _, y in cells)
                            max_y = max(y for _, y in cells)
                            
                            # 计算形状的尺寸
                            piece_width = (max_x - min_x + 1) * BLOCK_SIZE
                            piece_height = (max_y - min_y + 1) * BLOCK_SIZE
                            
                            # 计算中心位置
                            x = piece_spacing * (idx + 1) - piece_width // 2
                            # 使用固定的y值使所有拼块在同一水平线上
                            # 将y值调整为toolbar的中心，并考虑形状的高度
                            y = toolbar_y + (TOOLBAR_HEIGHT - piece_height) // 2
                            
                            # 绘制每个方块
                            for cell_x, cell_y in cells:
                                # 计算实际的绘制位置
                                block_x = x + (cell_x - min_x) * BLOCK_SIZE
                                # 注意这里使用cell_y的负值，因为向下为负
                                block_y = y + (-cell_y - min_y) * BLOCK_SIZE
                                
                                # 绘制单个方块
                                if piece.get('is_valid', True):
                                    self.draw_block(block_x, block_y, piece.get('terrain', 1))
                                else:
                                    self.draw_block(block_x, block_y, piece.get('terrain', 1), alpha=128)
                    else:
                        logger.error(f"No piece for grid {idx}")
            
            # Draw buttons based on game state
            if self.game_state == GameStatus.IN_GAME.value:
                # Draw ChangeBuilding button
                button_x = SCREEN_WIDTH - BUTTON_WIDTH - BUTTON_MARGIN
                button_y = SCREEN_HEIGHT - 2 * BUTTON_HEIGHT - 2 * BUTTON_MARGIN
                change_building_button = {
                    'text': '更换建筑',
                    'rect': pygame.Rect(button_x, button_y, BUTTON_WIDTH, BUTTON_HEIGHT)
                }
                
                # Draw EndTurn button
                button_x = SCREEN_WIDTH - BUTTON_WIDTH - BUTTON_MARGIN
                button_y = SCREEN_HEIGHT - BUTTON_HEIGHT - BUTTON_MARGIN
                end_turn_button = {
                    'text': '结束回合',
                    'rect': pygame.Rect(button_x, button_y, BUTTON_WIDTH, BUTTON_HEIGHT)
                }
                
                # Draw ChangeBuilding button
                pygame.draw.rect(self.screen, WHITE, change_building_button['rect'])
                pygame.draw.rect(self.screen, BLACK, change_building_button['rect'], 1)
                text = self.font.render(change_building_button['text'], True, BLACK)
                text_rect = text.get_rect(center=change_building_button['rect'].center)
                self.screen.blit(text, text_rect)

                # Draw EndTurn button
                pygame.draw.rect(self.screen, WHITE, end_turn_button['rect'])
                pygame.draw.rect(self.screen, BLACK, end_turn_button['rect'], 1)
                text = self.font.render(end_turn_button['text'], True, BLACK)
                text_rect = text.get_rect(center=end_turn_button['rect'].center)
                self.screen.blit(text, text_rect)
                
                # Update buttons list for click handling
                self.buttons = [change_building_button, end_turn_button]
            else:
                # Draw Ready/Start button in lobby
                for button in self.buttons:
                    pygame.draw.rect(self.screen, WHITE, button['rect'])
                    pygame.draw.rect(self.screen, BLACK, button['rect'], 1)
                    text = self.font.render(button['text'], True, BLACK)
                    text_rect = text.get_rect(center=button['rect'].center)
                    self.screen.blit(text, text_rect)
            
            # Update the display
            pygame.display.flip()
        
        # Draw selected piece following mouse if exists
        if self.selected_piece and self.game_state == GameStatus.IN_GAME.value:
            mouse_x, mouse_y = self.mouse_pos
            self.draw_piece(self.selected_piece, mouse_x, mouse_y, alpha=128)
        
        pygame.display.flip()
    
    def draw_player_slot(self, slot_index, player_data=None):
        """Draw a player slot with their information"""
        x = BLOCK_SIZE * GRID_WIDTH
        y = TOP_MARGIN + slot_index * PLAYER_SLOT_HEIGHT
        
        # Draw slot background
        slot_rect = pygame.Rect(x, y, PLAYER_SLOT_WIDTH, PLAYER_SLOT_HEIGHT)
        bg_color = WHITE if player_data else (200, 200, 200)  # Gray for empty slots
        pygame.draw.rect(self.screen, bg_color, slot_rect)
        pygame.draw.rect(self.screen, BLACK, slot_rect, 1)
        
        if player_data:
            # Draw player name
            name = player_data.get('name', 'Unknown')
            if self.game_state == GameStatus.IN_GAME.value:
                if player_data.get('current', False):
                    name += ' (Current Player)'
            if self.game_state == GameStatus.LOBBY.value:
                if player_data.get('ready', False):
                    name += ' (Ready)'
                else:
                    name += ' (Waiting)'
            name_font = pygame.font.Font(None, 24)
            name_text = name_font.render(name, True, BLACK)
            self.screen.blit(name_text, (x + 5, y + 5))
            
            # Get resources from player data
            resources = player_data.get('resources', {})
            
            resource_font = pygame.font.Font(None, 20)
            # 资源类型对应关系，从枚举值映射到资源名称
            resource_mapping = {
                '1': 'food',   # PlayerResource.Food.value
                '2': 'wood',   # PlayerResource.Wood.value
                '3': 'stone',  # PlayerResource.Stone.value
                '0': 'gold',   # PlayerResource.Gold.value
                '6': 'faith',  # PlayerResource.Faith.value
                '8': 'citizen',# PlayerResource.Citizen.value
                '7': 'order'   # PlayerResource.Decree.value
            }
            left_resources = ['1', '2', '3']  # Food, Wood, Stone
            right_resources = ['0', '6', '8', '7']  # Gold, Faith, Citizen, Order
            
            # Left column resources
            for i, resource_id in enumerate(left_resources):
                icon_y = y + 30 + i * (RESOURCE_ICON_SIZE + 5)
                resource_name = resource_mapping.get(resource_id)
                if resource_name and self.resource_images.get(resource_name):
                    self.screen.blit(self.resource_images[resource_name], (x + 5, icon_y))
                value_text = resource_font.render(str(resources.get(resource_id, '0')), True, BLACK)
                self.screen.blit(value_text, (x + RESOURCE_ICON_SIZE + 10, icon_y + 2))
            
            # Right column resources
            for i, resource_id in enumerate(right_resources):
                icon_y = y + 30 + i * (RESOURCE_ICON_SIZE + 5)
                resource_name = resource_mapping.get(resource_id)
                if resource_name and self.resource_images.get(resource_name):
                    self.screen.blit(self.resource_images[resource_name], (x + PLAYER_SLOT_WIDTH//2, icon_y))
                value_text = resource_font.render(str(resources.get(resource_id, '0')), True, BLACK)
                self.screen.blit(value_text, (x + PLAYER_SLOT_WIDTH//2 + RESOURCE_ICON_SIZE + 5, icon_y + 2))
            
            # Draw special effects slots
            effects_y = y + PLAYER_SLOT_HEIGHT - EFFECT_SLOT_SIZE - 5
            for i in range(4):
                effect_x = x + 5 + i * (EFFECT_SLOT_SIZE + 5)
                effect_rect = pygame.Rect(effect_x, effects_y, EFFECT_SLOT_SIZE, EFFECT_SLOT_SIZE)
                pygame.draw.rect(self.screen, WHITE, effect_rect)
                pygame.draw.rect(self.screen, BLACK, effect_rect, 1)
                
                # Draw effect icon if player has one
                effects = player_data.get('effects', [])
                if i < len(effects):
                    effect = effects[i]
                    # TODO: Draw effect icon when implemented
        else:
            # Draw empty slot text
            empty_text = self.font.render('Empty Slot', True, (128, 128, 128))
            text_rect = empty_text.get_rect(center=slot_rect.center)
            self.screen.blit(empty_text, text_rect)

    def handle_button_click(self, pos):
        # 检查所有按钮的点击
        for button in self.buttons:
            if button['rect'].collidepoint(pos):
                if self.game_state == GameStatus.LOBBY.value:
                    # 处理大厅中的按钮
                    if button['text'] == 'Ready':
                        self.sendMessage(PlayerAction.Ready.value, self.username, None, None, None, None)
                    elif button['text'] == 'Start':
                        self.sendMessage(PlayerAction.StartGame.value, self.username, None, None, None, None)
                else:
                    # 处理游戏中的按钮
                    if button['text'] == '更换建筑':
                        self.sendMessage(PlayerAction.ChangeCard.value, self.username, None, None, None, None)
                    elif button['text'] == '结束回合':
                        self.sendMessage(PlayerAction.EndTurn.value, self.username, None, None, None, None)
                break

    def is_mouse_in_toolbar(self, pos):
        """Check if mouse is in the toolbar area"""
        return SCREEN_HEIGHT - TOOLBAR_HEIGHT <= pos[1] <= SCREEN_HEIGHT

    def get_toolbar_piece_at_pos(self, pos):
        """Get the piece at the given position in the toolbar"""
        if not self.toolbar_pieces:
            return None
            
        x, y = pos
        toolbar_y = SCREEN_HEIGHT - TOOLBAR_HEIGHT

        # Calculate piece positions using only the left side width
        available_width = BLOCK_SIZE * GRID_WIDTH
        max_pieces = max(5, len(self.toolbar_pieces))  # 至少预留5个位置
        piece_spacing = available_width // (max_pieces + 1)

        # 初始化ShapeHelper
        shape_helper = ShapeHelper()

        # Check each piece
        for idx, piece in enumerate(self.toolbar_pieces):
            # 获取形状的相对坐标
            cells = shape_helper.GetShape(piece['shape'])
            if not cells:
                continue
                
            # 计算形状的边界
            min_x = min(x for x, _ in cells)
            max_x = max(x for x, _ in cells)
            min_y = min(y for _, y in cells)
            max_y = max(y for _, y in cells)
            
            # 计算形状的尺寸
            piece_width = (max_x - min_x + 1) * BLOCK_SIZE
            piece_height = (max_y - min_y + 1) * BLOCK_SIZE
            
            # Calculate piece position
            piece_x = piece_spacing * (idx + 1) - piece_width // 2
            piece_y = toolbar_y + (TOOLBAR_HEIGHT - piece_height) // 2
            
            # Check if click is within piece bounds
            if (piece_x <= x < piece_x + piece_width and
                piece_y <= y < piece_y + piece_height):
                return piece
        
        return None

    def get_grid_pos_from_mouse(self, pos):
        """Convert mouse position to grid coordinates"""
        x = max(0, min(pos[0] // BLOCK_SIZE, GRID_WIDTH - 1))
        y = max(0, min((pos[1] - TOP_MARGIN) // BLOCK_SIZE, GRID_HEIGHT - 1))
        return x, y

    def is_mouse_in_grid(self, pos):
        """Check if mouse is in the game grid"""
        x, y = pos
        return (0 <= x < GRID_WIDTH * BLOCK_SIZE and
                TOP_MARGIN <= y < TOP_MARGIN + GRID_HEIGHT * BLOCK_SIZE)

    def check_valid_placement(self, piece, grid_x, grid_y):
        """Check if piece can be placed at the given grid position"""
        if not piece or 'shape' not in piece:
            logger.error(f"piece is invalid or shape is missing: {piece}")
            return False

        # 获取旋转后的相对坐标
        cells = None
        if 'rotated_cells' in piece:
            cells = piece['rotated_cells']
        else:
            shape_helper = ShapeHelper()
            cells = shape_helper.GetShape(piece['shape'])
        
        if not cells:
            logger.error("Empty shape")
            return False

        # 检查每个方块的位置
        for cell_x, cell_y in cells:
            # 计算实际的网格位置
            x = grid_x + cell_x
            y = grid_y - cell_y  # 注意这里是减号，因为向下为负
            
            # 检查是否超出网格范围
            if not (0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT):
                logger.error(f"Invalid position: ({x}, {y}) outside grid bounds")
                return False
                
            # 检查该位置是否已被占用
            try:
                desktop_data = json.loads(self.game_manager.get('Desktop', '[]'))
                if desktop_data[y][x] != dict():
                    logger.error(f"Position ({x}, {y}) is already occupied: {desktop_data[y][x]}")
                    return False
            except (json.JSONDecodeError, IndexError, KeyError) as e:
                logger.error(f"Error checking desktop data: {e}")
                return False
        return True

    def rotate_piece(self, piece):
        """Rotate the piece 90 degrees clockwise"""
        if not piece or 'shape' not in piece:
            return piece

        # 初始化rotation计数
        if 'rotation' not in piece:
            piece['rotation'] = 0

        # 顺时针旋转90度，增加rotation计数
        piece['rotation'] = (piece['rotation'] + 1) % 4

        # 获取当前形状的相对坐标
        shape_helper = ShapeHelper()
        cells = shape_helper.GetShape(piece['shape'])
        if not cells:
            return piece

        # 根据rotation次数旋转相对坐标
        # 对于每个点(x,y)：
        # 旋转90度：(y,-x)
        # 旋转180度：(-x,-y)
        # 旋转270度：(-y,x)
        rotated_cells = []
        for x, y in cells:
            for _ in range(piece['rotation']):
                x, y = y, -x
            rotated_cells.append((x, y))

        # 更新piece的cells
        piece['rotated_cells'] = rotated_cells
        return piece

    def calculate_rotation_count(self, original_shape, current_shape):
        """返回当前的rotation值"""
        if self.selected_piece and 'rotation' in self.selected_piece:
            return self.selected_piece['rotation']
        return 0

    def place_piece(self, puzzle_id, rotate):
        """放置棋子并发送消息到服务器"""
        grid_x, grid_y = self.get_grid_pos_from_mouse(self.mouse_pos)
        
        # 获取形状的相对坐标
        shape_helper = ShapeHelper()
        cells = shape_helper.GetShape(self.selected_piece['shape'])
        if not cells:
            return
            
        # 计算形状的边界
        min_x = min(x for x, _ in cells)
        max_x = max(x for x, _ in cells)
        min_y = min(y for _, y in cells)
        max_y = max(y for _, y in cells)
        
        # 计算形状的尺寸
        piece_width = (max_x - min_x + 1)
        piece_height = (max_y - min_y + 1)
        
        logger.debug(f"Placing piece at ({grid_x}, {grid_y}) with rotation {rotate}")
        # 发送放置消息
        resp = self.sendMessage(
            PlayerAction.Place.value,
            self.username,
            str(puzzle_id),
            str(grid_x),
            str(grid_y),
            str(rotate)
        )        
        if resp.status == SystemResponse.OK.value:
            resp = self.sendMessage(PlayerAction.EndTurn.value, self.username)

    def run(self):
        """Main game loop"""
        logger.info("Starting game loop...")
        self.needs_redraw = True  # Force initial draw
        last_piece_pos = None
        last_draw_time = time.time()
        
        while self.running:
            current_time = time.time()
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.handle_quit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.handle_quit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        if self.game_state == GameStatus.IN_GAME.value:
                            if self.selected_piece:
                                # Try to place the piece
                                if self.is_mouse_in_grid(event.pos):
                                    grid_x, grid_y = self.get_grid_pos_from_mouse(event.pos)
                                    logger.debug(f"Placing piece at ({grid_x}, {grid_y})")
                                    if self.check_valid_placement(self.selected_piece, grid_x, grid_y):
                                        # 计算旋转次数
                                        original_shape = self.selected_piece.get('original_shape', self.selected_piece['shape'])
                                        current_shape = self.selected_piece['shape']
                                        rotate_count = self.calculate_rotation_count(original_shape, current_shape)
                                        logger.debug(f"Rotating piece {rotate_count} times")
                                        # 放置棋子
                                        piece_id = self.selected_piece.get('id')
                                        logger.debug(f'Place puzzle_id={piece_id}')
                                        try:
                                            self.place_piece(piece_id, rotate_count)
                                        except Exception as e:
                                            logger.error(f"Failed to place piece: {e}")
                                        finally:
                                            self.needs_redraw = True
                                        
                                        # 取消选中状态
                                        self.selected_piece = None
                                        last_piece_pos = None
                                    else:
                                        logger.error(f'invalid placement {self.selected_piece} at ({grid_x}, {grid_y})')
                                else:
                                    logger.error("Invalid placement")
                            else:
                                # Try to select a piece from toolbar
                                piece = self.get_toolbar_piece_at_pos(event.pos)
                                if piece:
                                    self.selected_piece = piece.copy()
                                    self.needs_redraw = True
                        self.handle_button_click(event.pos)
                    elif event.button == 3:  # Right click
                        # Cancel piece selection
                        if self.selected_piece:
                            self.selected_piece = None
                            last_piece_pos = None
                            self.needs_redraw = True
                elif event.type == pygame.MOUSEMOTION:
                    self.mouse_pos = event.pos
                    # Only redraw if we have a selected piece and it's over the grid
                    if self.selected_piece and self.is_mouse_in_grid(event.pos):
                        current_pos = self.get_grid_pos_from_mouse(event.pos)
                        if last_piece_pos != current_pos:
                            last_piece_pos = current_pos
                            self.needs_redraw = True
                elif event.type == pygame.MOUSEWHEEL:
                    # Rotate selected piece
                    if self.selected_piece:
                        # 向下滚动时y为负，顺时针旋转
                        # 向上滚动时y为正，逆时针旋转
                        if event.y < 0:  # 向下滚动
                            # 顺时针旋转
                            self.selected_piece['rotation'] = (self.selected_piece.get('rotation', 0) + 1) % 4
                        else:  # 向上滚动
                            # 逆时针旋转
                            self.selected_piece['rotation'] = (self.selected_piece.get('rotation', 0) - 1) % 4
                        
                        # 获取形状的相对坐标
                        shape_helper = ShapeHelper()
                        cells = shape_helper.GetShape(self.selected_piece['shape'])
                        if cells:
                            # 根据rotation次数旋转相对坐标
                            rotated_cells = []
                            for x, y in cells:
                                rx, ry = x, y
                                for _ in range(self.selected_piece['rotation']):
                                    rx, ry = ry, -rx
                                rotated_cells.append((rx, ry))
                            self.selected_piece['rotated_cells'] = rotated_cells
                            self.needs_redraw = True

            # Draw if needed and enough time has passed since last draw
            if self.needs_redraw and current_time - last_draw_time >= 1/30:  # 限制最大刷新率为30FPS
                try:
                    logger.debug(f"In run: Drawing game state: {self.game_state}")
                    self.draw()
                    pygame.display.flip()
                    self.needs_redraw = False
                    last_draw_time = current_time
                except Exception as e:
                    logger.error(f"Error drawing game state: {e}")
                    logger.error(traceback.format_exc())

            # Control frame rate
            self.clock.tick(60)


    def __listen_for_messages(self):
        """Listen for messages from the server and update game state"""
        try:
            while self.running:
                response = self.stub.Subscribe(pb2.GeneralRequest(
                    sender=self.username,
                    body=json.dumps({})
                ))
                for message in response:
                    try:
                        data = json.loads(message.body)
                        if isinstance(data, dict):
                            if data['status'] == GameStatus.LOBBY.value and 'ready_status' in data:
                                # Clear all slots first
                                self.players = {i: None for i in range(PLAYER_SLOTS)}
                                # Fill slots in order of ready_status dictionary
                                for i, (player_name, is_ready) in enumerate(data['ready_status'].items()):
                                    if i < PLAYER_SLOTS:
                                        self.players[i] = {
                                            'name': player_name,
                                            'resources': {},
                                            'ready': is_ready
                                        }
                                # Update button text for host (first player)
                                # Update button text based on game state
                                if self.username == list(data['ready_status'].keys())[0]:
                                    # Check if all players are ready
                                    all_ready = all(is_ready for is_ready in data['ready_status'].values())
                                    self.buttons[0]['text'] = 'Start' if all_ready else 'Ready'
                                # 强制刷新界面
                                self.needs_redraw = True
                            if data['status'] == GameStatus.IN_GAME.value:
                                current_player_index = data['current_player_index']
                                current_player_name = data['players'][current_player_index]
                                logger.debug(f'Receive IN_GAME Message: {data.keys()}')
                                # 保存游戏管理器状态
                                if 'manager' in data and 'players' in data['manager']:
                                    with self.game_state_lock:
                                        self.game_manager = data['manager']
                                        players_data = data['manager']['players']
                                        logger.debug(f'players_data: {players_data}')
                                        
                                        # First update the player order and resources
                                        if 'players' in data:
                                            # Reset all player slots first
                                            self.players = {i: None for i in range(PLAYER_SLOTS)}
                                            
                                            # Update player slots in the correct order
                                            for i, player_name in enumerate(data['players']):
                                                if i < PLAYER_SLOTS:
                                                    player_info = players_data.get(player_name, {})
                                                    if isinstance(player_info, dict):
                                                        self.players[i] = {
                                                            'name': player_name,
                                                            'resources': player_info.get('resources', {}),
                                                            'ready': True,  # In game, all players are ready
                                                            'current': player_name == current_player_name
                                                        }
                                        
                                        # Update the game state first
                                        self.game_state = data['status']
                                        # logger.info(f"Game state updated to: {self.game_state}")
                                        
                                        # Then update current player's toolbar pieces
                                        current_player_data = players_data.get(self.username, {})
                                        if isinstance(current_player_data, dict) and 'puzzles' in current_player_data:
                                            puzzles_data = current_player_data['puzzles']
                                            self.toolbar_pieces = []
                                            for puzzle_id, puzzle_info in puzzles_data.items():
                                                piece = {
                                                    'id': puzzle_id,
                                                    'shape': puzzle_info.get('shape', None),
                                                    'terrain': puzzle_info.get('terrainType', None),
                                                    'building_id': puzzle_info.get('building_id', None),
                                                    'is_valid': True
                                                }
                                                self.toolbar_pieces.append(piece)
                                            logger.debug(f"Updated toolbar pieces: {len(self.toolbar_pieces)} pieces")
                                            for piece in self.toolbar_pieces:
                                                logger.debug(f"Piece: {piece}")
                                        
                                        # Update button text based on game state
                                        self.buttons[0]['text'] = 'EndTurn'
                                        
                                        # 只设置重绘标志，让主循环处理重绘
                                        self.needs_redraw = True
                                        # logger.debug("Set needs_redraw to True")
                    except json.JSONDecodeError:
                        logger.error('Error decoding message:', message.body)
                        traceback.print_exc()
                    except Exception as e:
                        logger.error('Error processing message:', str(e))
                        traceback.print_exc()
        except Exception as e:
            logger.error('Error in message listener:', str(e))
            traceback.print_exc()
        finally:
            logger.info('Message listener stopped')

    def update_players(self, users_data):
        """Update player slots with user data"""
        # Clear all slots first
        self.players = {i: None for i in range(PLAYER_SLOTS)}
        
        # Update slots with connected players
        for i, (username, data) in enumerate(users_data.items()):
            if i < PLAYER_SLOTS:
                self.players[i] = {
                    'name': username,
                    'resources': data.get('resources', {}),
                    'ready': data.get('ready', False)
                }

        # 检查是否所有玩家都准备好了
        all_ready = True
        for player in self.players.values():
            if player and not player.get('ready', False):
                all_ready = False
                break

        # 更新按钮状态
        if self.game_state == GameStatus.LOBBY.value:
            # 获取当前玩家的状态
            current_player = next((p for p in self.players.values() if p and p['name'] == self.username), None)
            is_host = self.username == next(iter(users_data.keys()))
            
            # 更新按钮
            if is_host and all_ready and len(users_data) > 1:
                self.buttons = [{'text': 'Start', 'rect': pygame.Rect(
                    BLOCK_SIZE * GRID_WIDTH + (PLAYER_SLOT_WIDTH - BUTTON_WIDTH) // 2,
                    SCREEN_HEIGHT - TOOLBAR_HEIGHT + 20,
                    BUTTON_WIDTH, BUTTON_HEIGHT
                )}]
            else:
                ready_status = current_player.get('ready', False)
                self.buttons = [{'text': 'Ready' if not ready_status else 'Waiting...', 'rect': pygame.Rect(
                    BLOCK_SIZE * GRID_WIDTH + (PLAYER_SLOT_WIDTH - BUTTON_WIDTH) // 2,
                    SCREEN_HEIGHT - TOOLBAR_HEIGHT + 20,
                    BUTTON_WIDTH, BUTTON_HEIGHT
                )}]

        # Ensure current player is always in slot 0
        for i, player in self.players.items():
            if player and player['name'] == self.username:
                if i != 0:  # If current player is not in slot 0
                    self.players[0], self.players[i] = self.players[i], self.players[0]

    def handle_quit(self):
        """Handle quit event"""
        try:
            # Send logout message
            self.sendMessage(PlayerAction.Logout.value, self.username)
            # Stop message thread
            self.running = False
            if hasattr(self, 'message_thread') and self.message_thread.is_alive():
                self.message_thread.join(timeout=1)
        except Exception as e:
            logger.error(f'Error during cleanup: {e}')
        finally:
            pygame.quit()
            sys.exit()

    def sendMessage(self, action, arg1=None, arg2=None, arg3=None, arg4=None, arg5=None):
        """Send message to server"""
        try:
            msg = {
                'action': action,
                'arg1': arg1,
                'arg2': arg2,
                'arg3': arg3,
                'arg4': arg4,
                'arg5': arg5
            }
            response = self.stub.Handle(pb2.GeneralRequest(
                sender=self.username,
                body=json.dumps(msg)
            ))
            return response
        except Exception as e:
            logger.error(f'Error sending message: {e}')
            return None

def main():
    parser = argparse.ArgumentParser(description='Civilization Tetris Client')
    parser.add_argument('--address', default='localhost', help='Server address')
    parser.add_argument('--port', type=int, default=50051, help='Server port')
    parser.add_argument('--username', default=None, help='Username for the game')
    
    args = parser.parse_args()
    
    # Generate random username if not provided
    if not args.username:
        args.username = f'Player_{int(time.time()) % 1000}'
    
    client = None
    try:
        logger.info("Creating client...")
        client = Client(args.username, args.address, args.port)
        logger.info("Client created, starting game loop...")
        client.run()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        logger.error(traceback.format_exc())
    finally:
        if client:
            client.handle_quit()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.info('\nReceived shutdown signal')
        if client:
            client.handle_quit()
