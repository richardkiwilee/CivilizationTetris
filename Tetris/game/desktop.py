from Tetris.game.terrain import *

class Desktop:
    def __init__(self, row, col):
        self.rows = row
        self.cols = col
        self.GameMap = [[None] * self.cols] * self.rows

    def GetCell(self, x, y):
        if x < 0 or x >= self.rows or y < 0 or y >= self.cols:
            return None
        return self.GameMap[x][y]

    def SetCell(self, x, y, cell):
        if x < 0 or x >= self.rows or y < 0 or y >= self.cols:
            return
        self.GameMap[x][y] = cell

    def Clear(self):
        for x in range(self.rows):
            for y in range(self.cols):
                self.GameMap[x][y] = None

    def Resize(self, x, y):
        self.Clear()
        self.rows = x
        self.cols = y
        self.GameMap = [[None] * self.cols] * self.rows

    def Serialize(self):        # 序列化到字典
        data = {
            'rows': self.rows,
            'cols': self.cols,
        }
        return data

    def Deserialize(self, data):        # 从字典反序列化
        self.Clear()
        self.rows = data['rows']
        self.cols = data['cols']
    