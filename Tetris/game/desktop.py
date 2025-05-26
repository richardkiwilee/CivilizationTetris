try:
    from Tetris.game.terrain import *   
except:
    from terrain import *

import json
class Desktop:
    def __init__(self, row, col):
        self.rows = row
        self.cols = col
        self.GameMap = [[Cell() for _ in range(self.cols)] for _ in range(self.rows)]

    def GetCell(self, x, y):
        if x < 0 or x >= self.rows or y < 0 or y >= self.cols:
            print(f'GetCell {x}, {y} out of range')
            return None
        return self.GameMap[x][y]

    def SetCell(self, x, y, cell):
        if x < 0 or x >= self.rows or y < 0 or y >= self.cols:
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
