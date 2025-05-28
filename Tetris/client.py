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
import Tetris.protocol.service_pb2 as pb2
import Tetris.protocol.service_pb2_grpc as rpc
from enum import Enum

from Tetris.server import GameStatus

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
TOOLBAR_HEIGHT = 100  # Height of the bottom toolbar
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
        logger.info("Resources loaded")
        
        # Game state
        self.running = True
        self.game_state = GameStatus.LOBBY.value
        self.game_state_lock = threading.Lock()
        self.state_callback = None  # Callback for game state updates
        self.players = {}
        self.toolbar_pieces = []
        self.needs_redraw = False
        self.redraw_lock = threading.Lock()
        
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

    def get_shape_matrix(self, shape_name):
        """Convert shape name to shape matrix"""
        if not shape_name:
            logger.error("Shape name is None or empty")
            return [[1]]  # Default single block
            
        logger.debug(f"Converting shape: {shape_name}")
        if shape_name == 'Corner':
            return [
                [1, 1],
                [1, 0]
            ]
        elif shape_name == 'O':
            return [
                [1, 1],
                [1, 1]
            ]
        elif shape_name == 'L':
            return [
                [1, 0],
                [1, 0],
                [1, 1]
            ]
        elif shape_name == 'J':
            return [
                [0, 1],
                [0, 1],
                [1, 1]
            ]
        elif shape_name == 'Cell':
            return [[1]]  # Single cell
        elif shape_name == 'Two':
            return [[1, 1]]  # Two cells in a row
        
        logger.warning(f"Unknown shape: {shape_name}, using default")
        return [[1]]  # Default single block
    
    def get_terrain_color(self, terrain_type):
        """Get color based on terrain type"""
        colors = {
            8: (100, 200, 100),  # Example color for terrain type 8
            # Add more terrain colors as needed
        }
        return colors.get(terrain_type, (100, 100, 100))  # Default gray
    
    def draw_piece(self, piece, x, y, alpha=255):
        """Draw a puzzle piece at the specified position"""
        if not piece or 'shape' not in piece:
            logger.error("Invalid piece or missing shape")
            return
            
        shape = piece['shape']
        if not shape:
            logger.error("Empty shape matrix")
            return
            
        logger.debug(f"Drawing piece at ({x}, {y}): {piece}")
        
        # Draw each block of the piece
        for row_idx, row in enumerate(shape):
            for col_idx, cell in enumerate(row):
                if cell:
                    block_x = x + col_idx * BLOCK_SIZE
                    block_y = y + row_idx * BLOCK_SIZE
                    
                    # Draw block background
                    block_rect = pygame.Rect(
                        block_x,
                        block_y,
                        BLOCK_SIZE - 1,
                        BLOCK_SIZE - 1
                    )
                    
                    # Use color based on terrain type
                    color = self.get_terrain_color(piece.get('terrain', 0))
                    pygame.draw.rect(self.screen, color, block_rect)
                    pygame.draw.rect(self.screen, BLACK, block_rect, 1)
                    
                    # Draw building ID if present
                    if piece.get('building_id'):
                        text = self.font.render(str(piece['building_id']), True, BLACK)
                        text_rect = text.get_rect(center=block_rect.center)
                        self.screen.blit(text, text_rect)
    
    def draw_game_board(self):
        """Draw the game grid and placed pieces"""
        logger.debug("=== Drawing Game Board ===")
        logger.debug(f"Game State: {self.game_state}")
        
        # Draw grid lines
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                rect = pygame.Rect(
                    x * BLOCK_SIZE,
                    TOP_MARGIN + y * BLOCK_SIZE,
                    BLOCK_SIZE - 1,
                    BLOCK_SIZE - 1
                )
                pygame.draw.rect(self.screen, BLACK, rect, 1)
        
        # Draw placed pieces if in game
        if self.game_state == GameStatus.IN_GAME.value:
            logger.debug("Game is IN_GAME state")
            if hasattr(self, 'game_manager'):
                logger.debug("Game manager exists")
                try:
                    desktop_data = json.loads(self.game_manager.get('Desktop', '[]'))
                    logger.debug(f"Desktop data: {desktop_data}")
                    for y, row in enumerate(desktop_data):
                        for x, cell in enumerate(row):
                            if cell and cell.get('owner'):
                                rect = pygame.Rect(
                                    x * BLOCK_SIZE,
                                    TOP_MARGIN + y * BLOCK_SIZE,
                                    BLOCK_SIZE - 1,
                                    BLOCK_SIZE - 1
                                )
                                pygame.draw.rect(self.screen, WHITE, rect)
                                if cell.get('building_id'):
                                    text = self.font.render(str(cell['building_id']), True, BLACK)
                                    text_rect = text.get_rect(center=rect.center)
                                    self.screen.blit(text, text_rect)
                except json.JSONDecodeError as e:
                    logger.error(f"Error decoding desktop data: {e}")
                except Exception as e:
                    logger.error(f"Error drawing board: {e}")
                    logger.error(traceback.format_exc())
            else:
                logger.debug("No game manager available")
        
    def draw(self):
        """Draw the game state"""
        logger.debug("In Draw func")
        with self.game_state_lock:
            logger.debug("\n=== Drawing Game State ===")
            logger.debug(f"Game State: {self.game_state}")
            logger.debug(f"Toolbar Pieces: {len(self.toolbar_pieces)}")
            
            # Fill background
            self.screen.fill(CREAM)
            
            # Draw game grid and board pieces
            self.draw_game_board()
            
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
                
                # 遍历所有可能的位置
                for idx in range(max_pieces):
                    # 计算grid的位置
                    grid_x = piece_spacing * (idx + 1)
                    grid_y = toolbar_y + TOOLBAR_HEIGHT // 4
                    grid_size = TOOLBAR_HEIGHT // 2
                    
                    # 绘制grid边框
                    grid_rect = pygame.Rect(grid_x - grid_size//2, grid_y, grid_size, grid_size)
                    pygame.draw.rect(self.screen, BLACK, grid_rect, 1)
                    
                    # 如果有对应的piece则绘制
                    if self.toolbar_pieces and idx < len(self.toolbar_pieces):
                        piece = self.toolbar_pieces[idx]
                        if piece and 'shape' in piece and piece['shape']:
                            # 计算piece的尺寸
                            piece_width = len(piece['shape'][0]) * BLOCK_SIZE
                            piece_height = len(piece['shape']) * BLOCK_SIZE
                            
                            # 在grid中居中
                            x = grid_x - piece_width // 2
                            y = grid_y + (grid_size - piece_height) // 2
                            
                            logger.debug(f"Drawing piece {idx}:")
                            logger.debug(f"  - Position: ({x}, {y})")
                            logger.debug(f"  - Dimensions: {piece_width}x{piece_height}")
                            logger.debug(f"  - Shape: {piece['shape']}")
                            logger.debug(f"  - Valid: {piece.get('is_valid', True)}")
                            
                            if piece.get('is_valid', True):
                                self.draw_piece(piece, x, y)
                            else:
                                self.draw_piece(piece, x, y, alpha=128)
                                
                            # 在piece上方显示ID
                            if 'id' in piece:
                                id_text = self.font.render(f"ID: {piece['id']}", True, BLACK)
                                id_rect = id_text.get_rect()
                                id_rect.centerx = grid_x
                                id_rect.bottom = grid_y - 5  # 在grid上方5像素显示
                                self.screen.blit(id_text, id_rect)
                        else:
                            logger.debug(f"Piece {idx} is invalid or missing shape")
                    else:
                        logger.debug(f"No piece for grid {idx}")
                    logger.debug("No toolbar pieces to draw")
            
            # Draw buttons based on game state
            if self.game_state != GameStatus.IN_GAME.value:
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
            if player_data.get('ready', False):
                name += ' (Ready)'
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
        """Handle button clicks"""
        for button in self.buttons:
            if button['rect'].collidepoint(pos):
                if button['text'] == 'Ready':
                    self.sendMessage(PlayerAction.Ready.value, self.username)
                elif button['text'] == 'Start':
                    self.sendMessage(PlayerAction.StartGame.value, self.username)
                elif button['text'] == 'EndTurn':
                    self.sendMessage(PlayerAction.EndTurn.value, self.username)
                break

    def run(self):
        """Main game loop"""
        logger.info("Starting game loop...")
        self.needs_redraw = True  # Force initial draw
        
        while self.running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.handle_quit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.handle_quit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        self.handle_button_click(event.pos)
                        with self.redraw_lock:
                            self.needs_redraw = True

            # Draw if needed
            with self.redraw_lock:
                if self.needs_redraw:
                    try:
                        logger.debug(f"In run: Drawing game state: {self.game_state}")
                        self.draw()
                        pygame.display.flip()
                        self.needs_redraw = False
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
                            if data['status'] == GameStatus.IN_GAME.value:
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
                                                            'ready': True  # In game, all players are ready
                                                        }
                                        
                                        # Update the game state first
                                        self.game_state = data['status']
                                        logger.info(f"Game state updated to: {self.game_state}")
                                        
                                        # Then update current player's toolbar pieces
                                        current_player_data = players_data.get(self.username, {})
                                        if isinstance(current_player_data, dict) and 'puzzles' in current_player_data:
                                            puzzles_data = current_player_data['puzzles']
                                            self.toolbar_pieces = []
                                            for puzzle_id, puzzle_info in puzzles_data.items():
                                                piece = {
                                                    'id': puzzle_id,
                                                    'shape': self.get_shape_matrix(puzzle_info.get('shape', None)),
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
                                        
                                        # Set redraw flag
                                        with self.redraw_lock:
                                            self.needs_redraw = True
                                            logger.debug("Set needs_redraw to True")
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
