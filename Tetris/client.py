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
            {'text': 'Ready', 'rect': pygame.Rect(button_x, SCREEN_HEIGHT - TOOLBAR_HEIGHT + 20, BUTTON_WIDTH, BUTTON_HEIGHT)},
            {'text': 'Cancel', 'rect': pygame.Rect(button_x, SCREEN_HEIGHT - TOOLBAR_HEIGHT + 70, BUTTON_WIDTH, BUTTON_HEIGHT)}
        ]
        
        # Login to server
        loginResp = self.sendMessage(PlayerAction.Login.value, self.username, None, None, None, None)
        print(loginResp)
        if loginResp.status != SystemResponse.OK.value:
            print('Failed to login lobby: {}'.format(loginResp.msg))
            return
            
        # Start message listening thread
        self.listening_thread = threading.Thread(target=self.__listen_for_messages, daemon=True)
        self.listening_thread.start()
        
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

    def draw_player_slot(self, slot_index, player_data=None):
        """Draw a player slot with their information"""
        x = BLOCK_SIZE * GRID_WIDTH
        y = TOP_MARGIN + slot_index * PLAYER_SLOT_HEIGHT
        
        # Draw slot background
        slot_rect = pygame.Rect(x, y, PLAYER_SLOT_WIDTH, PLAYER_SLOT_HEIGHT)
        pygame.draw.rect(self.screen, WHITE, slot_rect)
        pygame.draw.rect(self.screen, BLACK, slot_rect, 1)
        
        if player_data:
            # Draw player name
            name_text = self.font.render(player_data.get('name', 'Unknown'), True, BLACK)
            self.screen.blit(name_text, (x + 10, y + 10))
            
            # Draw resources if available
            resources = player_data.get('resources', {})
            for i, (resource_name, _) in enumerate(RESOURCE_TYPES):
                resource_x = x + 10 + (i % 4) * (RESOURCE_ICON_SIZE + 5)
                resource_y = y + 40 + (i // 4) * (RESOURCE_ICON_SIZE + 5)
                
                # Draw resource icon
                if self.resource_images.get(resource_name):
                    self.screen.blit(self.resource_images[resource_name], (resource_x, resource_y))
                
                # Draw resource value
                value = resources.get(resource_name, 0)
                value_text = self.font.render(str(value), True, BLACK)
                self.screen.blit(value_text, (resource_x + RESOURCE_ICON_SIZE + 5, resource_y))

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
        if self.game_state:
            with self.game_state_lock:
                for y, row in enumerate(self.game_state):
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
                elif button['text'] == 'Cancel':
                    self.sendMessage(PlayerAction.Cancel.value, self.username)
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

            self.draw()
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
                            if 'users' in data:  # Player list update
                                self.update_players(data['users'])
                            if 'game_state' in data:  # Game state update
                                self.update_game_state(data['game_state'])
                    except json.JSONDecodeError:
                        print('Error decoding message:', message.body)
                    except Exception as e:
                        print('Error processing message:', str(e))
        except Exception as e:
            print('Error in message listener:', str(e))
            traceback.print_exc()
        finally:
            print('Message listener stopped')

    def update_players(self, users_data):
        """Update player slots with user data"""
        self.players.clear()
        for i, (username, data) in enumerate(users_data.items()):
            if i < PLAYER_SLOTS:
                self.players[i] = {
                    'name': username,
                    'resources': data.get('resources', {}),
                    'ready': data.get('ready', False)
                }

    def handle_quit(self):
        """Handle quit event"""
        self.running = False
        self.sendMessage(PlayerAction.Logout.value, self.username)
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
    
    client = Client(args.username, args.address, args.port)
    client.run()

if __name__ == '__main__':
    main()



def main(address='localhost', port=50051, username=None):
    chars = string.ascii_letters
    if username is None:
        username = ''.join(random.choice(chars) for _ in range(5))
    client = Client(username, address, port)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print('Bye')
