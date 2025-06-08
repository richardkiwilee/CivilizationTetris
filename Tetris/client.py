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
from Tetris.game.buildings import BuildingFactory
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
TOP_MARGIN = 200  # Height of top margin

# Top margin layout
TOP_MARGIN_SQUARE_WIDTH = TOP_MARGIN  # Left square area width equals top margin height
TOP_MARGIN_INFO_WIDTH = 500  # Fixed width for building info area
TOP_MARGIN_DESC_HEIGHT = int(TOP_MARGIN * 0.6)  # Description takes 60% of height
TOP_MARGIN_BUTTON_HEIGHT = TOP_MARGIN - TOP_MARGIN_DESC_HEIGHT  # Remaining height for buttons area
ACTION_BUTTON_WIDTH = 120  # Width for action buttons
ACTION_BUTTON_HEIGHT = 40  # Height for action buttons

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
        self.BuildingFactory = BuildingFactory()
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
        self.current_player_index = 0
        self.current_player_name = ""
        self.desktop_data = []
        self.puzzle_objs = {}
        self.selected_puzzle_id = None

        # 初始化字体
        self.small_font = pygame.font.Font(None, 24)  # 24是字体大小

        # Button setup
        button_x = BLOCK_SIZE * GRID_WIDTH + (PLAYER_SLOT_WIDTH - BUTTON_WIDTH) // 2
        self.buttons = [
            {'text': 'Ready', 'rect': pygame.Rect(button_x, SCREEN_HEIGHT - TOOLBAR_HEIGHT + 20, BUTTON_WIDTH, BUTTON_HEIGHT)}
        ]
        
        # Action buttons setup
        button_width = (TOP_MARGIN_INFO_WIDTH - 4 * BUTTON_MARGIN) // 3  # 将宽度平均分成3份
        button_y = TOP_MARGIN_DESC_HEIGHT + (TOP_MARGIN_BUTTON_HEIGHT - BUTTON_HEIGHT) // 2
        
        # Activate building button
        button_x = TOP_MARGIN_SQUARE_WIDTH + BUTTON_MARGIN
        activate_button = {
            'text': '激活建筑',
            'rect': pygame.Rect(button_x, button_y, button_width, BUTTON_HEIGHT),
            'enabled': False
        }
        
        # Upgrade building button
        button_x = TOP_MARGIN_SQUARE_WIDTH + 2 * BUTTON_MARGIN + button_width
        upgrade_button = {
            'text': '升级建筑',
            'rect': pygame.Rect(button_x, button_y, button_width, BUTTON_HEIGHT),
            'enabled': False
        }

        # Attack button
        button_x = TOP_MARGIN_SQUARE_WIDTH + 3 * BUTTON_MARGIN + 2 * button_width
        attack_button = {
            'text': '发动攻击',
            'rect': pygame.Rect(button_x, button_y, button_width, BUTTON_HEIGHT),
            'enabled': False
        }
        
        self.action_buttons = [activate_button, upgrade_button, attack_button]
        self.last_click_time = 0  # For tracking double clicks
        self.last_click_pos = None
        
        # Description area
        self.selected_building_desc = None
        
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
                self.desktop_data = json.loads(self.game_manager.get('Desktop', '[]'))
                players_data = self.game_manager.get('players', {})
                player_colors = [PLAYER1_COLOR, PLAYER2_COLOR, PLAYER3_COLOR, PLAYER4_COLOR]
                player_indices = {name: idx for idx, name in enumerate(players_data.keys())}
                
                for y, row in enumerate(self.desktop_data):
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
                        
                        # Draw terrain or building if exists
                        if cell:
                            if cell.get('terrainType'):
                                terrain = cell['terrainType']
                                img = self.terrain_images.get(terrain)
                                if img:
                                    self.screen.blit(img, 
                                                    (x * BLOCK_SIZE, 
                                                     y * BLOCK_SIZE + TOP_MARGIN))
                            elif cell.get('buildingType'):
                                building = cell['buildingType']
                                # Draw background color for building cells
                                if cell.get('owner') and cell['owner'] in player_indices:
                                    bg_color = player_colors[player_indices[cell['owner']]]
                                    bg_surface = pygame.Surface((BLOCK_SIZE - 1, BLOCK_SIZE - 1))
                                    bg_surface.fill(bg_color)
                                    bg_surface.set_alpha(128)  # 50% transparency
                                    self.screen.blit(bg_surface, rect)
                                # Draw building image
                                img = self.building_images.get(building)
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
        # logger.debug("In Draw func")
        with self.game_state_lock:
            # logger.debug(f"Game State: {self.game_state}; Toolbar Pieces: {len(self.toolbar_pieces)}")
            
            # Fill background
            self.screen.fill(CREAM)
            
            # Draw top margin layout
            # Left square area
            pygame.draw.rect(self.screen, BLACK, (0, 0, TOP_MARGIN_SQUARE_WIDTH, TOP_MARGIN), 2)
            
            # Draw description area
            desc_rect = pygame.Rect(TOP_MARGIN_SQUARE_WIDTH, 0, TOP_MARGIN_INFO_WIDTH, TOP_MARGIN_DESC_HEIGHT)
            pygame.draw.rect(self.screen, (200, 200, 200), desc_rect)
            pygame.draw.line(self.screen, (100, 100, 100), (TOP_MARGIN_SQUARE_WIDTH, 0), (TOP_MARGIN_SQUARE_WIDTH + TOP_MARGIN_INFO_WIDTH, 0), 2)
            pygame.draw.line(self.screen, (100, 100, 100), (TOP_MARGIN_SQUARE_WIDTH, TOP_MARGIN_DESC_HEIGHT), (TOP_MARGIN_SQUARE_WIDTH + TOP_MARGIN_INFO_WIDTH, TOP_MARGIN_DESC_HEIGHT), 2)
            pygame.draw.line(self.screen, (100, 100, 100), (TOP_MARGIN_SQUARE_WIDTH, 0), (TOP_MARGIN_SQUARE_WIDTH, TOP_MARGIN), 2)
            pygame.draw.line(self.screen, (100, 100, 100), (TOP_MARGIN_SQUARE_WIDTH + TOP_MARGIN_INFO_WIDTH, 0), (TOP_MARGIN_SQUARE_WIDTH + TOP_MARGIN_INFO_WIDTH, TOP_MARGIN), 2)
            
            # Draw button area
            button_rect = pygame.Rect(TOP_MARGIN_SQUARE_WIDTH, TOP_MARGIN_DESC_HEIGHT, TOP_MARGIN_INFO_WIDTH, TOP_MARGIN_BUTTON_HEIGHT)
            pygame.draw.rect(self.screen, (180, 180, 180), button_rect)
            pygame.draw.line(self.screen, (100, 100, 100), (TOP_MARGIN_SQUARE_WIDTH, TOP_MARGIN), (TOP_MARGIN_SQUARE_WIDTH + TOP_MARGIN_INFO_WIDTH, TOP_MARGIN), 2)
            
            # Draw description text if building is selected
            if self.selected_building_desc:
                line_height = self.font.get_height()
                for i, line in enumerate(self.selected_building_desc):
                    if line:  # 只渲染非空行
                        desc_text = self.font.render(line, True, BLACK)
                        desc_rect = desc_text.get_rect()
                        desc_rect.x = TOP_MARGIN_SQUARE_WIDTH + 10
                        desc_rect.y = 10 + i * (line_height + 5)  # 每行之间留5像素间距
                        self.screen.blit(desc_text, desc_rect)
                        

            
            # Draw action buttons
            for button in self.action_buttons:
                # Draw button background with different color based on enabled state
                bg_color = (220, 220, 220) if button['enabled'] else (180, 180, 180)
                pygame.draw.rect(self.screen, bg_color, button['rect'])
                # Draw button border
                border_color = BLACK if button['enabled'] else (150, 150, 150)
                pygame.draw.rect(self.screen, border_color, button['rect'], 2)
                # Draw button text
                text_color = BLACK if button['enabled'] else (100, 100, 100)
                text_surface = self.font.render(button['text'], True, text_color)
                text_rect = text_surface.get_rect(center=button['rect'].center)
                self.screen.blit(text_surface, text_rect)
            
            # Draw game grid and board pieces
            self.draw_game_board()
            
            # 鼠标在网格内，显示网格坐标
            if self.is_mouse_in_grid(self.mouse_pos):
                grid_x, grid_y = self.get_grid_pos_from_mouse(self.mouse_pos)
                try:
                    _ = self.desktop_data[grid_y][grid_x]
                except:
                    _ = None
                # 在TOP_MARGIN右侧区域显示坐标
                x_start = SCREEN_WIDTH - PLAYER_SLOT_WIDTH + 10
                y_start = TOP_MARGIN // 4
                line_spacing = 5
                
                # 第一行显示网格坐标
                coord_line = f"Grid: ({grid_x}, {grid_y})"
                text_surface = self.small_font.render(coord_line, True, RED)
                text_rect = text_surface.get_rect()
                text_rect.left = x_start
                text_rect.top = y_start
                self.screen.blit(text_surface, text_rect)
                
                # 显示网格单元格信息
                current_y = text_rect.bottom + line_spacing
                
                if _ is not None and isinstance(_, dict):
                    for key, value in _.items():
                        cell_line = f"{key}: {value}"
                        text_surface = self.small_font.render(cell_line, True, RED)
                        text_rect = text_surface.get_rect()
                        text_rect.left = x_start
                        text_rect.top = current_y
                        self.screen.blit(text_surface, text_rect)
                        current_y = text_rect.bottom + line_spacing
                else:
                    cell_line = "Cell: Empty"
                    text_surface = self.small_font.render(cell_line, True, RED)
                    text_rect = text_surface.get_rect()
                    text_rect.left = x_start
                    text_rect.top = current_y
                    self.screen.blit(text_surface, text_rect)
            
            # Draw player slots on the right side
            # logger.debug("Drawing player slots...")
            for i in range(PLAYER_SLOTS):
                if i in self.players and self.players[i]:
                    # logger.debug(f"Player {i}: {self.players[i]['name']}")
                    self.draw_player_slot(i, self.players[i])
                else:
                    # logger.debug(f"Player {i}: Empty")
                    self.draw_player_slot(i, None)
            
            # Draw toolbar at the bottom
            toolbar_y = SCREEN_HEIGHT - TOOLBAR_HEIGHT
            pygame.draw.rect(self.screen, WHITE, (0, toolbar_y, SCREEN_WIDTH, TOOLBAR_HEIGHT))
            pygame.draw.line(self.screen, BLACK, (0, toolbar_y), (SCREEN_WIDTH, toolbar_y))
            
            # Draw toolbar pieces in IN_GAME state
            if self.game_state == GameStatus.IN_GAME.value:
                # logger.debug("=== Drawing Toolbar Pieces ===")
                # 预设5个固定的grid位置
                max_pieces = 5
                available_width = BLOCK_SIZE * GRID_WIDTH
                piece_spacing = available_width // (max_pieces + 1)
                
                # logger.debug(f"Toolbar dimensions: width={available_width}, spacing={piece_spacing}")
                # logger.debug(f"Current toolbar pieces: {len(self.toolbar_pieces) if self.toolbar_pieces else 0}")
                
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
                            
                            # 计算缩放比例，确保拼块适合工具栏高度
                            max_height = TOOLBAR_HEIGHT - 20  # 去掉上下各神10像素的边距
                            scale = 1.0  # 默认不缩放
                            if piece_height > max_height:
                                scale = max_height / piece_height
                                piece_height = max_height
                                piece_width *= scale
                            
                            # 计算拼块的中心位置
                            x = piece_spacing * (idx + 1) - piece_width // 2
                            y = toolbar_y + 10  # 距离工具栏顶部10像素
                            
                            # 找到拼块的最高点（最大y值）
                            max_cell_y = max(y for _, y in cells)
                            
                            # 绘制每个方块
                            block_size = BLOCK_SIZE * scale  # 使用缩放后的块大小
                            for cell_x, cell_y in cells:
                                # 计算实际的绘制位置
                                block_x = x + (cell_x - min_x) * block_size
                                # 使用max_cell_y来对齐顶部
                                block_y = y + (max_cell_y - cell_y) * block_size
                                
                                # 绘制单个方块
                                if piece.get('is_valid', True):
                                    self.draw_block(block_x, block_y, piece.get('terrain', 1))
                                else:
                                    self.draw_block(block_x, block_y, piece.get('terrain', 1), alpha=128)
                    else:
                        logger.error(f"No piece for grid {idx}")
            
            # Draw buttons based on game state
            if self.game_state == GameStatus.IN_GAME.value:
                # Only show buttons if it's the current player's turn
                if self.current_player_name == self.username:
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
                    # Clear buttons list if it's not current player's turn
                    self.buttons = []
            else:
                # Draw Ready/Start button in lobby
                # Get first player (host) and current player
                host = next(iter(self.players.values()), None)
                current_player = next((p for p in self.players.values() if p and p['name'] == self.username), None)
                
                # Check if all players are ready
                all_ready = all(p.get('ready', False) for p in self.players.values() if p)
                players_count = sum(1 for p in self.players.values() if p)
                
                # Show buttons based on conditions
                if self.buttons and (
                    # Show Ready button for non-ready players
                    (not current_player.get('ready', False)) or
                    # Show Start button for host when all players are ready and more than 1 player
                    (host and host['name'] == self.username and all_ready)
                ):
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
            # Draw player name with color based on slot index
            name = player_data.get('name', 'Unknown')
            player_colors = [PLAYER1_COLOR, PLAYER2_COLOR, PLAYER3_COLOR, PLAYER4_COLOR]
            text_color = player_colors[slot_index] if slot_index < len(player_colors) else BLACK
            
            # Add hourglass emoji for current player in game
            if self.game_state == GameStatus.IN_GAME.value and player_data.get('current', False):
                name += ' (当前玩家)'
            if self.game_state == GameStatus.LOBBY.value:
                if player_data.get('ready', False):
                    name += ' (Ready)'
                else:
                    name += ' (Waiting...)'
            
            # Render player name with color
            name_text = self.font.render(name, True, text_color)
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
        # Check regular buttons
        for button in self.buttons:
            if button['rect'].collidepoint(pos):
                if self.game_state == GameStatus.LOBBY.value:
                    # Handle lobby buttons
                    if button['text'] == 'Ready':
                        self.sendMessage(PlayerAction.Ready.value, self.username, None, None, None, None)
                    elif button['text'] == 'Start':
                        self.sendMessage(PlayerAction.StartGame.value, self.username, None, None, None, None)
                else:
                    # Handle game buttons
                    if button['text'] == '更换建筑':
                        self.sendMessage(PlayerAction.ChangeCard.value, self.username, None, None, None, None)
                    elif button['text'] == '结束回合':
                        self.sendMessage(PlayerAction.EndTurn.value, self.username, None, None, None, None)
                    elif button['text'] == '发动攻击':
                        self.sendMessage(PlayerAction.Attack.value, self.username, None, None, None, None)
                return True
        
        # Check action buttons
        for button in self.action_buttons:
            if button['rect'].collidepoint(pos) and button['enabled']:
                if button['text'] == '激活建筑':
                    logger.debug('激活建筑')
                    if hasattr(self, 'selected_building_pos'):
                        self.activate_building()
                elif button['text'] == '升级建筑':
                    logger.debug('升级建筑')
                    if hasattr(self, 'selected_building_pos'):
                        self.upgrade_building()
                elif button['text'] == '发动攻击':
                    logger.debug('发动攻击')
                    if hasattr(self, 'selected_building_pos'):
                        self.attack()
                return True
        return False

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
            
            # Calculate piece position - 水平中心对齐
            piece_x = piece_spacing * (idx + 1) - piece_width // 2
            
            # 在工具栏中垂直定位
            # 对于单行形状，将其放在工具栏的上部位置
            if max_y == min_y:  # 单行形状
                piece_y = toolbar_y + BLOCK_SIZE
            else:  # 多行形状
                piece_y = toolbar_y + TOOLBAR_HEIGHT // 2
            
            # 检查点击是否在形状范围内
            # 因为draw_piece是向上绘制的，所以点击区域也应该向上检测
            if (piece_x <= x < piece_x + piece_width and
                piece_y - piece_height <= y < piece_y + piece_height):
                return piece
        
        return None

    def get_grid_pos_from_mouse(self, pos):
        """Convert mouse position to grid coordinates"""
        x = max(0, min(pos[0] // BLOCK_SIZE, GRID_WIDTH - 1))
        y = max(0, min((pos[1] - TOP_MARGIN) // BLOCK_SIZE, GRID_HEIGHT - 1))
        return x, y
        
    def select_building_at_pos(self, grid_x, grid_y):
        """Select a building at the given grid position and update description"""
        try:
            cell = self.desktop_data[grid_y][grid_x]
            if cell:
                print(cell)
                building_id = cell.get('building_id')
                puzzle_id = cell.get('puzzle_id')
                self.selected_puzzle_id = puzzle_id
                if building_id is not None:
                    building_data = self.BuildingFactory.GetBuildingById(building_id)
                    puzzle_data = self.puzzle_objs.get(str(puzzle_id))
                    print(puzzle_data)
                    common_text, activate_text, passive_text = self.BuildingFactory.GetTextById(building_id)
                    # 将描述文本组织成列表，便于逐行渲染
                    self.selected_building_desc = []
                    if common_text:
                        self.selected_building_desc.append(common_text)
                    if activate_text:
                        self.selected_building_desc.append(activate_text)
                    if passive_text:
                        self.selected_building_desc.append(passive_text)
                    self.selected_building_pos = (grid_x, grid_y)
                    # Enable/disable buttons based on ownership
                    is_owner = cell.get('owner') == self.username
                    for button in self.action_buttons:
                        button['enabled'] = is_owner
                    
                    self.needs_redraw = True
                    return True
        except (IndexError, KeyError) as e:
            logger.error(f"Error selecting building: {e}")
        return False

    def select_building_at_toolbar(self, building_id):
        """Select a building at the given grid position and update description"""
        try:
            building_data = self.BuildingFactory.GetBuildingById(building_id)
            common_text, activate_text, passive_text = self.BuildingFactory.GetTextById(building_id)
            # 将描述文本组织成列表，便于逐行渲染
            self.selected_building_desc = []
            if common_text:
                self.selected_building_desc.append(common_text)
            if activate_text:
                self.selected_building_desc.append(activate_text)
            if passive_text:
                self.selected_building_desc.append(passive_text)
            self.selected_building_pos = (building_id)
            # Enable/disable buttons based on ownership
            for button in self.action_buttons:
                button['enabled'] = False
            self.needs_redraw = True
            return True
        except (IndexError, KeyError) as e:
            logger.error(f"Error selecting building: {e}")
        return False

    def activate_building(self):
        puzzle_id = self.selected_puzzle_id
        self.sendMessage(PlayerAction.Active.value, self.username, puzzle_id, None, None, None)
        return True
        
    def upgrade_building(self):
        puzzle_id = self.selected_puzzle_id
        self.sendMessage(PlayerAction.Upgrade.value, self.username, puzzle_id, None, None, None)
        return True

    def attack(self):
        puzzle_id = self.selected_puzzle_id
        self.sendMessage(PlayerAction.Attack.value, self.username, puzzle_id, None, None, None)
        return True

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
                self.desktop_data = json.loads(self.game_manager.get('Desktop', '[]'))
                if self.desktop_data[y][x] != dict():
                    logger.error(f"Position ({x}, {y}) is already occupied: {self.desktop_data[y][x]}")
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
        
        # logger.debug(f"Placing piece at ({grid_x}, {grid_y}) with rotation {rotate}")
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
                    if event.button == pygame.BUTTON_LEFT:
                        # Handle button clicks
                        if self.handle_button_click(event.pos):
                            continue
                        
                        # Get current time for double-click detection
                        current_time = pygame.time.get_ticks()
                        
                        # Check if click is in toolbar
                        if self.is_mouse_in_toolbar(event.pos):
                            piece = self.get_toolbar_piece_at_pos(event.pos)
                            if piece:
                                self.selected_piece = piece.copy()
                                self.selected_building_desc = None  # Clear building description when selecting piece
                                if piece['building_id']:
                                    self.select_building_at_toolbar(piece['building_id'])
                                self.needs_redraw = True
                            continue
                        
                        # Check if click is in grid
                        if self.is_mouse_in_grid(event.pos):
                            grid_x, grid_y = self.get_grid_pos_from_mouse(event.pos)
                            if self.selected_piece:
                                # Try to place the piece
                                if self.check_valid_placement(self.selected_piece, grid_x, grid_y):
                                    rotate = self.calculate_rotation_count(
                                        self.selected_piece['shape'],
                                        self.selected_piece.get('rotated_cells', [])
                                    )
                                    self.place_piece(self.selected_piece['id'], rotate)
                                    self.selected_piece = None
                                    self.needs_redraw = True
                            else:
                                # Check for double click
                                is_double_click = False
                                if self.last_click_pos:
                                    last_x, last_y = self.last_click_pos
                                    if last_x == grid_x and last_y == grid_y:
                                        if current_time - self.last_click_time < 500:  # 500ms for double click
                                            is_double_click = True
                                
                                if is_double_click:
                                    # Try to select building on double click
                                    if self.desktop_data != []:
                                        cell = self.desktop_data[grid_y][grid_x]
                                        if cell and cell.get('building_id'):
                                            self.select_building_at_pos(grid_x, grid_y)
                                
                                # Update last click info
                                self.last_click_time = current_time
                                self.last_click_pos = (grid_x, grid_y)
                    elif event.button == pygame.BUTTON_RIGHT:
                        if self.selected_piece:
                            # Cancel piece selection on right click
                            self.selected_piece = None
                            self.selected_building_desc = None
                            self.needs_redraw = True
                        else:
                            # Clear building selection on right click
                            self.selected_building_desc = None
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
                    # logger.debug(f"In run: Drawing game state: {self.game_state}")
                    self.draw()
                    pygame.display.flip()
                    self.needs_redraw = False
                    last_draw_time = current_time
                except Exception as e:
                    logger.error(f"Error drawing game state: {e}")
                    logger.error(traceback.format_exc())

            # Control frame rate
            self.clock.tick(60)


    def is_mouse_in_grid(self, pos):
        """判断鼠标是否在游戏网格内"""
        x, y = pos
        grid_x = (x - 0) // BLOCK_SIZE
        grid_y = (y - TOP_MARGIN) // BLOCK_SIZE
        return (
            0 <= grid_x < GRID_WIDTH and
            0 <= grid_y < GRID_HEIGHT and
            TOP_MARGIN <= y < TOP_MARGIN + GRID_HEIGHT * BLOCK_SIZE
        )
    
    def get_grid_pos_from_mouse(self, pos):
        """获取鼠标位置对应的网格坐标"""
        x, y = pos
        grid_x = (x - 0) // BLOCK_SIZE
        grid_y = (y - TOP_MARGIN) // BLOCK_SIZE
        return grid_x, grid_y
    
    def is_mouse_in_toolbar(self, pos):
        """判断鼠标是否在工具栏区域内"""
        x, y = pos
        toolbar_y = SCREEN_HEIGHT - TOOLBAR_HEIGHT
        return toolbar_y <= y < SCREEN_HEIGHT
    
    def get_toolbar_piece_index(self, pos):
        """获取工具栏中鼠标位置对应的拼图索引"""
        if not self.is_mouse_in_toolbar(pos):
            return None
            
        x, y = pos
        max_pieces = 5
        available_width = BLOCK_SIZE * GRID_WIDTH
        piece_spacing = available_width // (max_pieces + 1)
        
        # 遍历所有可能的位置
        for idx in range(max_pieces):
            if idx < len(self.toolbar_pieces):
                piece = self.toolbar_pieces[idx]
                if piece and 'shape' in piece and piece['shape']:
                    # 获取形状的相对坐标
                    cells = ShapeHelper().GetShape(piece['shape'])
                    if cells:
                        # 计算形状的边界
                        min_x = min(x_ for x_, _ in cells)
                        max_x = max(x_ for x_, _ in cells)
                        
                        # 计算拼块的基准大小
                        piece_width = (max_x - min_x + 1) * BLOCK_SIZE
                        piece_height = (max_y - min_y + 1) * BLOCK_SIZE
                        
                        # 计算缩放比例，确保拼块适合工具栏高度
                        max_height = TOOLBAR_HEIGHT - 20
                        scale = 1.0
                        if piece_height > max_height:
                            scale = max_height / piece_height
                            piece_width *= scale
                        
                        # 计算拼块的中心位置
                        center_x = piece_spacing * (idx + 1)
                        piece_left = center_x - piece_width // 2
                        piece_right = center_x + piece_width // 2
                        
                        # 检查鼠标是否在当前拼块的范围内
                        if piece_left <= x <= piece_right:
                            return idx
        return None

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
                                self.current_player_index = data['current_player_index']
                                self.current_player_name = data['players'][self.current_player_index]
                                logger.debug(f'Receive IN_GAME Message: {data.keys()}')
                                # 保存游戏管理器状态
                                if 'manager' in data and 'players' in data['manager']:
                                    with self.game_state_lock:
                                        self.game_manager = data['manager']
                                        self.puzzle_objs = data['manager']['puzzle_objs']
                                        players_data = data['manager']['players']
                                        # logger.debug(f'players_data: {players_data}')
                                        
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
                                                            'current': player_name == self.current_player_name
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
                                            # logger.debug(f"Updated toolbar pieces: {len(self.toolbar_pieces)} pieces")
                                            for piece in self.toolbar_pieces:
                                                # logger.debug(f"Piece: {piece}")
                                                pass 
                                        
                                        # Initialize game buttons if needed
                                        if self.current_player_name == self.username:
                                            button_x = SCREEN_WIDTH - BUTTON_WIDTH - BUTTON_MARGIN
                                            button_y = SCREEN_HEIGHT - 2 * BUTTON_HEIGHT - 2 * BUTTON_MARGIN
                                            change_building_button = {
                                                'text': '更换建筑',
                                                'rect': pygame.Rect(button_x, button_y, BUTTON_WIDTH, BUTTON_HEIGHT)
                                            }
                                            
                                            button_y = SCREEN_HEIGHT - BUTTON_HEIGHT - BUTTON_MARGIN
                                            end_turn_button = {
                                                'text': '结束回合',
                                                'rect': pygame.Rect(button_x, button_y, BUTTON_WIDTH, BUTTON_HEIGHT)
                                            }
                                            self.buttons = [change_building_button, end_turn_button]
                                        else:
                                            self.buttons = []
                                    self.needs_redraw = True
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
