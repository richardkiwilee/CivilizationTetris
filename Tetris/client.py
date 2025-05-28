import time
import grpc
import threading
import traceback
import sys
import json
import pygame
import argparse
from Tetris.game.action import PlayerAction, SystemResponse
import Tetris.protocol.service_pb2 as pb2
import Tetris.protocol.service_pb2_grpc as rpc
from enum import Enum

from Tetris.server import GameStatus

# Initialize Pygame
pygame.init()
pygame.font.init()

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

# Colors
WHITE = (255, 255, 255)  # 玩家信息栏背景
BLACK = (0, 0, 0)    # 文字颜色
CREAM = (255, 253, 245)  # 游戏区域背景色
RED = (255, 0, 0)    # 无效放置提示


class Client:
    def __init__(self, username: str, address='localhost', port=50051):
        self.username = username
        # 创建 gRPC 通道和存根
        channel = grpc.insecure_channel(address + ':' + str(port))
        self.stub = rpc.LobbyStub(channel)
        
        # Initialize Pygame window
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(f'Civilization Tetris - {username}')
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('simhei', 24)
        
        # Load resources
        self.resource_images = self.load_resource_images()
        
        # Game state
        self.running = True
        self.game_state = None
        self.game_state_lock = threading.Lock()
        self.state_callback = None  # Callback for game state updates
        self.players = {}
        
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
        
        # Initialize lobby
        self.sendMessage(PlayerAction.Sync.value, self.username, None, None, None, None)

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
                print(f'Warning: Could not load image for {resource_name}: {e}')
                images[resource_name] = None
        return images

    def get_shape_matrix(self, shape_name):
        """Convert shape name to shape matrix"""
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
        # Add more shapes as needed
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
            return
            
        shape = piece['shape']
        color = self.get_terrain_color(piece.get('terrain', 0))
        
        # Create a surface for the piece with alpha channel
        piece_width = len(shape[0]) * BLOCK_SIZE
        piece_height = len(shape) * BLOCK_SIZE
        piece_surface = pygame.Surface((piece_width, piece_height), pygame.SRCALPHA)
        
        # Draw each block of the piece
        for row_idx, row in enumerate(shape):
            for col_idx, cell in enumerate(row):
                if cell:
                    block_rect = pygame.Rect(
                        col_idx * BLOCK_SIZE,
                        row_idx * BLOCK_SIZE,
                        BLOCK_SIZE - 1,
                        BLOCK_SIZE - 1
                    )
                    # Apply alpha to the color
                    block_color = (*color, alpha)
                    pygame.draw.rect(piece_surface, block_color, block_rect)
                    
        # Draw the piece surface on the screen
        self.screen.blit(piece_surface, (x, y))
    
    def draw(self):
        """Draw the game state"""
        # Fill background
        self.screen.fill(CREAM)
        
        # Draw toolbar background
        toolbar_y = TOP_MARGIN + GRID_HEIGHT * BLOCK_SIZE
        pygame.draw.rect(self.screen, WHITE,
                       (0, toolbar_y, SCREEN_WIDTH, TOOLBAR_HEIGHT))
        
        # Draw player slots
        for i in range(PLAYER_SLOTS):
            if i in self.players and self.players[i]:
                self.draw_player_slot(i, self.players[i])
            else:
                self.draw_player_slot(i, None)
        print(f'game_state: {self.game_state}')
        # Handle different game states
        if self.game_state == GameStatus.IN_GAME.value:
            print('toolbar_pieces: ', self.toolbar_pieces)
            # Draw toolbar pieces in the left side
            available_width = BLOCK_SIZE * GRID_WIDTH
            if self.toolbar_pieces:
                piece_spacing = available_width // (len(self.toolbar_pieces) + 1)
                for idx, piece in enumerate(self.toolbar_pieces):
                    print(f'idx: {idx}, piece: {piece}')
                    x = piece_spacing * (idx + 1) - (len(piece['shape'][0]) * BLOCK_SIZE) // 2
                    y = toolbar_y + (TOOLBAR_HEIGHT - len(piece['shape']) * BLOCK_SIZE) // 2
                    
                    if piece.get('is_valid', True):  # Default to True if not specified
                        self.draw_piece(piece, x, y)
                    else:
                        self.draw_piece(piece, x, y, alpha=128)
        else:
            # Draw Ready/Start button in lobby
            for button in self.buttons:
                pygame.draw.rect(self.screen, BLACK, button['rect'], 2)
                text = self.font.render(button['text'], True, BLACK)
                text_rect = text.get_rect(center=button['rect'].center)
                self.screen.blit(text, text_rect)
        
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

    def draw(self):
        """Draw the game state"""
        self.screen.fill(CREAM)
        
        # Draw game grid
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                rect = pygame.Rect(
                    x * BLOCK_SIZE,
                    TOP_MARGIN + y * BLOCK_SIZE,
                    BLOCK_SIZE - 1,
                    BLOCK_SIZE - 1
                )
                pygame.draw.rect(self.screen, BLACK, rect, 1)
        
        # Draw game state if available
        if self.game_state == GameStatus.IN_GAME.value:
            with self.game_state_lock:
                # 从服务器获取的游戏状态应该在manager中
                if hasattr(self, 'game_manager'):
                    try:
                        desktop_data = json.loads(self.game_manager.get('Desktop', '[]'))
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
                        print(f'Error decoding desktop data: {e}')
        
        # Draw player slots
        for i in range(PLAYER_SLOTS):
            self.draw_player_slot(i, self.players.get(i))
        
        # Draw buttons
        for button in self.buttons:
            pygame.draw.rect(self.screen, WHITE, button['rect'])
            pygame.draw.rect(self.screen, BLACK, button['rect'], 1)
            text = self.font.render(button['text'], True, BLACK)
            text_rect = text.get_rect(center=button['rect'].center)
            self.screen.blit(text, text_rect)
        
        pygame.display.flip()

    def handle_button_click(self, pos):
        """Handle button clicks"""
        for button in self.buttons:
            if button['rect'].collidepoint(pos):
                if button['text'] == 'Ready':
                    self.sendMessage(PlayerAction.Ready.value, self.username)
                elif button['text'] == 'Start':
                    self.sendMessage(PlayerAction.StartGame.value, self.username)
                break

    def run(self):
        """Main game loop"""
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.handle_quit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.handle_quit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        self.handle_button_click(event.pos)

            try:
                self.draw()
            except Exception as e:
                print(f"Error drawing game state: {e}")
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
                                if self.username == list(data['ready_status'].keys())[0]:
                                    # Check if all players are ready
                                    all_ready = all(is_ready for is_ready in data['ready_status'].values())
                                    self.buttons[0]['text'] = 'Start' if all_ready else 'Ready'
                            if data['status'] == GameStatus.IN_GAME.value:
                                print(f'Receive IN_GAME Message: {data.keys()}')
                                self.update_game_state(data['status'])
                                # 保存游戏管理器状态
                                if 'manager' in data and 'players' in data['manager']:
                                    self.game_manager = data['manager']
                                    players_data = data['manager']['players']
                                    print(f'players_data: {players_data}')                                    
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
                    except json.JSONDecodeError:
                        print('Error decoding message:', message.body)
                        traceback.print_exc()
                    except Exception as e:
                        print('Error processing message:', str(e))
                        traceback.print_exc()
        except Exception as e:
            print('Error in message listener:', str(e))
            traceback.print_exc()
        finally:
            print('Message listener stopped')

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
            print(f'Error during cleanup: {e}')
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
            print(f'Error sending message: {e}')
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
        client = Client(args.username, args.address, args.port)
        client.run()
    except KeyboardInterrupt:
        print('\nReceived shutdown signal')
        if client:
            client.handle_quit()
    except Exception as e:
        print(f'Error: {e}')
        traceback.print_exc()
        if client:
            client.handle_quit()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\nReceived shutdown signal')
        if client:
            client.handle_quit()
