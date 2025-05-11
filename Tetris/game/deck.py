from .terrain import *
import random

DEFAULT_MAP_SETTING = {
    'row': 12,      # 地图尺寸
    'col': 12,
    'CoverRate': 1.5,   # 地图格数覆盖率
    'TerrainRatio': {
        Terrain.Plain.value: 12,       # 地面卡密度
        Terrain.Forest.value: 12,
        Terrain.River.value: 6,
        Terrain.Farmland.value: 0,
        Terrain.Mountain.value: 6,
        Terrain.Barren.value: 0,
    },
    'BuildingRatio': 0.25,       # 建筑卡生成率

}

class Deck:
    def __init__(self, setting=DEFAULT_MAP_SETTING):
        self.mapsize = setting['row'] * setting['col']
        self.draw_pile = list()
        self.discard_pile = list()
        self.init()

    def init(self):
        pass

    def Draw(self) -> Puzzle:
        pass