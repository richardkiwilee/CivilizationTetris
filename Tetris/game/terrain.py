from enum import Enum

class Rotate(Enum):
    Zero = 0
    One = 1
    Two = 2
    Three = 3

def rotate_point(px, py, rotation):
    if rotation == Rotate.Zero.value:
        return px, py
    elif rotation == Rotate.One.value:  # 90度
        return -py, px
    elif rotation == Rotate.Two.value:  # 180度
        return -px, -py
    elif rotation == Rotate.Three.value:  # 270度
        return py, -px
    return px, py

class PuzzleType(Enum):
    Terrain = 0
    Building = 1

class Terrain(Enum):
    Building = 0    # 建筑
    Plain = 1       # 平原
    Forest = 2      # 森林
    River = 3       # 河流
    Farmland = 4    # 农田
    Mountain = 5    # 山地
    Barren = 6      # 贫瘠
    Fertile = 7     # 肥沃, 同时视为平原、森林、河流
    Urban = 8       # 城市

class Cell:
    def __init__(self, terrain, owner):
        self.terrain = terrain
        self.owner = owner

class BuildingTag(Enum):
    Production = 1          # 生产建筑
    Military = 2            # 军事建筑
    Religion = 3            # 宗教建筑
    Nobility = 4            # 贵族建筑
    Unique = 5              # 唯一建筑
    Special = 6             # 特殊建筑
    
class Shape(Enum):
    I = 1           # 4格
    J = 2           # 4格
    L = 3           # 4格
    O = 4           # 4格
    S = 5           # 4格
    T = 6           # 4格
    Z = 7           # 4格
    Corner = 10     # 3格转角
    Two = 11        # 2格
    Cell = 8        # 1格
    Rectangle6 = 9  # 6格矩形
    Rectangle8 = 10 # 8格矩形
    Line = 11       # 3格直线


class Forces(Enum):
    Normal = 0     # 不受任何克制
    Sword = 1      # 剑
    Axe = 2        # 斧
    Arrow = 3      # 箭
    Spear = 4      # 矛
    Horse = 5      # 马
    Heavy = 6      # 重装

class Puzzle:
    def __init__(self, _type: PuzzleType, shape: Shape, terrain: Terrain, tags=[]):
        self.id = 0
        self.x = 0
        self.y = 0
        self.rotation = Rotate.Zero.value
        self.name = ""
        self.type = _type
        self.shape = shape
        self.terrain = terrain
        self.tags = tags
        self.owner = None
        self.army = 0
        self.army_owner = None
        self.cells = set()
        self.activeable = False
        self.place_cost = dict()
        self.activate_cost = dict()
        self.upgrade_cost = dict()
        self.max_level = 0
        self.level = 0
        self.effect_range = 0

    def Activate(self):
        if self.terrain != Terrain.Building.value:
            return
        pass

    def Upgrade(self):
        if self.terrain != Terrain.Building.value:
            return
        pass

    def StartTurn(self):
        pass

    def EndTurn(self):
        pass

    def isBuilding(self):
        return self.terrain == Terrain.Building.value
