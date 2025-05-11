from typing import List, Set, Dict, Any, Optional
import random
import traceback
from Tetris.game.desktop import Desktop
from Tetris.game.deck import Deck



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

    def GetPuzzle(self, x, y):
        # 获取坐标(x, y)上的块
        pass

    def Place(self, player, x, y, puzzle):
        # 检查块的所有地格是否都为空
        # 将块放置在坐标(x, y)
        # 设置所有相关单元格的owner
        # 返回块是否设置成功
        pass

    def ActiveBuilding(self, player, x, y):
        # 根据坐标(x, y)获得块对象
        # 如果块是一个建筑并且该建筑属于当前玩家
        # 则激活该建筑的效果
        # 返回是否激活成功
        pass

    def UpgradeBuilding(self, player, x, y, building):
        # 检查坐标(x, y)上的块是否是一个建筑
        # 如果块是一个建筑并且该建筑属于当前玩家
        # 则升级该建筑的效果
        # 返回是否升级成功
        pass

    def Attack(self, player, x1, y1, x2, y2):
        # 检查坐标(x1, y1)上的块a1是否是一个建筑
        # 检查坐标(x2, y2)上的块a2是否是一个建筑
        # 如果a1属于当前玩家 视为a1建筑向a2建筑执行一次行动
        # 返回是否执行成功
        pass