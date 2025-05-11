from enum import Enum

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


class Forces(Enum):
    Normal = 0     # 不受任何克制
    Sword = 1      # 剑
    Spear = 2      # 矛
    Heavy = 3      # 斧
    Arrow = 4      # 箭

class Puzzle:
    def __init__(self, shape: Shape, terrain: Terrain, tags=[]):
        self.shape = shape
        self.terrain = terrain
        self.tags = tags
        self.owner = None

    def Activate(self):
        if self.terrain != Terrain.Building.value:
            return
        pass

    def Upgrade(self):
        if self.terrain != Terrain.Building.value:
            return
        pass

    def EndTurn(self):
        pass