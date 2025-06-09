from typing import List, Set, Dict, Any, Optional
import random
import traceback
try:
    from Tetris.game.terrain import load_puzzle
    from Tetris.game.desktop import Desktop
    from Tetris.game.deck import Deck, DEFAULT_MAP_SETTING
    from Tetris.game.terrain import Puzzle, Terrain, ShapeHelper
    from Tetris.game.player import Player
    from Tetris.game.buildings import BuildingFactory
except:
    from terrain import load_puzzle
    from desktop import Desktop
    from deck import Deck, DEFAULT_MAP_SETTING
    from terrain import Puzzle, Terrain, ShapeHelper
    from player import Player
    from buildings import BuildingFactory
import logging

logger = logging.getLogger('manager')
logger.setLevel(logging.DEBUG)
# 创建控制台处理器
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
# 创建格式化器
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
# 将处理器添加到日志记录器
logger.addHandler(console_handler)


def rotate_point(x, y, rotate):
    if rotate == 0:
        return x, y
    elif rotate == 1:
        return y, -x
    elif rotate == 2:
        return -x, -y
    elif rotate == 3:
        return -y, x

class Manager:
    def __init__(self):
        self.shape_helper = ShapeHelper()
        self.BuildingFactory = BuildingFactory()
        self.Desktop = None
        self.puzzle_deck = None
        self.setting = DEFAULT_MAP_SETTING
        self.setMapSize(7, 4)
        self.puzzle_objs = dict()
        self.players = dict()

    def AddPlayer(self, name: str):
        player = Player()
        player.name = name
        self.players[name] = player

    def setMapSize(self, block_size, block_count):
        self.setting['block_size'] = block_size
        self.setting['block_count'] = block_count
        _1 = block_count * block_count * block_size * block_size
        _2 = _1 / 4 / 7 / 28
        if _2 == int(_2):
            _2 = int(max(int(_2), 1))
        else:
            _2 = int(_2) + 1
        self.setting['TerrainRatio'][Terrain.Plain.value] = _2 * 8
        self.setting['TerrainRatio'][Terrain.Forest.value] = _2 * 8
        self.setting['TerrainRatio'][Terrain.River.value] = _2 * 5
        self.setting['TerrainRatio'][Terrain.Farmland.value] = _2 * 0
        self.setting['TerrainRatio'][Terrain.Mountain.value] = _2 * 5
        self.setting['TerrainRatio'][Terrain.Barren.value] = _2 * 2

    def StartGame(self):
        size = self.setting['block_size'] * self.setting['block_count']
        self.Desktop = Desktop(size, size)
        self.puzzle_deck = Deck(self.setting)
        self.puzzle_deck.init()
        for player in self.players.values():
            logger.info(f'Player: {player.name} setting initial hand cards.')
            for i in range(0, 3):
                self.PlayerDrawBuilding(player)
            for i in range(0, 2):
                self.PlayerDrawTerrain(player)
        self.PlaceBaseCamp()

    def GetBaseCampPostition(self):
        rows = self.Desktop.rows
        cols = self.Desktop.cols
        
        if len(self.players) == 1:
            # Center position for single player
            return [(rows // 2, cols // 2)]
        
        if len(self.players) == 2:
            # Diagonal corners for 2 players
            return [(0, 0), (rows - 1, cols - 1)]
        
        if len(self.players) == 3:
            # Triangle formation for 3 players
            return [
                (0, 0),                    # Top left
                (rows - 1, cols // 2),      # Bottom middle
                (0, cols - 1)               # Top right
            ]
        
        if len(self.players) == 4:
            # All corners for 4 players
            return [
                (0, 0),           # Top left
                (0, cols - 1),     # Top right
                (rows - 1, 0),     # Bottom left
                (rows - 1, cols - 1)# Bottom right
            ]
        logger.error("Invalid player count: " + str(len(self.players)))
        return []

    def PlaceBaseCamp(self):
        positions = self.GetBaseCampPostition()
        logger.info("Base camp positions: " + str(positions))
        for player in self.players.values():
            pos = positions.pop()
            building = self.BuildingFactory.GetBuildingById(999)
            print(building) # {'id': 999, 'name': '大本营', 'shape': ((0, 0), (1, 0), (0, -1), (1, -1)), 'tags': ['Special', 'Unique', 'Nobility'], 'cost': {0: {}, 1: {1: 400, 0: 200}, 2: {1: 1200, 0: 600}}}
            puzzle = Puzzle()
            puzzle.puzzle_id = self.puzzle_deck.index   
            puzzle.rotation = 0
            puzzle.terrainType = Terrain.Building.value
            puzzle.shape = 'O'
            puzzle.building_id = 999
            puzzle.building_level = 0
            puzzle.army = 50
            puzzle.army_owner = player.name
            
            
            
            self.puzzle_deck.index += 1
            self.puzzle_objs[puzzle.puzzle_id] = puzzle
            self.Place(player, pos[0], pos[1], puzzle)

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
        shapes = self.shape_helper.GetShape(puzzle.shape)
        for _cell in shapes:
            # 计算旋转后的相对坐标
            rx, ry = rotate_point(_cell[0], _cell[1], rotate)
            # 计算实际坐标
            ax, ay = x + rx, y - ry
            # 检查坐标是否在地图范围内
            if ax < 0 or ax >= self.Desktop.rows or ay < 0 or ay >= self.Desktop.cols:
                return False
            # 检查该位置是否已被占用 建筑可以在己方相同的地形上加盖
            cell = self.Desktop.GetCell(ax, ay)
            if cell is None:
                logger.error(f"Check Cell Placeable fail: cell {ax}, {ay} is None")
                return False
            if cell.owner is not None:
                logger.error(f"Check Cell Placeable fail: cell {ax}, {ay} is occupied")
                return False
        # TODO: 需要一个相邻的友方领土
        return True

    def GetPuzzleCells(self, x, y, puzzle: Puzzle, rotate):
        # 获得puzzle本身的格子
        cells = set()
        shapes = self.shape_helper.GetShape(puzzle.shape)
        for _cell in shapes:
            # 计算旋转后的相对坐标
            rx, ry = rotate_point(_cell[0], _cell[1], rotate)
            # 计算实际坐标
            ax, ay = x + rx, y - ry
            # 检查坐标是否在地图范围内
            if ax < 0 or ax >= self.Desktop.rows or ay < 0 or ay >= self.Desktop.cols:
                continue
            cells.add((ax, ay))
        return cells

    def GetRangeCells(self, x, y, puzzle, rotate, n):
        # 获得n范围内的所有其他格子
        cells = set()
        shapes = self.shape_helper.GetShape(puzzle.shape)
        for _cell in shapes:
            # 计算旋转后的相对坐标
            rx, ry = rotate_point(_cell[0], _cell[1], rotate)
            # 计算实际坐标
            ax, ay = x + rx, y - ry
            # 检查坐标是否在地图范围内
            if ax < 0 or ax >= self.Desktop.rows or ay < 0 or ay >= self.Desktop.cols:
                continue
            for _x in range(n):
                _y = n - _x
                cells.add((ax + _x, ay + _y))
                cells.add((ax - _x, ay - _y))
        cells.difference_update(self.GetPuzzleCells(x, y, puzzle, rotate))
        return cells

    def GetSameRowCol(self, x, y, puzzle, rotate):
        # 获得同行同列的所有其他格子
        cells = set()
        shapes = self.shape_helper.GetShape(puzzle.shape)
        for _cell in shapes:
            # 计算旋转后的相对坐标
            rx, ry = rotate_point(_cell[0], _cell[1], rotate)
            # 计算实际坐标
            ax, ay = x + rx, y - ry
            # 检查坐标是否在地图范围内
            if ax < 0 or ax >= self.Desktop.rows or ay < 0 or ay >= self.Desktop.cols:
                continue
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

    def GetConnectedCells(self, x, y, puzzle, rotate):
        # 获得连接的所有格子 按地形分类
        connected = dict()
        shapes = self.shape_helper.GetShape(puzzle.shape)
        for _cell in shapes:
            # 计算旋转后的相对坐标
            rx, ry = rotate_point(_cell[0], _cell[1], rotate)
            # 计算实际坐标
            ax, ay = x + rx, y - ry
            # 检查坐标是否在地图范围内
            if ax < 0 or ax >= self.Desktop.rows or ay < 0 or ay >= self.Desktop.cols:
                continue
            _cell = self.Desktop.GetCell(ax, ay)
            if _cell and _cell.terrain:
                if _cell.terrain not in connected:
                    connected[_cell.terrain] = set()
                connected[_cell.terrain].add((ax, ay))
        return connected

    def GetAdjacentCells(self, x, y, puzzle, rotate):
        # 获得毗邻的格子
        cells = set()
        shapes = self.shape_helper.GetShape(puzzle.shape)
        for _cell in shapes:
            # 计算旋转后的相对坐标
            rx, ry = rotate_point(_cell[0], _cell[1], rotate)
            # 计算实际坐标
            ax, ay = x + rx, y - ry
            # 检查坐标是否在地图范围内
            if ax < 0 or ax >= self.Desktop.rows or ay < 0 or ay >= self.Desktop.cols:
                continue
            # 检查上下左右四个方向
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nx, ny = ax + dx, ay + dy
                adj_cell = self.Desktop.GetCell(nx, ny)
                if adj_cell is None:
                    continue
                cells.add((nx, ny))
        cells.difference_update(self.GetPuzzleCells(x, y, puzzle, rotate))
        return cells

    def GetBlockByCell(self, x, y):
        # 根据传入的坐标，返回该坐标所属的BLOCK区域
        block_row = x // self.setting['block_size']
        block_col = y // self.setting['block_size']
        return block_row, block_col

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

    # TODO: 这里有bug
    """ 
    在战斗逻辑上具有不公平性
    1. 玩家指定进攻目标
    2. 自动计算最近的目标
    3. 兵力可以自由移动，不拘泥于建筑
    4. 兵力移动的速度
    考虑以上几点 防守方都具有相当大的优势 缺少博弈且很难让回合数在预期区间 
    放置地块阶段与战斗阶段也割裂
    """
    def ActiveBuilding(self, player: Player, puzzle: Puzzle):
        if self.Desktop is None:
            logger.error("Desktop is None")
            return False
        if not self.Accessible(player, puzzle):
            logger.error(f"Player {player.name} is not accessible to puzzle {puzzle.id}")
            return False
        if puzzle.isBuilding() and player.ResourceEnough(puzzle.activate_cost):
            player.Cost(puzzle.activate_cost)
            logger.info(f"Player {player.name} activated puzzle {puzzle.id} success")
            return True
        logger.error(f"Player {player.name} does not have enough resources to activate puzzle {puzzle.id}")
        return False

    def UpgradeBuilding(self, player: Player, puzzle: Puzzle):
        if self.Desktop is None:
            logger.error("Desktop is None")
            return False    
        if not self.Accessible(player, puzzle):
            logger.error(f"Player {player.name} is not accessible to puzzle {puzzle.id}")
            return False
        if puzzle.isBuilding() and puzzle.canUpgrade():
            if player.ResourceEnough(puzzle.upgrade_cost):
                player.Cost(puzzle.upgrade_cost)
                puzzle.building_level += 1
                logger.info(f"Player {player.name} upgraded puzzle {puzzle.id} success")
                return True
            logger.error(f"Player {player.name} does not have enough resources to upgrade puzzle {puzzle.id}")
        logger.error(f"Puzzle {puzzle.id} is not a building or is already at max level")
        return False

    def Attack(self, player: Player, puzzle: Puzzle):
        if self.Desktop is None:
            logger.error("Desktop is None")
            return False
        if not self.Accessible(player, puzzle):
            logger.error(f"Player {player.name} is not accessible to puzzle {puzzle.id}")
            return False
        # 计算攻击对象
        # 计算克制关系
        logger.info(f"Player {player.name} attacked puzzle {puzzle.id} success")
        pass

    def GetDesktopPosition(self, x, y, puzzle: Puzzle, rotate=0):
        shapes = self.shape_helper.GetShape(puzzle.shape)
        pos = []
        for cell in shapes:
            rx, ry = rotate_point(cell[0], cell[1], rotate)
            ax, ay = x + rx, y - ry
            pos.append((ax, ay))
        return pos

    def Place(self, player: Player, x, y, puzzle: Puzzle, rotate=0):
        if self.Desktop is None:
            logger.error("Desktop is None")
            return False
        # Set the owner of the puzzle
        if self.Placeable(player, x, y, puzzle, rotate):
            puzzle.owner = player.name
        else:
            return False
        # Try to place the puzzle on the desktop
        cost = self.BuildingFactory.GetCostById(puzzle.building_id, puzzle.building_level)
        if cost is None:
            logger.error(f"Cost is None. building_id: {puzzle.building_id}, level: {puzzle.building_level}")
        if player.ResourceEnough(cost):
            player.Cost(cost)
            puzzle.x = x
            puzzle.y = y
            puzzle.rotation = rotate            
            shapes = self.shape_helper.GetShape(puzzle.shape)
            if shapes is None:
                logger.error(f"Shape is None. shape: {puzzle.shape}")
            for cell in shapes:   # type: Cell
                # 计算旋转后的相对坐标
                rx, ry = rotate_point(cell[0], cell[1], rotate)
                # 计算实际坐标 地图向下y增加所以需要旋转
                ax, ay = x + rx, y - ry
                # 设置坐标
                cell = self.Desktop.GetCell(ax, ay)
                cell.owner  = player.name
                cell.terrainType = puzzle.terrainType
                cell.puzzle_id = puzzle.puzzle_id   
                cell.building_id = puzzle.building_id
            # 放置完后 触发效果
            if puzzle.building_id is not None:
                building = self.BuildingFactory.GetBuildingById(puzzle.building_id)
                if building is not None:
                    logger.info(f'Place building {building}')
            pass
        else:
            logger.error("Resource not enough")
            return False
        return True

    def Serialize(self):
        ret = dict()
        ret['Desktop'] = self.Desktop.Serialize()
        ret['puzzle_deck'] = self.puzzle_deck.Serialize()
        ret['setting'] = self.setting
        # 序列化puzzle_objs
        ret['puzzle_objs'] = {puzzle_id: puzzle.dump() for puzzle_id, puzzle in self.puzzle_objs.items()}
        ret['players'] = {name: player.Serialize() for name, player in self.players.items()}
        return ret

    def Deserialize(self, data):
        if self.Desktop is None:
            return False
        self.Desktop.Deserialize(data)
        self.players = {name: Player().Deserialize(player) for name, player in data['players'].items()}
        return True

    def PlayerDraw(self, player: Player):
        puzzle = self.puzzle_deck.Draw()
        puzzle.owner = player.name
        player.puzzles[puzzle.puzzle_id] = puzzle

    def PlayerDrawBuilding(self, player: Player):
        puzzle = self.puzzle_deck.DrawBuilding()
        puzzle.owner = player.name
        player.puzzles[puzzle.puzzle_id] = puzzle

    def PlayerDrawTerrain(self, player: Player):
        puzzle = self.puzzle_deck.DrawTerrain()
        player.puzzles[puzzle.puzzle_id] = puzzle

    def PlayerRemovePuzzle(self, player: Player, puzzle_id):
        try:
            player.puzzles.pop(puzzle_id)
        except KeyError:
            logger.error(f"Player {player.name} remove puzzle: PuzzleId {puzzle_id} not found")        
            traceback.print_exc()


if __name__ == '__main__':
    manager = Manager()
    manager.setMapSize(4,4)
    manager.StartGame()
    manager.AddPlayer('Player1')
    manager.AddPlayer('Player2')
    manager.AddPlayer('Player3')
    manager.AddPlayer('Player4')
    puzzle = manager.puzzle_deck.Draw()     
    print(manager.Place(manager.players['Player1'], 2, 2, puzzle, rotate=1))
    print(manager.Desktop.Serialize())
