import random
import os
import xml.etree.ElementTree as ET
try:
    from .terrain import Puzzle, Terrain, ShapeHelper
except:
    from terrain import Puzzle, Terrain, ShapeHelper

# 基于28*28的设置
DEFAULT_MAP_SETTING = {
    'block_size': 7,      # 每个小区域的大小
    'block_count': 4,     # 每行和每列的方块数量
    'TerrainRatio': {
        Terrain.Plain.value: 8,       # 28*28/4 = 196块 / 7 = 28组 数字加起来是28
        Terrain.Forest.value: 8,
        Terrain.River.value: 5,
        Terrain.Farmland.value: 0,
        Terrain.Mountain.value: 5,
        Terrain.Barren.value: 2,
    }
}

class Deck:
    def __init__(self, setting=DEFAULT_MAP_SETTING):
        self.setting = setting
        self.draw_pile = list()
        self.discard_pile = list()
        self.init()

    def init(self):
        index = 1
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'Buildings.xml')
        try:
            tree = ET.parse(config_path)
            root = tree.getroot()
            
            for building in root.findall('Building'):
                # 解析基本属性
                count = int(building.get('Count', '1'))
                shape_name = building.get('shape')
                building_id = int(building.get('id'))
                
                for i in range(count):
                    puzzle = Puzzle()
                    puzzle.puzzle_id = index
                    puzzle.x = None
                    puzzle.y = None
                    puzzle.rotation = None
                    puzzle.terrainType = Terrain.Building.value
                    puzzle.shape = ShapeHelper().GetShape(shape_name)
                    puzzle.building_id = building_id
                    puzzle.building_level = 0
                    puzzle.army = 0
                    puzzle.army_owner = None
                    self.draw_pile.append(puzzle)
                    index += 1
        except Exception as e:
            print(f"Error reading building config: {e}")
        for terrain in self.setting['TerrainRatio'].keys():
            for _shape in ['I', 'J', 'L', 'O', 'S', 'T', 'Z']:
                shape = ShapeHelper().GetShape(_shape)
                puzzle = Puzzle()
                puzzle.puzzle_id = index
                puzzle.x = None
                puzzle.y = None
                puzzle.rotation = None
                puzzle.terrainType = terrain
                puzzle.shape = shape
                puzzle.building_id = None
                puzzle.building_level = None
                puzzle.army = None
                puzzle.army_owner = None
                self.draw_pile.append(puzzle)
                index += 1
        random.shuffle(self.draw_pile)


    def Draw(self) -> Puzzle:
        return self.draw_pile.pop()

    def Serialize(self):
        ret = dict()
        ret['setting'] = self.setting
        ret['draw_pile'] = [p.dump() for p in self.draw_pile]
        ret['discard_pile'] = [p.dump() for p in self.discard_pile]
        return ret

    def Deserialize(self, data):
        self.setting = data['setting']
        self.draw_pile = [load_puzzle(p) for p in data['draw_pile']]
        self.discard_pile = [load_puzzle(p) for p in data['discard_pile']]
