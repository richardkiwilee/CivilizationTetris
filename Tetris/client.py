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
FILL_BLOCK = 7
BLOCK_COUNT = 4
GRID_WIDTH = BLOCK_COUNT * FILL_BLOCK
GRID_HEIGHT = BLOCK_COUNT * FILL_BLOCK
TOOLBAR_HEIGHT = 100
TOP_MARGIN = 50

# Screen dimensions
SCREEN_WIDTH = BLOCK_SIZE * GRID_WIDTH
SCREEN_HEIGHT = TOP_MARGIN + BLOCK_SIZE * GRID_HEIGHT + TOOLBAR_HEIGHT

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
CREAM = (255, 253, 245)
RED = (255, 0, 0)


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
        
        # Game state
        self.running = True
        self.game_state = None
        self.game_state_lock = threading.Lock()
        self.state_callback = None  # Callback for game state updates
        
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

    def draw(self):
        """Draw the game state"""
        self.screen.fill(CREAM)
        
        # Draw game grid
        if self.game_state:
            with self.game_state_lock:
                for y, row in enumerate(self.game_state):
                    for x, cell in enumerate(row):
                        rect = pygame.Rect(
                            x * BLOCK_SIZE,
                            TOP_MARGIN + y * BLOCK_SIZE,
                            BLOCK_SIZE - 1,
                            BLOCK_SIZE - 1
                        )
                        if cell and cell.get('owner'):
                            pygame.draw.rect(self.screen, WHITE, rect)
                            # Draw cell info (you can expand this based on cell data)
                            if cell.get('building_id'):
                                text = self.font.render(str(cell['building_id']), True, BLACK)
                                text_rect = text.get_rect(center=rect.center)
                                self.screen.blit(text, text_rect)
        
        pygame.display.flip()

    def run(self):
        """Main game loop"""
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.handle_quit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.handle_quit()

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
                        if isinstance(data, list):  # Game state update
                            self.update_game_state(data)
                        else:
                            print(f'Message from {message.sender}: {data}')
                    except json.JSONDecodeError:
                        print('Error decoding message:', message.body)
                    except Exception as e:
                        print('Error processing message:', str(e))
        except Exception as e:
            print('Error in message listener:', str(e))
            traceback.print_exc()
        finally:
            print('Message listener stopped')

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
