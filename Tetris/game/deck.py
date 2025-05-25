from turtle import settiltangle
from .terrain import Puzzle, Terrain, Shape
import random
from configparser import ConfigParser

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
        self.mapsize = setting['block_size'] * setting['block_size'] * setting['block_count'] *setting['block_count']
        self.draw_pile = list()
        self.discard_pile = list()
        self.init()

    def init(self):
        config = ConfigParser()
        config.read('data/Buildings.xml')
        index = 1
        for section in config.sections():
            count = int(config[section]['Count'])
            for i in range(0, count):
                puzzle = Puzzle()
                puzzle.puzzle_id = index
                puzzle.x = None
                puzzle.y = None
                puzzle.rotation = None
                puzzle.terrainType = Terrain.Building.value
                puzzle.shape = config[section]['shape']
                puzzle.building_id = int(config[section]['id'])
                puzzle.building_level = 0
                puzzle.army = 0
                puzzle.army_owner = None
                self.draw_pile.append(puzzle)
                index += 1
        for terrain in self.setting['TerrainRatio'].keys():
            for shape in [Shape.I, Shape.J, Shape.L, Shape.O, Shape.S, Shape.T, Shape.Z]:
                puzzle = Puzzle()
                puzzle.puzzle_id = index
                puzzle.x = None
                puzzle.y = None
                puzzle.rotation = None
                puzzle.terrainType = terrain
                puzzle.shape = shape.value
                puzzle.building_id = None
                puzzle.building_level = None
                puzzle.army = None
                puzzle.army_owner = None
                self.draw_pile.append(puzzle)
                index += 1
        self.draw_pile.shuffle()


    def Draw(self) -> Puzzle:
        return self.draw_pile.pop()
