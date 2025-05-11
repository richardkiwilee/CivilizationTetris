from typing import List, Set, Dict, Any, Optional
import random
import traceback
from Tetris.game.desktop import Desktop
from Tetris.game.deck import Deck
from Tetris.game.terrain import *
from Tetris.game.player import Player

class Manager:
    def __init__(self):
        self.Desktop = None
        self.puzzles = None
        self.setting = dict()
        self.setMapSize(12, 12)

    def setMapSize(self, row, col):
        self.setting['map_row'] = row
        self.setting['map_col'] = col

    def StartGame(self):
        self.Desktop = Desktop(self.setting['map_row'], self.setting['map_col'])
        self.puzzles = Deck()

    def dumpPlayerInfo(self) -> Dict[str, Any]:
        info = dict()
        return info

    def GetPuzzle(self, x, y) -> Optional[Puzzle]:
        if self.Desktop is None:
            return None
        return self.Desktop.GetCell(x, y)

    def Accessible(self, player: Player, puzzle: Puzzle) -> bool:
        if self.Desktop is None:
            return False
        if puzzle.owner == player.name:
            return True
        if puzzle.isBuilding():
            if puzzle.army > 0 and puzzle.army_owner == player.name:
                return True
        return False

    def Placeable(self, player: Player, x, y, puzzle: Puzzle, rotate=0) -> bool:
        if self.Desktop is None:
            return False
        if puzzle.type == PuzzleType.Building.value:
            for _cell in puzzle.cells:
                # 计算旋转后的相对坐标
                rx, ry = rotate_point(_cell[0], _cell[1], rotate)
                # 计算实际坐标
                ax, ay = x + rx, y + ry
                # 检查坐标是否在地图范围内
                if ax < 0 or ax >= self.Desktop.rows or ay < 0 or ay >= self.Desktop.cols:
                    return False
                # 检查该位置是否已被占用 建筑可以在己方相同的地形上加盖
                cell = self.Desktop.GetCell(ax, ay)
                if cell is not None:
                    if cell.owner != player.name:
                        return False
                    if cell.terrain != puzzle.terrain:
                        return False

        if puzzle.type == PuzzleType.Terrain.value:
            for cell in puzzle.cells:
                # 计算旋转后的相对坐标
                rx, ry = rotate_point(cell[0], cell[1], rotate)
                # 计算实际坐标
                ax, ay = x + rx, y + ry
                # 检查坐标是否在地图范围内
                if ax < 0 or ax >= self.Desktop.rows or ay < 0 or ay >= self.Desktop.cols:
                    return False
                # 对于地形，我们只需要检查位置是否在地图范围内
        return True


    def Place(self, player: Player, x, y, puzzle: Puzzle, rotate=0):
        if self.Desktop is None:
            return False
        # Set the owner of the puzzle
        if self.Placeable(player, x, y, puzzle, rotate):
            puzzle.owner = player.name
        # Try to place the puzzle on the desktop
        if player.ResourceEnough(puzzle.place_cost):
            player.Cost(puzzle.place_cost)
            self.Desktop.PlaceObject(puzzle)    # TODO
        return True

    def ActiveBuilding(self, player: Player, x, y):
        if self.Desktop is None:
            return False
        puzzle = self.GetPuzzle(x, y)
        if not self.Accessible(player, puzzle):
            return False
        if puzzle.isBuilding() and player.ResourceEnough(puzzle.activate_cost):
            player.Cost(puzzle.activate_cost)
            puzzle.Activate()
            return True
        return False

    def UpgradeBuilding(self, player: Player, x, y, building):
        if self.Desktop is None:
            return False    
        puzzle = self.GetPuzzle(x, y)
        if not self.Accessible(player, puzzle):
            return False
        if puzzle.isBuilding() and puzzle.level < puzzle.max_level:
            if player.ResourceEnough(puzzle.upgrade_cost):
                player.Cost(puzzle.upgrade_cost)
                puzzle.Upgrade()
                return True
        return False

    def Attack(self, player, x1, y1, x2, y2):
        if self.Desktop is None:
            return False
            
        attacker = self.GetPuzzle(x1, y1)
        defender = self.GetPuzzle(x2, y2)
        if not self.Accessible(player, attacker):
            return False
        if defender is None:
            return False
        # 计算进攻路线
        # 计算克制关系
        pass