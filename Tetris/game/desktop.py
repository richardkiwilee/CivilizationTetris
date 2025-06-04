try:
    from Tetris.game.terrain import *   
except:
    from terrain import *

import json
import logging
logger = logging.getLogger('desktop')
logger.setLevel(logging.DEBUG)
# 创建控制台处理器
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
# 创建格式化器
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
# 将处理器添加到日志记录器
logger.addHandler(console_handler)

class Desktop:
    def __init__(self, row, col):
        self.rows = row
        self.cols = col
        self.GameMap = [[Cell() for _ in range(self.cols)] for _ in range(self.rows)]

    def GetCell(self, x, y):
        if x < 0 or x >= self.rows or y < 0 or y >= self.cols:
            logger.error(f'GetCell {x}, {y} out of range')
            return None
        _cell = self.GameMap[y][x]
        return _cell

    def SetCell(self, x, y, cell):
        if x < 0 or x >= self.rows or y < 0 or y >= self.cols:
            logger.error(f'SetCell {x}, {y} out of range')
            return
        self.GameMap[x][y] = cell

    def Clear(self):
        self.GameMap = [[Cell() for _ in range(self.cols)] for _ in range(self.rows)]

    def Resize(self, x, y):
        self.Clear()
        self.rows = x
        self.cols = y
        self.GameMap = [[Cell() for _ in range(self.cols)] for _ in range(self.rows)]

    def Serialize(self):        # 序列化到字典
        ret = []
        for row in self.GameMap:
            ret.append([cell.dump() for cell in row])
        data = json.dumps(ret)
        return data

    def Deserialize(self, data):        # 从字典反序列化
        self.GameMap = json.loads(data)
        self.rows = len(self.GameMap)
        self.cols = len(self.GameMap[0])
