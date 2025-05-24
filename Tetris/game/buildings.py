from Tetris.game.player import *
from Tetris.game.terrain import *

class Building(Puzzle):
    def __init__(self, _type: PuzzleType, shape: Shape, terrain: Terrain, tags=[]):
        super().__init__(_type, shape, terrain, tags)
    
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
