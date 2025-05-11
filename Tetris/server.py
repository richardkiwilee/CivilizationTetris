import time
import traceback
from concurrent import futures
import queue
import random
import logging
import json
from urllib.parse import uses_fragment
import grpc
from Tetris.game.action import PlayerAction, SystemResponse
from Tetris.game.player import Player
import Tetris.protocol.service_pb2 as pb2
import Tetris.protocol.service_pb2_grpc as rpc
from Tetris.game.manager import Manager
from concurrent.futures import ThreadPoolExecutor
from Tetris.action import *
import threading


queues = []
# 配置日志记录器
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# 创建控制台处理器
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
# 创建格式化器
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
# 将处理器添加到日志记录器
logger.addHandler(console_handler)

class GameStatus(Enum):
    LOBBY = 1
    IN_GAME = 2

class LobbyServicer(rpc.LobbyServicer):
    def __init__(self):
        self.gm = Manager()
        logger.info(f'Manager initialized')
        logger.info(f'Manager Poker Deck Count: {len(self.gm.deck.cards)}')
        logger.info(f'Manager Consume Deck Count: {len(self.gm.consume.cards)}')
        self.status = GameStatus.LOBBY.value
        self.host = None
        self.users = dict()     # 记录当前大厅的玩家状态
        self.player_order = list()
        self.current_player_index = 0
        self.seq = 0

    def StartGame(self):
        self.status = GameStatus.IN_GAME.value
        self.gm.StartGame()

    def Handle(self, request, context):
        resp = {'type': None, 'msg': ''}
        sender = request.sender
        body = json.loads(request.body)
        action = body.get('action')
        
        # 强制刷新功能
        if action == PlayerAction.Sync.value:
            self._broadcast()
            return self._response(SystemResponse.OK, resp)
        
        # 大厅状态
        if self.status == GameStatus.LOBBY.value:
            if action == PlayerAction.Login.value:
                username = body['arg1']
                if len(self.users) == 0:
                    self.host = username
                if username not in self.users:
                    self.users[username] = dict()
                    self.users[username]['ready'] = False
                    self._broadcast()
                    return self._response(SystemResponse.OK, resp)
                else:
                    self._broadcast()
                    return self._response(SystemResponse.OK, resp)
            
            if action == PlayerAction.Logout.value:
                username = body['arg1']
                if username in self.users:
                    self.users.pop(username)
                    self._broadcast()
                resp['msg'] = f'{username} Logout'
                return self._response(SystemResponse.OK, resp)    
            
            if action == PlayerAction.StartGame.value:
                if sender != self.host:
                    resp['msg'] = 'Only host can start game'
                    return self._response(SystemResponse.ERROR, resp)
                if not self.isAllPlayerReady():
                    resp['msg'] = 'Not all players are ready'
                    return self._response(SystemResponse.ERROR, resp)
                self.StartGame()
                self._broadcast()
                resp['msg'] = 'Game started'
                return self._response(SystemResponse.OK, resp)
            
            if action == PlayerAction.Ready.value:
                if sender in self.users:
                    self.users[sender]['ready'] = True
                    self._broadcast()
                    resp['msg'] = f'{sender} Ready'
                return self._response(SystemResponse.OK, resp)            
            
        # 游戏进行中状态
        if self.status == GameStatus.IN_GAME.value:
            # 检查是否是当前玩家的回合
            if sender != self.gm.player_order[self.gm.current_player_index].username:
                self._broadcast()
                resp['msg'] = f'Not your turn, current player index: {self.gm.current_player_index}'
                return self._response(SystemResponse.ERROR, resp) 

            if action == PlayerAction.EndTurn.value:
                self._next_player()
                self._broadcast()
                resp['msg'] = f'{sender} end turn'
                return self._response(SystemResponse.OK, resp) 
            
            if action == PlayerAction.Place.value:
                self._broadcast()
                return self._response(SystemResponse.OK, resp) 

            
            if action == PlayerAction.Active.value:
                self._broadcast()
                return self._response(SystemResponse.OK, resp) 
            
            if action == PlayerAction.Upgrade.value:
                self._broadcast()
                return self._response(SystemResponse.OK, resp) 
            
            if action == PlayerAction.Attack.value:
                self._broadcast()
                return self._response(SystemResponse.OK, resp) 

        self._broadcast()
        resp['msg'] = 'Unexpect response'
        return self._response(SystemResponse.ERROR, resp)

    def get_current_player(self) -> Any:
        """获取当前回合的玩家"""
        if not self.player_order:
            return None
        return self.player_order[self.current_player_index]

    def next_player(self) -> Any:
        """移动到下一个玩家"""
        self.current_player_index = (self.current_player_index + 1) % len(self.player_order)
        return self.get_current_player()


    def isAllPlayerReady(self):
        for k in self.users.keys():
            if not self.users[k]['ready']:
                return False
        return True

    def resetPlayerReadyStatus(self):
        for user in self.users.values():
            user['ready'] = False

    def getPlayerFromSender(self, sender: str):
        for player in self.gm.player_order:
            if player.username == sender:
                return player
        return None


    def Subscribe(self, request, context):
        """
        Handle client subscription to game state updates
        """
        # Create a queue for this client's messages
        message_queue = queue.Queue()
        
        # Add the client to our users with their stream queue
        if request.sender not in self.users:
            self.users[request.sender] = {'name': request.sender, 'stream': message_queue}
        else:
            self.users[request.sender]['stream'] = message_queue
            
        # Send initial game state
        self._broadcast()
        
        try:
            while True:
                # Wait for messages in the queue
                message = message_queue.get()
                if message is None:  # Check for termination signal
                    break
                yield message
        except Exception as e:
            logger.error(f"Error in subscription stream for {request.sender}: {e}")
            traceback.print_exc()
        finally:
            # Cleanup when client disconnects
            if request.sender in self.users:
                if 'stream' in self.users[request.sender]:
                    del self.users[request.sender]['stream']

    def _response(self, status, body):
        return pb2.GeneralResponse(self.seq, msgtype='response', status=status.value, sender='__SERVER__', 
        body=json.dumps(body))

    def Broadcast(self, info):
        return pb2.Broadcast(sequence=self.seq, msgtype=200, 
                            status=200, sender='SYSTEM',
                            body=json.dumps(info))

    def _broadcast(self):
        try:
            self.seq += 1
            data = dict()
            data['status'] = self.status
            if data['status'] == GameStatus.LOBBY.value:
                ready_status = dict()
                for user, _data in self.users.items():
                    ready_status[user] = _data['ready']
                data['ready_status'] = ready_status
            if data['status'] == GameStatus.IN_GAME.value:
                data['current_player_index'] = self.gm.current_player_index
                data['players'] = [p.to_dict() for p in self.gm.player_order]
                data['public_cards'] = [c.to_dict() for c in self.gm.public_cards]
                data['last_used_cards'] = [c.to_dict() for c in self.gm.last_used_cards]
                data['deck'] = self.gm.deck.dump()
        except Exception as ex:
            logger.error(f'Error in broadcast: {ex}')
            traceback.print_exc()
        try:
            _obj = pb2.Broadcast(
                sequence=self.seq,
                msgtype=0,
                status=200,
                sender='__SYSTEM__',
                body=json.dumps(data)
            )
            for user in self.users:
                if 'stream' in self.users[user]:
                    self.users[user]['stream'].put(_obj)
            return data
        except Exception as e:
            logger.error(f'Error in broadcast: {e}')
            logger.error(f'{data}')
            traceback.print_exc()

    def _onDisconnectWrapper(self, request, context):
        def callback():
            curUser = request.name
            self._broadcast()
            del curUser['stream']
            self.gm.player_exit(curUser['name'])
        return callback


def server(port=50051):
    logger.info('Starting server')
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=8))
    rpc.add_LobbyServicer_to_server(LobbyServicer(), server)
    server.add_insecure_port(f'[::]:{port}')
    logger.info('Server started')
    server.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info('Exiting')
        # to unblock all queues
        for q in queues:
            q.put(None)
        server.stop(0)


if __name__ == '__main__':
    server()
