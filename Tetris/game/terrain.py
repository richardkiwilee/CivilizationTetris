from enum import Enum
from configparser import ConfigParser
import os
import xml.etree.ElementTree as ET
try:
    from Tetris.game.player import PlayerResource
except:
    from player import PlayerResource


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
    Unknown = 0
    Plain = 1       # 平原
    Forest = 2      # 森林
    River = 3       # 河流
    Farmland = 4    # 农田
    Mountain = 5    # 山地
    Barren = 6      # 贫瘠
    Urban = 7       # 城市
    Building = 8    # 建筑  具体建筑类型通过Building查询

class BuildingType(Enum):
    Unknown = 0
    Production = 1          # 生产建筑
    Military = 2            # 军事建筑
    Religion = 3            # 宗教建筑
    Nobility = 4            # 贵族建筑
    Unique = 5              # 唯一建筑
    Special = 6             # 特殊建筑

class BuildingTag(Enum):
    Unknown = 0
    Production = 1          # 生产建筑
    Military = 2            # 军事建筑
    Religion = 3            # 宗教建筑
    Nobility = 4            # 贵族建筑
    Unique = 5              # 唯一建筑
    Special = 6             # 特殊建筑

class ShapeHelper:
    def __init__(self):
        self.config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'Shapes.xml')
        self.shapes = dict()
        self.ReadConfig()
    
    def ReadConfig(self):
        """从 XML 配置文件中读取形状定义"""
        try:
            tree = ET.parse(self.config_path)
            root = tree.getroot()
            for shape_elem in root.findall('Shape'):
                # 解析基本属性
                name = shape_elem.find('Name').text
                shape_type = name  # 使用枚举名称获取对应的Shape枚举值
                
                # 解析网格
                grid = []
                for row in shape_elem.find('Grid').findall('Row'):
                    # 处理可能的逗号分隔的情况
                    if ',' in row.text:
                        grid.append([int(x) for x in row.text.split(',')])
                    else:
                        grid.append([int(x) for x in row.text])
                
                # 先按行后按列找到第一个1的位置作为中心点(0,0)
                center_x = -1
                center_y = -1
                found = False
                for y in range(len(grid)):  # 先遍历行
                    if found:
                        break
                    for x in range(len(grid[y])):  # 再遍历列
                        if grid[y][x] == 1:
                            center_x = x
                            center_y = y
                            found = True
                            break
                
                # 生成相对坐标（y轴向下为负）
                cells = []
                for y in range(len(grid)):
                    for x in range(len(grid[y])):
                        if grid[y][x] == 1:
                            # 计算相对于中心的偏移
                            rel_x = x - center_x
                            rel_y = center_y - y  # 注意这里是center_y - y，这样向下为负值
                            cells.append((rel_x, rel_y))
                
                # 将形状添加到字典中
                self.shapes[shape_type] = tuple(cells)
                
        except Exception as e:
            print(f"Error reading shape config: {e}")
            raise
    
    def GetShape(self, shape: str):
        """获取指定形状的相对坐标元组"""
        _ = self.shapes.get(shape, None)
        if _ is not None:   
            return _
        return None


class Forces(Enum):
    Unknown = 0
    Normal = 1     # 不受任何克制
    Light = 2      # 轻装
    Heavy = 3      # 重装
    Range = 4      # 远程


class Cell:
    def __init__(self):
        self.owner = None
        self.terrainType = Terrain.Unknown.value
        self.puzzle_id = None
        self.building_id = None

    def get(self, key):
        return getattr(self, key)

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
        self.owner = None   # 拼块所有者
        self.terrainType = Terrain.Unknown.value   # 地形类型
        self.shape = None   # 形状        
        self.building_id = None   # 建筑id 如果是None则表示这个拼块不是一个建筑
        self.building_level = None   # 建筑等级 如果是None则表示这个拼块不是一个建筑
        self.building_max_level = None   # 建筑最大等级 如果是None则表示这个拼块不是一个建筑
        self.army = 0   # 军队数量  只有这个拼块是一个建筑的情况下才可用
        self.army_owner = None   # 军队所有者  只有这个拼块是一个建筑的情况下才可用

    def isBuilding(self):
        return self.building_id is not None

    def canUpgrade(self):
        if self.building_level is None and self.isBuilding():
            self.building_level = 0
        return self.building_level < self.building_max_level

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
        if self.building_max_level:  
            ret['building_max_level'] = self.building_max_level
        if self.army:  
            ret['army'] = self.army
        if self.army_owner:  
            ret['army_owner'] = self.army_owner
        return ret

    def load(self, data):
        self.puzzle_id = data['puzzle_id']
        self.x = data['x'] if 'x' in data else None
        self.y = data['y'] if 'y' in data else None
        # 保持terrainType为数值形式，因为它本身就是枚举的value
        self.terrainType = data['terrainType'] if 'terrainType' in data else Terrain.Unknown.value
        self.shape = data['shape']
        self.rotation = data['rotation'] if 'rotation' in data else None
        self.building_id = data['building_id'] if 'building_id' in data else None
        self.building_level = data['building_level'] if 'building_level' in data else None
        self.building_max_level = data['building_max_level'] if 'building_max_level' in data else None
        self.army = data['army'] if 'army' in data else 0
        self.army_owner = data['army_owner'] if 'army_owner' in data else None

def load_puzzle(data):
    puzzle = Puzzle()
    puzzle.load(data)
    return puzzle


if __name__ == '__main__':
    shape_helper = ShapeHelper()
    shape_helper.ReadConfig()
    print(shape_helper.GetShape('Corner'))   # ((0, 0), (0, 1), (0, 2), (0, 3))
