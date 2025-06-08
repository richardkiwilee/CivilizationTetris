import time
import traceback
from concurrent import futures
import queue
import random
from enum import Enum
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
from Tetris.game.action import *
import threading
from Tetris.game.terrain import Terrain
from Tetris.game.player import PlayerResource

queues = []
# 配置日志记录器
logger = logging.getLogger('server')
logger.setLevel(logging.DEBUG)
# 创建控制台处理器
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
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
        self.status = GameStatus.LOBBY.value
        self.host = None
        self.users = dict()     # 记录当前大厅的玩家状态
        self.player_order = []  # 玩家名字列表，按加入顺序决定回合顺序
        self.current_player_index = 0
        self.seq = 0
        self.deck = None

    def StartGame(self):
        # 设置游戏状态
        self.status = GameStatus.IN_GAME.value
        # 使用已有的player_order（按加入顺序）
        for username in self.player_order:
            self.gm.AddPlayer(username)
        # 初始化游戏管理器
        self.gm.StartGame()
        # 重置当前玩家索引
        self.current_player_index = 0
        # 初始化游戏相关组件
        self.deck = self.gm.puzzle_deck

    def Handle(self, request, context):
        resp = {'type': None, 'msg': ''}
        sender = request.sender
        body = json.loads(request.body)
        logger.debug(f'Received: {body}')
        action = body.get('action')
        
        # 强制刷新功能
        if action == PlayerAction.Sync.value:
            self._broadcast()
            return self._response(SystemResponse.OK, resp)
        
        # 大厅状态
        if self.status == GameStatus.LOBBY.value:
            if action == PlayerAction.Login.value:
                username = body['arg1']
                # 第一个玩家作为房主
                if len(self.users) == 0:
                    self.host = username
                # 新玩家加入
                if username not in self.users:
                    self.users[username] = dict()
                    self.users[username]['ready'] = False
                    # 将玩家添加到玩家顺序列表
                    if username not in self.player_order:
                        self.player_order.append(username)
                    self._broadcast()
                    logger.debug(f'User {username} logined')
                    return self._response(SystemResponse.OK, resp)
                # 玩家重新连接
                else:
                    # 如果玩家不在顺序列表中（可能是由于之前的退出），重新添加
                    if username not in self.player_order:
                        self.player_order.append(username)
                    self._broadcast()
                    logger.debug(f'User {username} logined')
                    return self._response(SystemResponse.OK, resp)
            
            if action == PlayerAction.Logout.value:
                username = body['arg1']
                if username in self.users:
                    self.users.pop(username)
                    # 从玩家顺序列表中移除
                    if username in self.player_order:
                        self.player_order.remove(username)
                    
                    # 检查是否还有其他用户连接
                    if not self.users:
                        # 如果没有用户，重置房间状态
                        self.reset_room()
                    
                    self._broadcast()
                resp['msg'] = f'{username} Logout'
                logger.debug(f'User {username} logout')
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
            if sender != self.player_order[self.current_player_index]:
                self._broadcast()
                resp['msg'] = f'Not your turn, current player index: {self.current_player_index}'
                return self._response(SystemResponse.ERROR, resp) 

            if action == PlayerAction.EndTurn.value:
                self.next_player()
                self._broadcast()
                resp['msg'] = f'{sender} end turn'
                return self._response(SystemResponse.OK, resp) 
            
            if action == PlayerAction.Place.value:
                logger.info(f'{sender} place {body}')
                try:
                    # 获取玩家
                    player = self.gm.players[sender]
                    # 获取拼块
                    puzzle_id = int(body['arg2'])
                    puzzle = player.puzzles[puzzle_id]
                    # 获取放置位置和旋转角度
                    x = int(body['arg3'])
                    y = int(body['arg4'])
                    rotate = int(body['arg5'])
                    # 尝试放置
                    if self.gm.Place(player, x, y, puzzle, rotate):
                        # 放置成功，移除玩家手中的拼块
                        self.gm.PlayerRemovePuzzle(player, puzzle_id)
                        add_resource_cnt = len(self.gm.shape_helper.GetShape(puzzle.shape))
                        if puzzle.building_id is None:
                            if puzzle.terrainType == Terrain.Plain.value:
                                player.AddResource(PlayerResource.Food, add_resource_cnt)
                            elif puzzle.terrainType == Terrain.Forest.value:
                                player.AddResource(PlayerResource.Wood, add_resource_cnt)
                            elif puzzle.terrainType == Terrain.River.value:
                                player.AddResource(PlayerResource.Gold, add_resource_cnt)
                            elif puzzle.terrainType == Terrain.Farmland.value:
                                player.AddResource(PlayerResource.Food, add_resource_cnt * 2)
                            elif puzzle.terrainType == Terrain.Mountain.value:
                                player.AddResource(PlayerResource.Stone, add_resource_cnt)
                        # 如果填满了一个区域 额外获得一次奖励资源
                        _block = []
                        for cell in self.gm.GetDesktopPosition(x, y, puzzle, rotate):
                            _block.append(self.gm.GetBlockByCell(cell[0], cell[1]))
                        _block = list(set(_block))
                        block_size = self.gm.setting['block_size']
                        for _block_x, _block_y in _block:
                            terrain_count_dict = {
                                Terrain.Plain.value: 0,
                                Terrain.Forest.value: 0,
                                Terrain.River.value: 0,
                                Terrain.Farmland.value: 0,
                                Terrain.Mountain.value: 0
                            }
                            fullfill = True
                            for cell_x in range(_block_x * block_size, (_block_x + 1) * block_size):
                                for cell_y in range(_block_y * block_size, (_block_y + 1) * block_size):
                                    cell = self.gm.Desktop.GetCell(cell_x, cell_y)
                                    if cell.terrainType == Terrain.Unknown.value:
                                        fullfill = False
                                    if cell.terrainType in terrain_count_dict.keys():
                                        terrain_count_dict[cell.terrainType] += 1
                            if fullfill:
                                logger.info(f'Fullfill Block: {_block_x}, {_block_y}. Bouns: {terrain_count_dict}')
                                for terrain_type, count in terrain_count_dict.items():
                                    if terrain_type == Terrain.Plain.value:
                                        player.AddResource(PlayerResource.Food, 5 * count)
                                    elif terrain_type == Terrain.Forest.value:
                                        player.AddResource(PlayerResource.Wood, 5 * count)
                                    elif terrain_type == Terrain.River.value:
                                        player.AddResource(PlayerResource.Gold, 5 * count)
                                    elif terrain_type == Terrain.Farmland.value:
                                        player.AddResource(PlayerResource.Food, 5 * count * 2)
                                    elif terrain_type == Terrain.Mountain.value:
                                        player.AddResource(PlayerResource.Stone, 5 * count)
                            else:
                                logger.info(f'Not fullfill Block: {_block_x}, {_block_y}. Bouns: {terrain_count_dict}')
                        # 抽取新的拼块
                        self.PlayerDrawToLimit(player)
                        self.next_player()
                        self._broadcast()
                        resp['msg'] = f'{sender} placed puzzle {puzzle_id} at ({x}, {y}) with rotation {rotate}'
                    else:
                        resp['msg'] = 'Failed to place puzzle'
                        logger.error(f'Failed to place puzzle {puzzle_id} at ({x}, {y}) with rotation {rotate}')
                        self._broadcast()
                        return self._response(SystemResponse.ERROR, resp)
                except Exception as e:
                    logger.error(f'Error in Place action: {e}')
                    resp['msg'] = f'Error: {str(e)}'
                    logger.error(f'Handle Place action error: {resp}')
                    traceback.print_exc()
                    return self._response(SystemResponse.ERROR, resp)
                self._broadcast()
                return self._response(SystemResponse.OK, resp)

            if action == PlayerAction.ChangeCard.value:
                player = self.gm.players[sender]
                for puzzle_id, puzzle in list(player.puzzles.items()):
                    if puzzle.building_id is not None:
                        cost = self.gm.BuildingFactory.GetCostById(puzzle.building_id, 0)
                        if not player.ResourceEnough(cost):
                            # Remove the puzzle and draw a terrain puzzle instead
                            self.gm.PlayerRemovePuzzle(player, puzzle_id)
                self.PlayerDrawTerrainToLimit(player)
                self._broadcast()
                return self._response(SystemResponse.OK, resp)
            
            if action == PlayerAction.Active.value:
                player = self.gm.players[sender]
                puzzle_id = int(body['arg2'])
                puzzle = self.gm.puzzle_objs[puzzle_id]
                _ = self.gm.ActiveBuilding(player, puzzle)
                if _:
                    logger.info(f'{sender} activated puzzle {puzzle_id}')
                else:
                    logger.error(f'{sender} failed to activate puzzle {puzzle_id}')
                self._broadcast()
                return self._response(SystemResponse.OK, resp) 
            
            if action == PlayerAction.Upgrade.value:
                print('UpgradeBuilding?')
                player = self.gm.players[sender]
                puzzle_id = int(body['arg2'])
                print(player)
                print(puzzle_id)
                print(player.puzzles)
                puzzle = self.gm.puzzle_objs[puzzle_id]
                print(puzzle)
                print('UpgradeBuilding??')
                _ = self.gm.UpgradeBuilding(player, puzzle)
                if _:
                    logger.info(f'{sender} upgraded puzzle {puzzle_id}')
                else:
                    logger.error(f'{sender} failed to upgrade puzzle {puzzle_id}')
                self._broadcast()
                return self._response(SystemResponse.OK, resp) 
            
            if action == PlayerAction.Attack.value:
                player = self.gm.players[sender]
                puzzle_id = int(body['arg2'])
                puzzle = self.gm.puzzle_objs[puzzle_id]
                _ = self.gm.Attack(player, puzzle)
                if _:
                    logger.info(f'{sender} attacked puzzle {puzzle_id}')
                else:
                    logger.error(f'{sender} failed to attack puzzle {puzzle_id}')
                self._broadcast()
                return self._response(SystemResponse.OK, resp) 

        self._broadcast()
        resp['msg'] = 'Unexpect response'
        return self._response(SystemResponse.ERROR, resp)

    def PlayerDrawTerrainToLimit(self, player, limit=5):
        while len(player.puzzles) < limit:
            self.gm.PlayerDrawTerrain(player)

    def PlayerDrawToLimit(self, player, limit=5):
        while len(player.puzzles) < limit:
            self.gm.PlayerDraw(player)

    def get_current_player(self):
        """获取当前回合的玩家"""
        if not self.player_order:
            return None
        return self.player_order[self.current_player_index]

    def next_player(self):
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
        if sender in self.player_order:
            return sender
        return None
        
    def player_exit(self, username: str):
        """处理玩家退出"""
        # 从玩家顺序列表中移除
        if username in self.player_order:
            self.player_order.remove(username)
        
        # 如果是游戏中状态
        if self.status == GameStatus.IN_GAME.value:
            if len(self.player_order) > 0:
                # 如果退出的是当前玩家，移动到下一个玩家
                if self.current_player_index >= len(self.player_order):
                    self.current_player_index = 0
            else:
                # 如果没有玩家了，重置游戏状态
                self.status = GameStatus.LOBBY.value
        
        # 如果是大厅状态，检查是否需要更换房主
        elif self.status == GameStatus.LOBBY.value and username == self.host and len(self.users) > 0:
            # 选择新房主（第一个在线的玩家）
            self.host = next(iter(self.users.keys()))


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
            
        # Register disconnect callback
        context.add_callback(self._onDisconnectWrapper(request, context))
            
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
        return pb2.GeneralResponse(
            sequence=self.seq,
            msgtype=1,  # 1 for response
            status=status.value,
            sender='__SERVER__',
            body=json.dumps(body)
        )

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
                    ready_status[user] = _data.get('ready', False)
                data['ready_status'] = ready_status
                # logger.debug(f'Broadcast - Game Status:{data["status"]}')
                # logger.debug(f'Broadcast - Ready Status:{data["ready_status"]}')
            if data['status'] == GameStatus.IN_GAME.value:
                data['current_player_index'] = self.current_player_index
                data['players'] = self.player_order
                data['manager'] = self.gm.Serialize()
                # logger.debug(f'Broadcast - Game Status:{data["status"]}')        
                # logger.debug(f'Broadcast - Current Player Index:{data["current_player_index"]}')       
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

    def reset_room(self):
        """Reset the room to initial state"""
        self.status = GameStatus.LOBBY.value
        self.host = None
        self.current_player_index = 0
        self.gm = Manager()
        self.users = dict()     # 记录当前大厅的玩家状态
        self.player_order = []  # 玩家名字列表，按加入顺序决定回合顺序
        self.current_player_index = 0
        self.seq = 0
        self.deck = None
        logger.info('Room reset to lobby state')

    def _onDisconnectWrapper(self, request, context):
        def callback():
            try:
                username = request.sender
                if username in self.users:
                    user_data = self.users[username]
                    if 'stream' in user_data:
                        user_data['stream'].put(None)
                    self.users.pop(username)
                    self.player_exit(username)
                    # 检查是否还有其他用户连接
                    if not self.users:
                        # 如果没有用户，重置房间状态
                        logger.info('No users left, resetting room')
                        self.reset_room()                    
                    self._broadcast()
                    logger.debug(f'User {username} disconnected')
            except Exception as e:
                logger.error(f'Error in disconnect callback: {e}')
        return callback


def server(port=50051):
    logger.info('Starting server')
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=8))
    servicer = LobbyServicer()
    rpc.add_LobbyServicer_to_server(servicer, server)
    server.add_insecure_port(f'[::]:{port}')
    logger.info(f'Server started, listening on port: {port}')
    server.start()

    def cleanup():
        logger.info('Cleaning up server...')
        try:
            # First stop accepting new connections
            server.stop(0)
            
            # Close all existing client connections
            for username, user_data in list(servicer.users.items()):
                try:
                    if 'stream' in user_data:
                        user_data['stream'].put(None)
                    servicer.users.pop(username)
                except Exception as e:
                    logger.error(f'Error closing connection for {username}: {e}')
            
            # Clear all message queues
            for q in queues:
                try:
                    while not q.empty():
                        q.get_nowait()
                    q.put(None)
                except Exception as e:
                    logger.error(f'Error clearing queue: {e}')
            
            # Wait for all RPCs to complete
            server.wait_for_termination(timeout=2)
            
            logger.info('Server shutdown complete')
        except Exception as e:
            logger.error(f'Error during cleanup: {e}')
            raise

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info('Received shutdown signal')
        cleanup()
        exit()
    except Exception as e:
        logger.error(f'Server error: {e}')
        cleanup()
        exit()


if __name__ == '__main__':
    server()
