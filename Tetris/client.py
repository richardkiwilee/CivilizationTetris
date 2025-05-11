import time
import grpc
import threading
import traceback
import queue
import sys
import random
import string
import argparse
import json
import os
import Tetris.protocol.service_pb2 as pb2
import Tetris.protocol.service_pb2_grpc as rpc
from Tetris.game.manager import Manager
from Tetris.game.ui import RefreshScreen
import ctypes
# 定义GetAsyncKeyState函数
def getasynckeystate(key):
    return ctypes.windll.user32.GetAsyncKeyState(key)


class Client:
    def __init__(self, username: str, address='localhost', port=50051):
        self.username = username
        # 创建 gRPC 通道和存根
        channel = grpc.insecure_channel(address + ':' + str(port))
        self.stub = rpc.LobbyStub(channel)
        # 启动一个新线程监听消息
        self.running = True  # 添加运行状态标志
        retry = 0
        self.detail = False
        loginResp = self.sendMessage(LobbyAction.LOGIN.value, self.username, None, None, None, None)
        if loginResp.status != 200:
            print('Failed to login lobby: {}'.format(loginResp.msg))
            return
        self.listening_thread = threading.Thread(target=self.__listen_for_messages, daemon=True)
        self.listening_thread.start()
        # 初始化lobby
        self.sendMessage(LobbyAction.SYNC.value, self.username, None, None, None, None)
        self.input_thread = threading.Thread(target=self.add_input, daemon=True)
        self.input_thread.start()

    def add_input(self):
        # 从控制台获取输入并发送到服务器
        while self.running:
            try:
                # 等待用户输入
                command = input('> ')
                if not command:
                    continue
                # 解析命令和参数
                parts = command.strip().split()
                action = parts[0]
                arg1 = parts[1] if len(parts) > 1 else None
                arg2 = parts[2] if len(parts) > 2 else None
                arg3 = parts[3] if len(parts) > 3 else None
                arg4 = parts[4] if len(parts) > 4 else None
                arg5 = parts[5] if len(parts) > 5 else None                
                print('Command received:', action)
                if action == 'exit':
                    print('Exiting game...')
                    self.sendMessage(LobbyAction.LOGOUT.value, self.username, arg2, arg3, arg4, arg5)
                    self.running = False  # 设置运行状态为False
                    os._exit(0)  # 强制结束所有线程
                    break
                if action in ['debug', 'd']:
                    print(self.table_info)
                    continue
                if action in ['sync', 's']:
                    self.sendMessage(LobbyAction.SYNC.value, self.username, arg2, arg3, arg4, arg5)
                if action == 'detail':
                    self.detail = not self.detail
                # 根据游戏状态处理不同的命令
                if self.table_info.get('game_status') == GameStatus.SCORE.value:
                    self.sendMessage(LobbyAction.READY.value, self.username, arg2, arg3, arg4, arg5)                    
                if self.table_info.get('game_status') == GameStatus.LOBBY.value:
                    if action == LobbyAction.READY.value or action == LobbyAction.READY.value[0]:
                        self.sendMessage(LobbyAction.READY.value, self.username, arg2, arg3, arg4, arg5)
                    if action == LobbyAction.CANCEL.value or action == LobbyAction.CANCEL.value[0]:
                        self.sendMessage(LobbyAction.CANCEL.value, self.username, arg2, arg3, arg4, arg5)
                    if action == LobbyAction.START_GAME.value or action == LobbyAction.START_GAME.value[0]:
                        self.sendMessage(LobbyAction.START_GAME.value, self.username, arg2, arg3, arg4, arg5)
                if self.table_info.get('game_status') == GameStatus.GAME.value:
                    if action in ['skill', 'card']:
                        self.sendMessage(action, arg1, arg2, arg3, arg4, arg5)
                    elif action == 's':
                        self.sendMessage('skill', arg1, arg2, arg3, arg4, arg5)
                    elif action == 'c':
                        self.sendMessage('card', arg1, arg2, arg3, arg4, arg5)
                    elif action == 'p':
                        self.sendMessage('pass', arg1, arg2, arg3, arg4, arg5)
                    else:
                        print('In game, available commands: skill, card, exit')
                if self.table_info.get('game_status') == GameStatus.WAIT_PLAY.value:
                    try:
                        parts = command.strip().split()            
                        arg1 = self.CheckArg(parts[0] if len(parts) > 0 else None)
                        arg2 = self.CheckArg(parts[1] if len(parts) > 1 else None)
                        arg3 = self.CheckArg(parts[2] if len(parts) > 2 else None)
                        arg4 = self.CheckArg(parts[3] if len(parts) > 3 else None)
                        arg5 = self.CheckArg(parts[4] if len(parts) > 4 else None)
                        self.sendMessage(TurnAction.PLAY_CARD.value, arg1, arg2, arg3, arg4, arg5)
                    except Exception as ex:
                        print(ex)
            except KeyboardInterrupt:
                print('\nReceived keyboard interrupt, exiting...')
                self.sendMessage(LobbyAction.LOGOUT.value, self.username)
                self.running = False  # 设置运行状态为False
                os._exit(0)  # 强制结束所有线程
                break
            except Exception as ex:
                print('Error processing command:', str(ex))

    def __listen_for_messages(self):
        # 从服务器接收新消息并显示
        try:
            subscribeResps = self.stub.Subscribe(pb2.GeneralRequest(sender=self.username, body=json.dumps(dict())))
            subscribeResp = next(subscribeResps)
            if subscribeResp is None:
                print('Failed to subscribe game.')
                self.running = False
                os._exit(1)
                return
            print('Successfully joined the game.')
            for resp in subscribeResps:
                if not self.running:  # 检查运行状态
                    break
                self.table_info = json.loads(resp.body)
                RefreshScreen(self.username, self.table_info, self.detail)
        except grpc.RpcError as rpc_error:
            print('Stream interrupted: RPC Error -', rpc_error.code())
            traceback.print_exc()
            self.running = False
            os._exit(1)
        except Exception as ex:
            print('Stream interrupted:', str(ex))
            traceback.print_exc()
            self.running = False
            os._exit(1)

    def sendMessage(self, action, arg1=None, arg2=None, arg3=None, arg4=None, arg5=None):
        msg = {
            'action': action, 'arg1': arg1, 'arg2': arg2, 'arg3': arg3, 'arg4': arg4, 'arg5': arg5
        }
        resp = self.stub.Handle(pb2.GeneralRequest(sender=self.username, body=json.dumps(msg)))
        print('Server response: ', resp)
        return resp


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
