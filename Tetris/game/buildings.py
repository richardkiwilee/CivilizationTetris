from Tetris.game.player import *
from Tetris.game.terrain import *


class Mercenary_01(Puzzle):
    def __init__(self):
        super().__init__(PuzzleType.Building, Shape.L, Terrain.Plain,
                         tags=[BuildingTag.Military])
        self.name = "雇佣兵营地1"    
        self.effect_range = 2
        self.upgrade_cost = {
        }
    
    def Activate(self):
        # 驻兵15斧
        pass

class Mercenary_02(Puzzle):
    def __init__(self):
        super().__init__(PuzzleType.Building, Shape.Z, Terrain.Plain,
                         tags=[BuildingTag.Military])
        self.name = "雇佣兵营地2"    
        self.effect_range = 2
        self.upgrade_cost = {
        }
    
    def Activate(self):
        # 驻兵15斧
        pass

class Mercenary_03(Puzzle):
    def __init__(self):
        super().__init__(PuzzleType.Building, Shape.J, Terrain.Plain,
                         tags=[BuildingTag.Military])
        self.name = "雇佣兵营地3"    
        self.effect_range = 2
        self.upgrade_cost = {
        }
    
    def Activate(self):
        # 驻兵15剑
        pass


class Building_001(Puzzle):
    def __init__(self):
        super().__init__(PuzzleType.Building, Shape.Cell, Terrain.Plain, 
                        tags=[BuildingTag.Military])
        self.name = "瞭望塔"    
        self.effect_range = 2
        self.upgrade_cost = {
            2: {PlayerResource.Food: 250, PlayerResource.Wood: 250},
            3: {PlayerResource.Food: 400, PlayerResource.Wood: 400},
        }

    def Activate(self):
        # 范围2/2/3内每有一个平原 征召1/2/3箭 每有一个农田 征召3/3/5箭
        pass

class Building_002(Puzzle):
    def __init__(self):
        super().__init__(PuzzleType.Building, Shape.Line, Terrain.Urban,
                         tags=[BuildingTag.Production])
        self.name = "镇子"    
        self.upgrade_cost = {
            2: {PlayerResource.Wood: 50, PlayerResource.Stone: 100, PlayerResource.Gold: 100},
            3: {PlayerResource.Wood: 100, PlayerResource.Stone: 150, PlayerResource.Gold: 150}
        }
    
    def Activate(self):
        # 探索时收益增加75%
        pass

class Building_003(Puzzle):
    def __init__(self):
        super().__init__(PuzzleType.Building, Shape.Cell, Terrain.Farmland,
                         tags=[BuildingTag.Production])
        self.name = "镇长居所"    
        self.upgrade_cost = {
            2: {PlayerResource.Wood: 100, PlayerResource.Wood: 100},
            3: {PlayerResource.Wood: 150, PlayerResource.Wood: 150}
        }
    
    def Activate(self):
        # 每与一个生产建筑或农田相连, 征收6/9/12金币
        pass

class Building_004(Puzzle):
    def __init__(self):
        super().__init__(PuzzleType.Building, Shape.Two, Terrain.Farmland,
                         tags=[BuildingTag.Military, BuildingTag.Production])
        self.name = "防匪农场"    
        self.effect_range = 2
        self.upgrade_cost = {
            2: {PlayerResource.Wood: 200},
            3: {PlayerResource.Wood: 350},
        }
    
    def Activate(self):
        # 范围1/2/3内的平原变成农田 提供驻兵5/10/15
        pass

class Building_005(Puzzle):
    def __init__(self):
        super().__init__(PuzzleType.Building, Shape.Two, Terrain.Farmland,
                         tags=[BuildingTag.Military, BuildingTag.Production])
        self.name = "防匪农场"    
        self.effect_range = 2
        self.upgrade_cost = {
            2: {PlayerResource.Wood: 200},
            3: {PlayerResource.Wood: 350},
        }
    
    def Activate(self):
        # 范围1/2/3内的平原变成农田 提供驻兵5/10/15
        pass

class Building_006(Puzzle):
    def __init__(self):
        super().__init__(PuzzleType.Building, Shape.Cell, Terrain.Urban,
                         tags=[BuildingTag.Military, BuildingTag.Production, BuildingTag.Unique])
        self.name = "钟楼"    
        self.upgrade_cost = {
            2: {PlayerResource.Citizen: 50},
            3: {PlayerResource.Citizen: 50},
            4: {PlayerResource.Citizen: 100},
            5: {PlayerResource.Citizen: 150},
            6: {PlayerResource.Citizen: 150},
            7: {PlayerResource.Citizen: 200, PlayerResource.Stone: 50},
            8: {PlayerResource.Citizen: 250, PlayerResource.Stone: 50},
            9: {PlayerResource.Citizen: 250, PlayerResource.Stone: 50},
            10: {PlayerResource.Citizen: 300, PlayerResource.Stone: 100},
        }
    
    def Activate(self):
        # 驻兵5/10/15/20/25/30/35/40/45/50
        # 提供2/ 2/ 2/ 3/ 3/ 3/ 4/ 4/ 4/ 5粮食
        # 提供2/ 2/ 2/ 3/ 3/ 3/ 4/ 4/ 4/ 5木头
        # 提供2/ 2/ 2/ 3/ 3/ 3/ 4/ 4/ 4/ 5石头
        # 提供2/ 2/ 2/ 3/ 3/ 3/ 4/ 4/ 4/ 5金币
        # 每个相连的城市单元格提供1/ 1/ 1/ 2/ 2/ 2/ 3/ 3/ 3/ 4市民
        # 特殊升级规则 需要满足范围内均是城区单元格
        pass

class Building_007(Puzzle):
    def __init__(self):
        super().__init__(PuzzleType.Building, Shape.Two, Terrain.Urban,
                         tags=[BuildingTag.Production])
        self.name = "闹市"    
        self.effect_range = 2
        self.upgrade_cost = {
            2: {PlayerResource.Wood: 50, PlayerResource.Food: 50},
            3: {PlayerResource.Wood: 200, PlayerResource.Food: 200, PlayerResource.Stone: 50},
        }
    
    def Activate(self):
        # 范围1/2/3内的平原和森林变成城市单元格
        pass

class Buidling_008(Puzzle):
    def __init__(self):
        super().__init__(PuzzleType.Building, Shape.Corner, Terrain.Urban,
                         tags=[BuildingTag.Production])
        self.name = "集市"    
        self.effect_range = 2
        self.upgrade_cost = {
            2: {PlayerResource.Wood: 150},
            3: {PlayerResource.Wood: 250},
        }
    
    def Activate(self):
        # 每个相连的街坊单元格提供5/7/10粮食
        pass

class Building_009(Puzzle):
    def __init__(self):
        super().__init__(PuzzleType.Building, Shape.Line, Terrain.Urban,
                         tags=[BuildingTag.Production])
        self.name = "仓库"    
        self.effect_range = 2
        self.upgrade_cost = {
            2: {PlayerResource.Food: 150},
            3: {PlayerResource.Food: 250},
        }
    
    def Activate(self):
        # 每个相连的街坊单元格提供5/7/10木头
        pass

class Building_010(Puzzle):
    def __init__(self):
        super().__init__(PuzzleType.Building, Shape.O, Terrain.Plain,
                         tags=[BuildingTag.Military, BuildingTag.Unique])
        self.name = "骑士堡"    
        self.effect_range = 2
        self.upgrade_cost = {
            2: {PlayerResource.Wood: 200, PlayerResource.Food: 200, PlayerResource.Gold: 100},
            3: {PlayerResource.Stone: 150, PlayerResource.Food: 300, PlayerResource.Gold: 250},
        }
    
    def Activate(self):
        # 提供信仰1/2/3 最小相连区域的每个单元格提供1/2/3箭
        pass

class Building_011(Puzzle):
    def __init__(self):
        super().__init__(PuzzleType.Building, Shape.Cell, Terrain.Plain,
                         tags=[BuildingTag.Production])
        self.name = "随军牧师驻地"    
        self.effect_range = 2
        self.upgrade_cost = {
            2: {PlayerResource.Wood: 100, PlayerResource.Food: 100, PlayerResource.Gold: 50},
            3: {PlayerResource.Wood: 100, PlayerResource.Stone: 50, PlayerResource.Gold: 150},
        }
    
    def Activate(self):
        # 如果毗邻宗教建筑 获得总计10/20/30的粮食、木头、石头
        pass

class Building_012(Puzzle):
    def __init__(self):
        super().__init__(PuzzleType.Building, Shape.Corner, Terrain.Plain,
                         tags=[BuildingTag.Production])
        self.name = "墓地"    
        self.effect_range = 2
        self.upgrade_cost = {
            2: {PlayerResource.Wood: 50, PlayerResource.Gold: 100},
            3: {PlayerResource.Wood: 150, PlayerResource.Gold: 100},
        }
    
    def Activate(self):
        # 消耗1/3/5信仰信仰 获得8/8/8倍的粮食、木头、石头
        pass

class Building_013(Puzzle):
    def __init__(self):
        super().__init__(PuzzleType.Building, Shape.Cell, Terrain.Plain,
                         tags=[BuildingTag.Production])
        self.name = "十字军哨所"    
        self.effect_range = 2
        self.upgrade_cost = {
            2: {PlayerResource.Wood: 100, PlayerResource.Food: 100, PlayerResource.Gold: 100},
            3: {PlayerResource.Food: 200, PlayerResource.Gold: 200}
        }
    
    def Activate(self):
        # 每与1种环境毗邻 获得15/25/35的粮食、木头、石头 驻兵5/10/15
        pass

class Building_014(Puzzle):
    def __init__(self):
        super().__init__(PuzzleType.Building, Shape.Two, Terrain.Forest,
                         tags=[BuildingTag.Production, BuildingTag.Military])
        self.name = "狩猎木屋"    
        self.effect_range = 2
        self.upgrade_cost = {
            2: {PlayerResource.Wood: 300},
            3: {PlayerResource.Food: 150, PlayerResource.Wood: 350}
        }
    
    def Activate(self):
        # 每与一个森林单元格相连 征召2/3/4斧 获得3/6/9粮食
        pass

class Building_015(Puzzle):
    def __init__(self):
        super().__init__(PuzzleType.Building, Shape.Cell, Terrain.Farmland,
                         tags=[BuildingTag.Production])
        self.name = "农场"    
        self.effect_range = 2
        self.upgrade_cost = {
            2: {PlayerResource.Wood: 100},
            3: {PlayerResource.Food: 100, PlayerResource.Wood: 100}
        }
    
    def Activate(self):
        # 范围1/2/3的平原变成农田
        pass

class Building_016(Puzzle):
    def __init__(self):
        super().__init__(PuzzleType.Building, Shape.Cell, Terrain.Forest,
                         tags=[BuildingTag.Production])
        self.name = "伐木场"    
        self.effect_range = 2
        self.upgrade_cost = {
            2: {PlayerResource.Food: 150},
            3: {PlayerResource.Food: 200}
        }
    
    def Activate(self):
        # 范围2/2/3的森林变成平原并获得8/12/12木头
        pass

class Building_017(Puzzle):
    def __init__(self):
        super().__init__(PuzzleType.Building, Shape.Two, Terrain.Forest,
                         tags=[BuildingTag.Production])
        self.name = "伐木营地"    
        self.effect_range = 2
        self.upgrade_cost = {
            2: {PlayerResource.Food: 150},
            3: {PlayerResource.Food: 200}
        }
    
    def Activate(self):
        # 每与一个森林单元格相连 获得3/5/7木头
        pass

class Building_018(Puzzle):
    def __init__(self):
        super().__init__(PuzzleType.Building, Shape.Corner, Terrain.Mountain,
                         tags=[BuildingTag.Production])
        self.name = "采石场"    
        self.effect_range = 2
        self.upgrade_cost = {
            2: {PlayerResource.Food: 100, PlayerResource.Gold: 50},
            3: {PlayerResource.Food: 100, PlayerResource.Gold: 100}
        }
    
    def Activate(self):
        # 每与一个山地单元格相连 获得20/30/40石头
        pass

class Building_019(Puzzle):
    def __init__(self):
        super().__init__(PuzzleType.Building, Shape.Corner, Terrain.Forest,
                         tags=[BuildingTag.Military])
        self.name = "游骑兵基地"    
        self.effect_range = 2
        self.upgrade_cost = {
            2: {PlayerResource.Wood: 400},
            3: {PlayerResource.Wood: 700}
        }
    
    def Activate(self):
        # 每与一个森林单元格相连 征召3/5/7箭
        pass

class Building_020(Puzzle):
    def __init__(self):
        super().__init__(PuzzleType.Building, Shape.Two, Terrain.Forest,
                         tags=[BuildingTag.Military])
        self.name = "木制堡垒"    
        self.effect_range = 2
        self.upgrade_cost = {
            2: {PlayerResource.Wood: 250, PlayerResource.Food: 150},
            3: {PlayerResource.Wood: 250, PlayerResource.Food: 250, PlayerResource.Gold: 150}
        }
    
    def Activate(self):
        # 驻兵10/15/20 将毗邻的森林单元格变成平原 每个成功转化获得3/4/5剑
        pass

class Building_021(Puzzle):
    def __init__(self):
        super().__init__(PuzzleType.Building, Shape.Two, Terrain.Mountain,
                         tags=[BuildingTag.Military])
        self.name = "哨所"    
        self.effect_range = 2
        self.upgrade_cost = {
            2: {PlayerResource.Wood: 300, PlayerResource.Stone: 100},
            3: {PlayerResource.Wood: 350, PlayerResource.Stone: 200}
        }
    
    def Activate(self):
        # 每与1个山地puzzle相邻 征召10/15/20剑
        pass

class Building_022(Puzzle):
    def __init__(self):
        super().__init__(PuzzleType.Building, Shape.O, Terrain.Mountain,
                         tags=[BuildingTag.Military])
        self.name = "砌石堡垒"    
        self.effect_range = 2
        self.upgrade_cost = {
            2: {PlayerResource.Wood: 150, PlayerResource.Stone: 150},
            3: {PlayerResource.Wood: 250, PlayerResource.Stone: 250}
        }
    
    def Activate(self):
        # 同行同列的每个山地puzzle 驻兵7/10/12箭
        pass

class Building_023(Puzzle):
    def __init__(self):
        super().__init__(PuzzleType.Building, Shape.Cell, Terrain.Mountain,
                         tags=[BuildingTag.Production])
        self.name = "碎石厂"    
        self.effect_range = 2
        self.upgrade_cost = {
            2: {PlayerResource.Wood: 100, PlayerResource.Gold: 50},
            3: {PlayerResource.Wood: 100, PlayerResource.Gold: 100}
        }
    
    def Activate(self):
        # 行同列的每个建筑 产出20/30/40石头
        pass

class Building_024(Puzzle):
    def __init__(self):
        super().__init__(PuzzleType.Building, Shape.Cell, Terrain.Mountain,
                         tags=[BuildingTag.Military])
        self.name = "老楼"    
        self.effect_range = 2
        self.upgrade_cost = {
            2: {PlayerResource.Wood: 100, PlayerResource.Food: 250},
            3: {PlayerResource.Wood: 150, PlayerResource.Food: 300, PlayerResource.Gold: 150}
        }
    
    def Activate(self):
        # 范围2内的每个山地puzzle 驻兵5/7/10剑 如果被山地包围 额外获得30/40/50剑
        pass

class Building_025(Puzzle):
    def __init__(self):
        super().__init__(PuzzleType.Building, Shape.Two, Terrain.Plain,
                         tags=[BuildingTag.Production])
        self.name = "路边旅馆"    
        self.effect_range = 2
        self.upgrade_cost = {
            2: {PlayerResource.Food: 150},
            3: {PlayerResource.Food: 150, PlayerResource.Wood: 100}
        }
    
    def Activate(self):
        # 范围2/3/3内的每个环境单元格获得2/2/3金币
        pass

class Building_026(Puzzle):
    def __init__(self):
        super().__init__(PuzzleType.Building, Shape.Two, Terrain.Plain,
                         tags=[BuildingTag.Military])
        self.name = "民兵基地"    
        self.effect_range = 2
        self.upgrade_cost = {
            2: {PlayerResource.Wood: 150, PlayerResource.Food: 150, PlayerResource.Gold: 200},
            3: {PlayerResource.Wood: 250, PlayerResource.Food: 250, PlayerResource.Gold: 300}
        }
    
    def Activate(self):
        # 范围2/2/3内的每个生产建筑 驻兵10/15/20箭
        pass

class Building_027(Puzzle):
    def __init__(self):
        super().__init__(PuzzleType.Building, Shape.Cell, Terrain.Plain,
                         tags=[BuildingTag.Production])
        self.name = "牧羊人小屋"    
        self.effect_range = 2
        self.upgrade_cost = {
            2: {PlayerResource.Wood: 50, PlayerResource.Stone: 50},
            3: {PlayerResource.Wood: 100, PlayerResource.Stone: 50}
        }
    
    def Activate(self):
        # 每与一个山地puzzle相连 获得20/30/40粮食
        pass

class Building_028(Puzzle):
    def __init__(self):
        super().__init__(PuzzleType.Building, Shape.Cell, Terrain.Mountain,
                         tags=[BuildingTag.Military])
        self.name = "制高点"    
        self.effect_range = 2
        self.upgrade_cost = {
            2: {PlayerResource.Wood: 150, PlayerResource.Food: 200},
            3: {PlayerResource.Wood: 200, PlayerResource.Food: 200, PlayerResource.Gold: 200}
        }
    
    def Activate(self):
        # 相连的山地单元格每有一个毗邻的平原或农田 驻兵2/3/4箭
        pass

class Building_029(Puzzle):
    def __init__(self):
        super().__init__(PuzzleType.Building, Shape.Two, Terrain.Plain,
                         tags=[BuildingTag.Production])
        self.name = "石矿场"    
        self.effect_range = 2
        self.upgrade_cost = {
            2: {PlayerResource.Gold: 150},
            3: {PlayerResource.Gold: 200}
        }
    
    def Activate(self):
        # 范围3/3/3内的每个森林或平原单元格 获得4/6/8石头
        pass

class Building_030(Puzzle):
    def __init__(self):
        super().__init__(PuzzleType.Building, Shape.Two, Terrain.Mountain,
                         tags=[BuildingTag.Production])
        self.name = "淘金据点"    
        self.effect_range = 2
        self.upgrade_cost = {
            2: {PlayerResource.Food: 50, PlayerResource.Stone: 50},
            3: {PlayerResource.Food: 100, PlayerResource.Stone: 50}
        }
    
    def Activate(self):
        # 每与一个山地puzzle相连 获得25/35/50金币
        pass

class Building_031(Puzzle):
    def __init__(self):
        super().__init__(PuzzleType.Building, Shape.Corner, Terrain.Plain,
                         tags=[BuildingTag.Military])
        self.name = "集结点"    
        self.effect_range = 2
        self.upgrade_cost = {
            2: {PlayerResource.Wood: 250, PlayerResource.Food: 250},
            3: {PlayerResource.Wood: 400, PlayerResource.Food: 400}
        }
    
    def Activate(self):
        # 每个毗邻的平原或农田 征召4/5/6斧 如果总数达到4/5/6 额外获得15/20/25斧
        pass

class Building_032(Puzzle):
    def __init__(self):
        super().__init__(PuzzleType.Building, Shape.Z, Terrain.Plain,
                         tags=[BuildingTag.Production])
        self.name = "果园"    
        self.effect_range = 2
        self.upgrade_cost = {
            2: {PlayerResource.Gold: 150},
            3: {PlayerResource.Gold: 250}
        }
    
    def Activate(self):
        # 每个毗邻的生产建筑 获得25/50/80的粮食和木头
        pass

class Building_033(Puzzle):
    def __init__(self):
        super().__init__(PuzzleType.Building, Shape.Line, Terrain.Forest,
                         tags=[BuildingTag.Production])
        self.name = "木匠铺"    
        self.effect_range = 2
        self.upgrade_cost = {
            2: {PlayerResource.Food: 150},
            3: {PlayerResource.Food: 150, PlayerResource.Stone: 50}
        }
    
    def Activate(self):
        # 所在行和列每有一个建筑 获得20/40/60木头
        pass

class Building_034(Puzzle):
    def __init__(self):
        super().__init__(PuzzleType.Building, Shape.Corner, Terrain.Mountain,
                         tags=[BuildingTag.Military])
        self.name = "秘密洞穴"    
        self.effect_range = 2
        self.upgrade_cost = {
            2: {PlayerResource.Wood: 200, PlayerResource.Stone: 150},
            3: {PlayerResource.Wood: 400, PlayerResource.Stone: 200}
        }
    
    def Activate(self):
        # 每与一个森林puzzle相连 征召2/3/4剑 每与一个山地puzzle相连 征召5/6/7剑
        pass

class Building_035(Puzzle):
    def __init__(self):
        super().__init__(PuzzleType.Terrain, Shape.Corner, Terrain.Farmland,
                         tags=[BuildingTag.Production])
        self.name = "耕地"    
        self.effect_range = 2
        self.upgrade_cost = {
            2: {PlayerResource.Wood: 150},
            3: {PlayerResource.Wood: 200}
        }
    
    def Activate(self):
        # 获得60/120/180的粮食
        pass

class Building_036(Puzzle):
    def __init__(self):
        super().__init__(PuzzleType.Building, Shape.Cell, Terrain.Farmland,
                         tags=[BuildingTag.Production])
        self.name = "风车磨坊"    
        self.effect_range = 2
        self.upgrade_cost = {
            2: {PlayerResource.Wood: 150},
            3: {PlayerResource.Wood: 150, PlayerResource.Gold: 100}
        }
    
    def Activate(self):
        # 每与1个农田单元格相连 获得5/7/10粮食
        pass

class Building_037(Puzzle):
    def __init__(self):
        super().__init__(PuzzleType.Building, Shape.Corner, Terrain.Plain,
                         tags=[BuildingTag.Military])
        self.name = "训练营地"    
        self.effect_range = 2
        self.upgrade_cost = {
            2: {PlayerResource.Food: 450},
            3: {PlayerResource.Food: 500, PlayerResource.Wood: 200}
        }
    
    def Activate(self):
        # 驻兵0/0/0剑 向同行和同列的己方军事建筑输送12/15/18兵力
        pass

class Building_038(Puzzle):
    def __init__(self):
        super().__init__(PuzzleType.Building, Shape.Two, Terrain.Plain,
                         tags=[BuildingTag.Military])
        self.name = "马厩"    
        self.effect_range = 2
        self.upgrade_cost = {
            2: {PlayerResource.Food: 250, PlayerResource.Wood: 250},
            3: {PlayerResource.Food: 300, PlayerResource.Wood: 300, PlayerResource.Stone: 100}
        }
    
    def Activate(self):
        # 与同行或同列最近的建筑 每一格距离提供3/5/6剑
        pass

class Building_039(Puzzle):
    def __init__(self):
        super().__init__(PuzzleType.Building, Shape.Cell, Terrain.Plain,
                         tags=[BuildingTag.Military])
        self.name = "哨塔"    
        self.effect_range = 2
        self.upgrade_cost = {
            2: {PlayerResource.Food: 250, PlayerResource.Gold: 250},
            3: {PlayerResource.Food: 250, PlayerResource.Gold: 400}
        }
    
    def Activate(self):
        # 同行或同列的每一个敌方军事建筑 征召10/15/20斧
        pass

class Building_040(Puzzle):
    def __init__(self):
        super().__init__(PuzzleType.Building, Shape.J, Terrain.Plain,
                         tags=[BuildingTag.Military])
        self.name = "围城营地"    
        self.effect_range = 2
        self.upgrade_cost = {
            2: {PlayerResource.Food: 250, PlayerResource.Wood: 250},
            3: {PlayerResource.Food: 300, PlayerResource.Wood: 300, PlayerResource.Stone: 100}
        }
    
    def Activate(self):
        # 范围2/2/2的所有敌方部队减员8/12/16 驻兵10/15/20斧
        pass

class Building_041(Puzzle):
    def __init__(self):
        super().__init__(PuzzleType.Building, Shape.Cell, Terrain.Plain,
                         tags=[BuildingTag.Production])
        self.name = "税务所"    
        self.effect_range = 2
        self.upgrade_cost = {
            2: {PlayerResource.Wood: 150},
            3: {PlayerResource.Wood: 250, PlayerResource.Food: 100}
        }
    
    def Activate(self):
        # 同行或同列的每一个敌建筑 获得15/25/35金币
        pass

class Building_042(Puzzle):
    def __init__(self):
        super().__init__(PuzzleType.Building, Shape.Corner, Terrain.Forest,
                         tags=[BuildingTag.Production])
        self.name = "煤窑"    
        self.effect_range = 2
        self.upgrade_cost = {
            2: {PlayerResource.Wood: 100, PlayerResource.Food: 50},
            3: {PlayerResource.Wood: 150, PlayerResource.Food: 100}
        }
    
    def Activate(self):
        # 每个毗邻的森林单元格提供10/15/20金币 若被森林包围 额外获得50/100/150金币
        pass


class Building_043(Puzzle):
    def __init__(self):
        super().__init__(PuzzleType.Building, Shape.Corner, Terrain.Plain,
                         tags=[BuildingTag.Military])
        self.name = "营房"    
        self.effect_range = 2
        self.upgrade_cost = {
            2: {PlayerResource.Gold: 500},
            3: {PlayerResource.Gold: 800}
        }
    
    def Activate(self):
        # 每获得20金币 征召2/3/4剑
        pass

class Building_044(Puzzle):
    def __init__(self):
        super().__init__(PuzzleType.Building, Shape.Line, Terrain.Plain,
                         tags=[BuildingTag.Military])
        self.name = "战略枢纽"    
        self.effect_range = 2
        self.upgrade_cost = {
            2: {PlayerResource.Food: 250, PlayerResource.Gold: 250},
            3: {PlayerResource.Food: 250, PlayerResource.Gold: 400}
        }
    
    def Activate(self):
        # 每与1个军事建筑毗邻 征召8/12/16箭
        pass

class Building_045(Puzzle):
    def __init__(self):
        super().__init__(PuzzleType.Building, Shape.Two, Terrain.Plain,
                         tags=[BuildingTag.Production])
        self.name = "锯木厂"    
        self.effect_range = 2
        self.upgrade_cost = {
            2: {PlayerResource.Food: 150},
            3: {PlayerResource.Food: 150, PlayerResource.Gold: 100}
        }
    
    def Activate(self):
        # 相连的水域超出15格的部分 每个单元格获得4/6/8木头
        pass

class Building_046(Puzzle):
    def __init__(self):
        super().__init__(PuzzleType.Building, Shape.Two, Terrain.Plain,
                         tags=[BuildingTag.Production])
        self.name = "水车磨坊"    
        self.effect_range = 2
        self.upgrade_cost = {
            2: {PlayerResource.Wood: 150},
            3: {PlayerResource.Wood: 250}
        }
    
    def Activate(self):
        # 相连的水域超出15格的部分 每个单元格获得4/6/8粮食
        pass

class Building_047(Puzzle):
    def __init__(self):
        super().__init__(PuzzleType.Building, Shape.Two, Terrain.Plain,
                         tags=[BuildingTag.Military])
        self.name = "护河营"    
        self.effect_range = 2
        self.upgrade_cost = {
            2: {PlayerResource.Wood: 200, PlayerResource.Food: 100, PlayerResource.Gold: 200},
            3: {PlayerResource.Wood: 250, PlayerResource.Food: 250, PlayerResource.Gold: 300}
        }
    
    def Activate(self):
        # 驻兵0/0/0斧 如果建筑相邻水域 该水域的其他毗邻友方军事建筑获得8/12/16兵力
        pass

class Building_048(Puzzle):
    def __init__(self):
        super().__init__(PuzzleType.Building, Shape.L, Terrain.Plain,
                         tags=[BuildingTag.Military])
        self.name = "船坞"    
        self.effect_range = 2
        self.upgrade_cost = {
            2: {PlayerResource.Wood: 150, PlayerResource.Food: 150, PlayerResource.Gold: 200},
            3: {PlayerResource.Wood: 200, PlayerResource.Food: 250, PlayerResource.Gold: 400}
        }
    
    def Activate(self):
        # 相连的水域每有一个单元格毗邻板块边框 征召2/4/6斧
        pass


class Building_049(Puzzle):
    def __init__(self):
        super().__init__(PuzzleType.Building, Shape.Cell, Terrain.Plain,
                         tags=[BuildingTag.Production])
        self.name = "渔场"    
        self.effect_range = 2
        self.upgrade_cost = {
            2: {PlayerResource.Wood: 100, PlayerResource.Gold: 50},
            3: {PlayerResource.Wood: 150, PlayerResource.Gold: 100}
        }
    
    def Activate(self):
        # 超过12的每个水域单元格 获得12/18/25粮食
        pass


class Building_050(Puzzle):
    def __init__(self):
        super().__init__(PuzzleType.Building, Shape.T, Terrain.Plain,
                         tags=[BuildingTag.Production])
        self.name = "水畔菜市场"    
        self.effect_range = 2
        self.upgrade_cost = {
            2: {PlayerResource.Wood: 50, PlayerResource.Food: 100},
            3: {PlayerResource.Wood: 100, PlayerResource.Food: 150}
        }
    
    def Activate(self):
        # 超过15的每个水域单元格 获得5/7/10石头
        pass


class Building_051(Puzzle):
    def __init__(self):
        super().__init__(PuzzleType.Terrain, Shape.O, Terrain.Fertile,
                         tags=[BuildingTag.Production])
        self.name = "丰腴之地"    
        self.effect_range = 2
        self.upgrade_cost = {
            2: {PlayerResource.Wood: 50, PlayerResource.Food: 50, PlayerResource.Gold: 50},
            3: {PlayerResource.Wood: 100, PlayerResource.Food: 100, PlayerResource.Gold: 100}
        }
    
    def Activate(self):
        # 获得16/32/48粮食、木头、金币
        pass

class Building_052(Puzzle):
    def __init__(self):
        super().__init__(PuzzleType.Building, Shape.Line, Terrain.River,
                         tags=[BuildingTag.Production])
        self.name = "桥梁"    
        self.effect_range = 2
        self.upgrade_cost = {
            2: {PlayerResource.Wood: 50, PlayerResource.Food: 50},
            3: {PlayerResource.Wood: 100, PlayerResource.Food: 100}
        }
    
    def Activate(self):
        # 超过15的每个相连水域 获得3/5/7金币
        pass

class Building_053(Puzzle):
    def __init__(self):
        super().__init__(PuzzleType.Building, Shape.O, Terrain.Plain,
                         tags=[BuildingTag.Military])
        self.name = "水畔城堡"    
        self.effect_range = 2
        self.upgrade_cost = {
            2: {PlayerResource.Wood: 250, PlayerResource.Food: 250, PlayerResource.Gold: 150},
            3: {PlayerResource.Food: 150, PlayerResource.Gold: 100, PlayerResource.Stone: 300}
        }
    
    def Activate(self):
        # 超过15的每个相连水域 获得1/2/3剑
        pass

class Building_054(Puzzle):
    def __init__(self):
        super().__init__(PuzzleType.Building, Shape.Two, Terrain.Forest,
                         tags=[BuildingTag.Production])
        self.name = "平原造林站"    
        self.effect_range = 2
        self.upgrade_cost = {
            2: {PlayerResource.Food: 100, PlayerResource.Gold: 50},
            3: {PlayerResource.Food: 150, PlayerResource.Gold: 100, PlayerResource.Stone: 50}
        }
    
    def Activate(self):
        # 范围2/2/3内的平原变成树林
        pass


class Building_055(Puzzle):
    def __init__(self):
        super().__init__(PuzzleType.Building, Shape.O, Terrain.Mountain,
                         tags=[BuildingTag.Military])
        self.name = "要塞"    
        self.effect_range = 2
        self.upgrade_cost = {
            2: {PlayerResource.Wood: 450},
            3: {PlayerResource.Wood: 650, PlayerResource.Food: 200}
        }
    
    def Activate(self):
        # 每与1个空板块相邻 或是与板块边框相邻 获得4/7/10箭
        pass

class Building_056(Puzzle):
    def __init__(self):
        super().__init__(PuzzleType.Building, Shape.Cell, Terrain.Plain,
                         tags=[BuildingTag.Religion])
        self.name = "小教堂"    
        self.effect_range = 2
        self.upgrade_cost = {
            2: {PlayerResource.Wood: 100},
            3: {PlayerResource.Wood: 100, PlayerResource.Gold: 100}
        }
    
    def Activate(self):
        # 如果毗邻其他建筑 获得1/2/3信仰
        pass

class Building_057(Puzzle):
    def __init__(self):
        super().__init__(PuzzleType.Building, Shape.Two, Terrain.Plain,
                         tags=[BuildingTag.Religion])
        self.name = "教堂"    
        self.effect_range = 2
        self.upgrade_cost = {
            2: {PlayerResource.Wood: 50, PlayerResource.Food: 50, PlayerResource.Gold: 100},
            3: {PlayerResource.Stone: 50, PlayerResource.Gold: 200}
        }
    
    def Activate(self):
        # 获得2/3/4信仰
        pass

class Building_058(Puzzle):
    def __init__(self):
        super().__init__(PuzzleType.Building, Shape.Two, Terrain.Plain,
                         tags=[BuildingTag.Religion])
        self.name = "神学院"    
        self.effect_range = 2
        self.upgrade_cost = {
            2: {PlayerResource.Food: 150, PlayerResource.Gold: 50},
            3: {PlayerResource.Food: 250, PlayerResource.Stone: 50}
        }
    
    def Activate(self):
        # 如果毗邻宗教建筑 获得3/4/5信仰
        pass

class Building_059(Puzzle):
    def __init__(self):
        super().__init__(PuzzleType.Building, Shape.Two, Terrain.Forest,
                         tags=[BuildingTag.Religion])
        self.name = "教堂捐税所"    
        self.effect_range = 2
        self.upgrade_cost = {
            2: {PlayerResource.Gold: 200},
            3: {PlayerResource.Gold: 100, PlayerResource.Stone: 100}
        }
    
    def Activate(self):
        # 如果毗邻森林 获得信仰值3/5/7倍的粮食、木头和金币
        pass

class Building_060(Puzzle):
    def __init__(self):
        super().__init__(PuzzleType.Building, Shape.Line, Terrain.Plain,
                         tags=[BuildingTag.Religion])
        self.name = "僧院"    
        self.effect_range = 2
        self.upgrade_cost = {
            2: {PlayerResource.Gold: 200},
            3: {PlayerResource.Gold: 300}
        }
    
    def Activate(self):
        # 获得1信仰和信仰值10/15/20倍的粮食
        pass

class Building_061(Puzzle):
    def __init__(self):
        super().__init__(PuzzleType.Building, Shape.S, Terrain.Plain,
                         tags=[BuildingTag.Religion])
        self.name = "修道院"    
        self.effect_range = 2
        self.upgrade_cost = {
            2: {PlayerResource.Wood: 100, PlayerResource.Food: 100},
            3: {PlayerResource.Wood: 150, PlayerResource.Food: 150}
        }
    
    def Activate(self):
        # 获得1信仰和信仰值10/15/20倍的木材
        pass

class Building_062(Puzzle):
    def __init__(self):
        super().__init__(PuzzleType.Building, Shape.Corner, Terrain.Plain,
                         tags=[BuildingTag.Religion, BuildingTag.Military])
        self.name = "骑士团团长辖地"    
        self.effect_range = 2
        self.upgrade_cost = {
            2: {PlayerResource.Wood: 150, PlayerResource.Food: 150, PlayerResource.Gold: 200},
            3: {PlayerResource.Wood: 250, PlayerResource.Stone: 200, PlayerResource.Gold: 200}
        }
    
    def Activate(self):
        # 获得1信仰 驻兵信仰值3/4/5倍的剑
        pass

class Building_063(Puzzle):
    def __init__(self):
        super().__init__(PuzzleType.Building, Shape.T, Terrain.Plain,
                         tags=[BuildingTag.Military])
        self.name = "异教巢穴"    
        self.effect_range = 2
        self.upgrade_cost = {
            2: {PlayerResource.Wood: 150, PlayerResource.Food: 150, PlayerResource.Gold: 200, PlayerResource.Faith: 10},
            3: {PlayerResource.Wood: 200, PlayerResource.Food: 200, PlayerResource.Gold: 400, PlayerResource.Faith: 20}
        }
    
    def Activate(self):
        # 驻兵25/40/60
        pass

class Building_064(Puzzle):
    def __init__(self):
        super().__init__(PuzzleType.Building, Shape.Cell, Terrain.Mountain,
                         tags=[BuildingTag.Religion])
        self.name = "隐士洞穴"    
        self.effect_range = 2
        self.upgrade_cost = {
            2: {PlayerResource.Stone: 100, PlayerResource.Food: 50},
            3: {PlayerResource.Stone: 200, PlayerResource.Food: 150}
        }
    
    def Activate(self):
        # 获得3/5/7信仰
        pass

class Building_065(Puzzle):
    def __init__(self):
        super().__init__(PuzzleType.Building, Shape.Cell, Terrain.Plain,
                         tags=[BuildingTag.Religion, BuildingTag.Unique])
        self.name = "圣地"    
        self.effect_range = 2
        self.upgrade_cost = {
            2: {PlayerResource.Wood: 200, PlayerResource.Food: 100, PlayerResource.Gold: 300},
            3: {PlayerResource.Stone: 250, PlayerResource.Gold: 450}
        }
    
    def Activate(self):
        # 获得2/4/6信仰 2/2/3范围内的所有部队减员你的信仰值
        pass

class Building_066(Puzzle):
    def __init__(self):
        super().__init__(PuzzleType.Building, Shape.Corner, Terrain.Plain,
                         tags=[BuildingTag.Military])
        self.name = "监狱"    
        self.effect_range = 2
        self.upgrade_cost = {
            2: {PlayerResource.Food: 500},
            3: {PlayerResource.Food: 600, PlayerResource.Stone: 100}
        }
    
    def Activate(self):
        # 驻兵25/40/55 如果毗邻的敌方部队兵力总和达到30/45/60 则移除自己的部队
        pass

class Building_067(Puzzle):
    def __init__(self):
        super().__init__(PuzzleType.Building, Shape.L, Terrain.Plain,
                         tags=[BuildingTag.Military])
        self.name = "盗贼巢穴"    
        self.effect_range = 2
        self.upgrade_cost = {
            2: {PlayerResource.Food: 150, PlayerResource.Wood: 150, PlayerResource.Gold: 200},
            3: {PlayerResource.Food: 300, PlayerResource.Wood: 300, PlayerResource.Gold: 300}
        }
    
    def Activate(self):
        # 范围2/2/2内的每个建筑 支付4/7/10粮食、木头、金币 征召10/15/20剑
        pass

class Building_068(Puzzle):
    def __init__(self):
        super().__init__(PuzzleType.Building, Shape.Two, Terrain.Plain,
                         tags=[BuildingTag.Military])
        self.name = "补给线"    
        self.effect_range = 2
        self.upgrade_cost = {
            2: {PlayerResource.Food: 250, PlayerResource.Wood: 250},
            3: {PlayerResource.Food: 300, PlayerResource.Wood: 250, PlayerResource.Stone: 150}
        }
    
    def Activate(self):
        # 同行和同列的每一个环境单元格 支付1/1/2粮食、木头 征召3/4/5箭
        pass

class Building_069(Puzzle):
    def __init__(self):
        super().__init__(PuzzleType.Building, Shape.Z, Terrain.Barren,
                         tags=[BuildingTag.Military])
        self.name = "劫掠殖民地"    
        self.effect_range = 2
        self.upgrade_cost = {
            2: {PlayerResource.Food: 100, PlayerResource.Wood: 100, PlayerResource.Gold: 300},
            3: {PlayerResource.Stone: 200, PlayerResource.Gold: 500}
        }
    
    def Activate(self):
        # 驻兵30/50/70 将毗邻的单元格转换成荒地 每一个转换扣除3/4/5兵力
        pass

class Building_070(Puzzle):
    def __init__(self):
        super().__init__(PuzzleType.Building, Shape.O, Terrain.Plain,
                         tags=[BuildingTag.Military, BuildingTag.Unique, BuildingTag.Nobility])
        self.name = "城堡"    
        self.effect_range = 2
        self.upgrade_cost = {
            2: {PlayerResource.Food: 200, PlayerResource.Wood: 200, PlayerResource.Gold: 300},
            3: {PlayerResource.Food: 100, PlayerResource.Stone: 200, PlayerResource.Gold: 500}
        }
    
    def Activate(self):
        # 驻兵25/40/60斧
        pass

class Building_071(Puzzle):
    def __init__(self):
        super().__init__(PuzzleType.Building, Shape.O, Terrain.Plain,
                         tags=[BuildingTag.Military, BuildingTag.Nobility])
        self.name = "棱堡"    
        self.effect_range = 2
        self.upgrade_cost = {
            2: {PlayerResource.Food: 200, PlayerResource.Stone: 50, PlayerResource.Gold: 200},
            3: {PlayerResource.Food: 300, PlayerResource.Stone: 200, PlayerResource.Gold: 300}
        }
    
    def Activate(self):
        # 驻兵10/15/20 每个毗邻的平原征召3/4/6箭
        pass

class Building_072(Puzzle):
    def __init__(self):
        super().__init__(PuzzleType.Building, Shape.Z, Terrain.Plain,
                         tags=[BuildingTag.Production, BuildingTag.Nobility])
        self.name = "皇家花园"    
        self.effect_range = 2
        self.upgrade_cost = {
            2: {PlayerResource.Wood: 100, PlayerResource.Food: 50, PlayerResource.Gold: 50},
            3: {PlayerResource.Food: 50, PlayerResource.Stone: 100, PlayerResource.Gold: 50}
        }
    
    def Activate(self):
        # 完全探索时 对应的行或列中的每个单元格获得8/16/24粮食、木头、金币
        pass

class Building_073(Puzzle):
    def __init__(self):
        super().__init__(PuzzleType.Building, Shape.Corner, Terrain.Plain,
                         tags=[BuildingTag.Production, BuildingTag.Nobility])
        self.name = "庄园"    
        self.effect_range = 2
        self.upgrade_cost = {
            2: {PlayerResource.Wood: 150, PlayerResource.Gold: 100},
            3: {PlayerResource.Stone: 100, PlayerResource.Gold: 100}
        }
    
    def Activate(self):
        # 激活范围1/2/3内的所有单元格和建筑效果
        pass

class Building_074(Puzzle):
    def __init__(self):
        super().__init__(PuzzleType.Building, Shape.Cell, Terrain.Plain,
                         tags=[BuildingTag.Special])
        self.name = "铁匠铺"    
        self.effect_range = 2
        self.upgrade_cost = {
            2: {PlayerResource.Wood: 500, PlayerResource.Stone: 100},
            3: {PlayerResource.Wood: 500, PlayerResource.Stone: 200, PlayerResource.Gold: 200}
        }
    
    def Activate(self):
        # 驻兵0剑 触发1/2/3个毗邻建筑的效果
        pass

class Building_075(Puzzle):
    def __init__(self):
        super().__init__(PuzzleType.Building, Shape.O, Terrain.Plain,
                         tags=[BuildingTag.Unique, BuildingTag.Nobility])
        self.name = "大教堂"    
        self.effect_range = 2
        self.upgrade_cost = {
            2: {PlayerResource.Stone: 150, PlayerResource.Food: 100, PlayerResource.Gold: 300},
            3: {PlayerResource.Stone: 300, PlayerResource.Food: 200, PlayerResource.Gold: 300}
        }
    
    def Activate(self):
        # 获得1/3/5信仰 1/1/1范围内的建筑提供的信仰翻倍
        pass

class Building_076(Puzzle):
    def __init__(self):
        super().__init__(PuzzleType.Building, Shape.Cell, Terrain.Plain,
                         tags=[BuildingTag.Special, BuildingTag.Unique, BuildingTag.Nobility])
        self.name = "纪念碑"    
        self.effect_range = 2
        self.upgrade_cost = {
            2: {PlayerResource.Wood: 200, PlayerResource.Food: 300, PlayerResource.Gold: 200},
            3: {PlayerResource.Food: 300, PlayerResource.Stone: 300, PlayerResource.Gold: 200}
        }
    
    def Activate(self):
        # 范围2/2/3内的所有部队获得15/25/30兵力
        pass
