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
        self.puzzle_deck = None
        self.setting = dict()
        self.setMapSize(12, 12)
        self.buildings = dict()
        self.puzzle_objs = dict()

    def setMapSize(self, row, col):
        self.setting['map_row'] = row
        self.setting['map_col'] = col

    def StartGame(self):
        self.Desktop = Desktop(self.setting['map_row'], self.setting['map_col'])
        self.puzzle_deck = Deck()

    def dumpPlayerInfo(self) -> Dict[str, Any]:
        info = dict()
        return info

    def GetPuzzle(self, x, y) -> Optional[Puzzle]:
        if self.Desktop is None:
            return None
        cell = self.Desktop.GetCell(x, y)
        puzzle = self.puzzle_objs.get(cell.puzzle_id)
        return puzzle

    def SetPuzzle(self, x, y, puzzle: Puzzle, rotate=0):
        cell = self.Desktop.GetCell(x, y)
        cell.puzzle_id = puzzle.id

    def GetCell(self, x, y):
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
            self.puzzle_objs[puzzle.id] = puzzle
            for cell in puzzle.cells:
                # 计算旋转后的相对坐标
                rx, ry = rotate_point(cell[0], cell[1], puzzle.rotation)
                # 计算实际坐标
                ax, ay = x + rx, y + ry
                # 设置坐标
                cell = self.Desktop.GetCell(ax, ay)
                cell.puzzle_id = puzzle.id
                cell.owner = player.name
                cell.terrain = puzzle.terrain
                cell.triggered_buildings = set()
            # 放置完后 触发效果
            pass
        return True

    def GetPuzzleCells(self, x, y, puzzle: Puzzle, rotate):
        # 获得puzzle本身的格子
        cells = set()
        for cell in puzzle.cells:
            rx, ry = rotate_point(cell[0], cell[1], rotate)
            ax, ay = x + rx, y + ry
            cells.add((ax, ay))
        return cells

    def GetRangeCells(self, x, y, puzzle, rotate, n):
        # 获得n范围内的所有其他格子
        cells = set()
        # 对每一个格子计算出range的集合
        for cell in puzzle.cells:
            rx, ry = rotate_point(cell[0], cell[1], rotate)
            ax, ay = x + rx, y + ry
            for _x in range(n):
                _y = n - _x
                cells.add((ax + _x, ay + _y))
                cells.add((-1 * (ax + _x), -1 * (ay + _y)))
        cells.difference_update(self.GetPuzzleCells(x, y, puzzle, rotate))
        return cells

    def GetSameRowCol(self, x, y, puzzle, rotate):
        # 获得同行同列的所有其他格子
        cells = set()
        for cell in puzzle.cells:
            rx, ry = rotate_point(cell[0], cell[1], rotate)
            ax, ay = x + rx, y + ry
            for col in range(0, self.Desktop.cols):
                cells.add((ax, col))
            for row in range(0, self.Desktop.rows):
                cells.add((row, ay))
        cells.difference_update(self.GetPuzzleCells(x, y, puzzle, rotate))
        return cells

    def GetSurround(self, x, y, puzzle, rotate):
        # 获得包围的所有格子
        cells = self.GetRangeCells(x, y, puzzle, rotate, n=1)
        return cells

    def GetFillRowCol(self, x, y, puzzle, rotate):
        # 获得填充行列的所有格子 不排除建筑
        rows = set()    
        cols = set()
        for cell in puzzle.cells:
            rx, ry = rotate_point(cell[0], cell[1], rotate)
            ax, ay = x + rx, y + ry
            rows.add(ax)
            cols.add(ay)
        fill = {'row': set(), 'col': set()}
        for row in rows:
            for col in range(0, self.Desktop.cols):
                _cell = self.Desktop.GetCell(row, col)
                if _cell.terrain is None:
                    continue
            fill['row'].add(row)
        for col in cols:
            for row in range(0, self.Desktop.rows):
                _cell = self.Desktop.GetCell(row, col)
                if _cell.terrain is None:
                    continue
            fill['col'].add(col)
        cells = set()
        for _ in fill['row']:
            for col in range(0, self.Desktop.cols):
                cells.add((_ , col))
        for _ in fill['col']:
            for row in range(0, self.Desktop.rows):
                cells.add((row , _))
        return cells

    def GetConnectedCells(self, x, y, puzzle, rotate):
        # 获得连接的所有格子 按地形分类
        connected = dict()
        for cell in puzzle.cells:
            rx, ry = rotate_point(cell[0], cell[1], rotate)
            ax, ay = x + rx, y + ry
            _cell = self.Desktop.GetCell(ax, ay)
            if _cell and _cell.terrain:
                if _cell.terrain not in connected:
                    connected[_cell.terrain] = set()
                connected[_cell.terrain].add((ax, ay))
        return connected

    def GetAdjacentCells(self, x, y, puzzle, rotate):
        # 获得毗邻的格子
        cells = set()
        # 获取拼图所有格子的边界
        for cell in puzzle.cells:
            rx, ry = rotate_point(cell[0], cell[1], rotate)
            ax, ay = x + rx, y + ry
            # 检查上下左右四个方向
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nx, ny = ax + dx, ay + dy
                adj_cell = self.Desktop.GetCell(nx, ny)
                if adj_cell is None:
                    continue
                cells.add((nx, ny))
        cells.difference_update(self.GetPuzzleCells(x, y, puzzle, rotate))
        return cells

    def GetAdjacentPuzzle(self, x, y, puzzle, rotate):
        # 获得毗邻的板块
        puzzles = set()
        # 获取所有相邻格子
        adj_cells = self.GetAdjacentCells(x, y, puzzle, rotate)
        # 检查每个相邻格子是否属于某个拼图
        for ax, ay in adj_cells:
            cell = self.Desktop.GetCell(ax, ay)
            if cell and cell.puzzle_id is not None:
                adj_puzzle = self.GetPuzzle(ax, ay)
                if adj_puzzle:
                    puzzles.add(adj_puzzle)
        return puzzles

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