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

    