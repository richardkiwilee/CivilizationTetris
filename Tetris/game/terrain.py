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

class Terrain(Enum):
    Plain = 1       # 平原
    Forest = 2      # 森林
    River = 3       # 河流
    Farmland = 4    # 农田
    Mountain = 5    # 山地
    Barren = 6      # 贫瘠
    Urban = 7       # 城市
    Building = 8    # 建筑  具体建筑类型通过Building查询

class BuildingType(Enum):
    Production = 1          # 生产建筑
    Military = 2            # 军事建筑
    Religion = 3            # 宗教建筑
    Nobility = 4            # 贵族建筑
    Unique = 5              # 唯一建筑
    Special = 6             # 特殊建筑

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
    Light = 1      # 轻装
    Heavy = 2      # 重装
    Range = 3      # 远程


class Cell:
    def __init__(self):
        self.owner = None
        self.terrainType = None
        self.puzzle_id = None
        self.building_id = None

    def dump(self):
        ret = dict()
        if self.owner:  
            ret['owner'] = self.owner
        if self.terrainType:  
            ret['terrainType'] = self.terrainType
        if self.puzzle_id:  
            ret['puzzle_id'] = self.puzzle_id
        if self.building_id:  
            ret['building_id'] = self.building_id
        return ret

    def load(self, data):
        self.owner = data['owner']
        self.terrainType = data['terrainType']
        self.puzzle_id = data['puzzle_id']
        self.building_id = data['building_id']

def load_cell(data):
    cell = Cell()
    cell.load(data)
    return cell

class Puzzle:
    def __init__(self):
        self.puzzle_id = None   # 拼块id
        self.x = None   # 中心坐标x
        self.y = None   # 中心坐标y
        self.rotation = None   # 旋转角度

        self.terrainType = None   # 地形类型
        self.shape = None   # 形状        
        self.building_id = None   # 建筑id 如果是None则表示这个拼块不是一个建筑
        self.building_level = None   # 建筑等级 如果是None则表示这个拼块不是一个建筑
        self.army = 0   # 军队数量  只有这个拼块是一个建筑的情况下才可用
        self.army_owner = None   # 军队所有者  只有这个拼块是一个建筑的情况下才可用

    def dump(self):
        ret = dict()
        if self.puzzle_id:  
            ret['puzzle_id'] = self.puzzle_id
        if self.x:  
            ret['x'] = self.x
        if self.y:  
            ret['y'] = self.y
        if self.terrainType:
            ret['terrainType'] = self.terrainType
        if self.shape:  
            ret['shape'] = self.shape
        if self.rotation:  
            ret['rotation'] = self.rotation
        if self.building_id:  
            ret['building_id'] = self.building_id
        if self.building_level:  
            ret['building_level'] = self.building_level
        if self.army:  
            ret['army'] = self.army
        if self.army_owner:  
            ret['army_owner'] = self.army_owner
        return ret

    def load(self, data):
        self.puzzle_id = data['puzzle_id']
        self.x = data['x']
        self.y = data['y']
        self.terrainType = data['terrainType']
        self.shape = data['shape']
        self.rotation = data['rotation']
        self.building_id = data['building_id']
        self.building_level = data['building_level']
        self.army = data['army']
        self.army_owner = data['army_owner']

def load_puzzle(data):
    puzzle = Puzzle()
    puzzle.load(data)
    return puzzle