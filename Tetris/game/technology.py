from Tetris.game.player import PlayerResource


class Technology:
    def __init__(self):
        self.name = None
        self.description = None
    

class Tech_001(Technology):
    def __init__(self):
        super().__init__()
        self.name = "民兵"
        self.description = "每与一个生产建筑相邻 军事建筑征召4/8/12"
        self.upgrade_cost = {
            2: {PlayerResource.Food: 400},
            3: {PlayerResource.Food: 400, PlayerResource.Stone: 100},
        }


class Tech_002(Technology):
    def __init__(self):
        super().__init__()
        self.name = "重犁"
        self.description = "农田的收获奖励+2"
        self.upgrade_cost = {
            2: {PlayerResource.Wood: 150},
            3: {PlayerResource.Wood: 200, PlayerResource.Gold: 100},
        }

class Tech_003(Technology):
    def __init__(self):
        super().__init__()
        self.name = "菜园"
        self.description = "建筑落成后 毗邻的1/2/3个平原转换为农田"
        self.upgrade_cost = {
            2: {PlayerResource.Wood: 150},
            3: {PlayerResource.Wood: 200},
        }

class Tech_004(Technology):
    def __init__(self):
        super().__init__()
        self.name = "后勤补给"
        self.description = "如果军事建筑毗邻的农田达到3个 征召4/7/10"
        self.upgrade_cost = {
            2: {PlayerResource.Wood: 150, PlayerResource.Food: 150},
            3: {PlayerResource.Food: 300, PlayerResource.Stone: 100},
        }


class Tech_005(Technology):
    def __init__(self):
        super().__init__()
        self.name = "朝圣信徒"
        self.description = "宗教建筑落成时 获得20/30/40金币"
        self.upgrade_cost = {
            2: {PlayerResource.Food: 150},
            3: {PlayerResource.Food: 300},
        }

class Tech_006(Technology):
    def __init__(self):
        super().__init__()
        self.name = "税收兴城"
        self.description = "每个毗邻城市的生产建筑 获得30/45/60金币"
        self.upgrade_cost = {
            2: {PlayerResource.Food: 50, PlayerResource.Wood: 150},
            3: {PlayerResource.Food: 50, PlayerResource.Wood: 100, PlayerResource.Stone: 50},
        }


class Tech_007(Technology):
    def __init__(self):
        super().__init__()
        self.name = "十字军远征"
        self.description = "战斗胜利获得1/2/3/4/5/6/7/8/9/10粮食、木头、石头、金币"
        self.upgrade_cost = {
            2: {PlayerResource.Faith: 10},
            3: {PlayerResource.Faith: 10},
            4: {PlayerResource.Faith: 10},
            5: {PlayerResource.Faith: 10},
            6: {PlayerResource.Faith: 10},
            7: {PlayerResource.Faith: 10},
            8: {PlayerResource.Faith: 10},
            9: {PlayerResource.Faith: 10},
            10: {PlayerResource.Faith: 10},
        }

class Tech_008(Technology):
    def __init__(self):
        super().__init__()
        self.name = "以剑之名"
        self.description = "每征召80/65/50, 获得1信仰"
        self.upgrade_cost = {
            2: {PlayerResource.Stone: 50, PlayerResource.Gold: 150},
            3: {PlayerResource.Stone: 100, PlayerResource.Gold: 250},
        }

class Tech_009(Technology):
    def __init__(self):
        super().__init__()
        self.name = "强迫皈依"
        self.description = "回合结束时 宗教建筑1/2/3范围内的敌方部队减员10/15/25"
        self.upgrade_cost = {
            2: {PlayerResource.Food: 150, PlayerResource.Gold: 150},
            3: {PlayerResource.Food: 200, PlayerResource.Gold: 200},
        }

class Tech_010(Technology):
    def __init__(self):
        super().__init__()
        self.name = "虔诚"
        self.description = "宗教建筑落成时 所有敌方部队减员20/30/40"
        self.upgrade_cost = {
            2: {PlayerResource.Food: 100, PlayerResource.Stone: 50, PlayerResource.Gold: 100},
            3: {PlayerResource.Food: 100, PlayerResource.Stone: 100, PlayerResource.Gold: 100},
        }

class Tech_011(Technology):
    def __init__(self):
        super().__init__()
        self.name = "独轮车"
        self.description = "完全探索时 获得15/30/50金币"
        self.upgrade_cost = {
            2: {PlayerResource.Food: 150},
            3: {PlayerResource.Wood: 150, PlayerResource.Food: 150},
        }

class Tech_012(Technology):
    def __init__(self):
        super().__init__()
        self.name = "防线加强"
        self.description = "你的大本营获得10/15/20兵力"
        self.upgrade_cost = {
            2: {PlayerResource.Food: 100, PlayerResource.Wood: 100},
            3: {PlayerResource.Food: 150, PlayerResource.Stone: 50},
        }

class Tech_013(Technology):
    def __init__(self):
        super().__init__()
        self.name = "踏轮起重机"
        self.description = "建筑牌升级成本降低10/20/30%"
        self.upgrade_cost = {
            2: {PlayerResource.Wood: 200, PlayerResource.Gold: 100},
            3: {PlayerResource.Wood: 200, PlayerResource.Stone: 100, PlayerResource.Gold: 100},
        }

class Tech_014(Technology):
    def __init__(self):
        super().__init__()
        self.name = "印刷机"
        self.description = "技术牌升级成本降低10/20/30%"
        self.upgrade_cost = {
            2: {PlayerResource.Wood: 150, PlayerResource.Food: 150},
            3: {PlayerResource.Stone: 100, PlayerResource.Gold: 200},
        }

class Tech_015(Technology):
    def __init__(self):
        super().__init__()
        self.name = "柴火"
        self.description = "完全探索时, 该行或列上的每一个毗邻森林的建筑获得5/10/15木头"
        self.upgrade_cost = {
            2: {PlayerResource.Food: 150, PlayerResource.Gold: 50},
            3: {PlayerResource.Food: 200, PlayerResource.Gold: 50},
        }

class Tech_016(Technology):
    def __init__(self):
        super().__init__()
        self.name = "鬼斧石工"
        self.description = "所有石头成本降低20/40/60%"
        self.upgrade_cost = {
            2: {PlayerResource.Food: 150, PlayerResource.Wood: 150},
            3: {PlayerResource.Food: 250, PlayerResource.Wood: 250},
        }

class Tech_017(Technology):
    def __init__(self):
        super().__init__()
        self.name = "灌溉"
        self.description = "建筑落成时 毗邻的板块提升富饶度 荒地-平原-森林-肥沃"
        self.upgrade_cost = {
            2: {PlayerResource.Food: 50, PlayerResource.Wood: 50, PlayerResource.Gold: 50},
            3: {PlayerResource.Food: 100, PlayerResource.Wood: 100, PlayerResource.Gold: 100},
        }

class Tech_018(Technology):
    def __init__(self):
        super().__init__()
        self.name = "伐木造田"
        self.description = "建筑落成时 毗邻的森林板块变成平原/农田/农田并获得25/50/100木头"
        self.upgrade_cost = {
            2: {PlayerResource.Food: 200},
            3: {PlayerResource.Food: 250},
        }

class Tech_019(Technology):
    def __init__(self):
        super().__init__()
        self.name = "改换有术"
        self.description = "环境发生改变时 获得原本环境4/6/8倍的探索奖励"
        self.upgrade_cost = {
            2: {PlayerResource.Wood: 100, PlayerResource.Food: 50},
            3: {PlayerResource.Wood: 100, PlayerResource.Food: 100, PlayerResource.Stone: 50},
        }

class Tech_020(Technology):
    def __init__(self):
        super().__init__()
        self.name = "土地扩建"
        self.description = "改变环境时, 如果改变个数达到4/3/2, 额外改变一个单元格"
        self.upgrade_cost = {
            2: {PlayerResource.Wood: 50, PlayerResource.Food: 100},
            3: {PlayerResource.Wood: 150, PlayerResource.Food: 150},
        }

class Tech_021(Technology):
    def __init__(self):
        super().__init__()
        self.name = "优化大师"
        self.description = "完全探索多行的奖励增加1/2/3"
        self.upgrade_cost = {
            2: {PlayerResource.Wood: 100, PlayerResource.Food: 100},
            3: {PlayerResource.Wood: 100, PlayerResource.Food: 100, PlayerResource.Gold: 100},
        }

class Tech_022(Technology):
    def __init__(self):
        super().__init__()
        self.name = "意外收获"
        self.description = "完全探索时 20/30/40%概率获得双倍资源"
        self.upgrade_cost = {
            2: {PlayerResource.Gold: 200},
            3: {PlayerResource.Gold: 250, PlayerResource.Stone: 50},
        }

class Tech_023(Technology):
    def __init__(self):
        super().__init__()
        self.name = "海水入江湖"
        self.description = "完全探索时 毗邻板块边框的每个水域单元格获得5/10/15金币"
        self.upgrade_cost = {
            2: {PlayerResource.Wood: 200},
            3: {PlayerResource.Wood: 250},
        }

class Tech_024(Technology):
    def __init__(self):
        super().__init__()
        self.name = "护城河"
        self.description = "被水域包围的军事建筑增加15/30/45兵力"
        self.upgrade_cost = {
            2: {PlayerResource.Wood: 300, PlayerResource.Gold: 100},
            3: {PlayerResource.Wood: 350, PlayerResource.Gold: 150, PlayerResource.Stone: 50},
        }

class Tech_025(Technology):
    def __init__(self):
        super().__init__()
        self.name = "运河"
        self.description = "获得2/3/4个水域puzzle"
        self.upgrade_cost = {
            2: {PlayerResource.Gold: 200},
            3: {PlayerResource.Gold: 250},
        }

class Tech_026(Technology):
    def __init__(self):
        super().__init__()
        self.name = "同心协力"
        self.description = "汇合的部队如果是同一兵种 额外获得7/11/15兵力"
        self.upgrade_cost = {
            2: {PlayerResource.Food: 100, PlayerResource.Gold: 100},
            3: {PlayerResource.Food: 100, PlayerResource.Gold: 100, PlayerResource.Stone: 100},
        }

class Tech_027(Technology):
    def __init__(self):
        super().__init__()
        self.name = "战术优势"
        self.description = "建筑落成时 如果毗邻的军事建筑拥有同样的兵种类型 双方获得4/8/12额外兵力"
        self.upgrade_cost = {
            2: {PlayerResource.Wood: 200, PlayerResource.Gold: 200},
            3: {PlayerResource.Wood: 200, PlayerResource.Gold: 200, PlayerResource.Stone: 100},
        }

class Tech_028(Technology):
    def __init__(self):
        super().__init__()
        self.name = "一个不留"
        self.description = "全歼敌军时获得100/150/200金币"
        self.upgrade_cost = {
            2: {PlayerResource.Wood: 150, PlayerResource.Food: 100},
            3: {PlayerResource.Wood: 300, PlayerResource.Food: 100},
        }

class Tech_029(Technology):
    def __init__(self):
        super().__init__()
        self.name = "封堵"
        self.description = "如果进攻的敌方军事建筑被山地单元格包围, 减员其50/75/100%的兵力"
        self.upgrade_cost = {
            2: {PlayerResource.Stone: 100},
            3: {PlayerResource.Stone: 200}
        }

class Tech_030(Technology):
    def __init__(self):
        super().__init__()
        self.name = "博学"
        self.description = "抽卡时 选项+1/2/3"
        self.upgrade_cost = {
            2: {PlayerResource.Gold: 200},
            3: {PlayerResource.Gold: 200, PlayerResource.Stone: 100, PlayerResource.Food: 100},
        }

class Tech_031(Technology):
    def __init__(self):
        super().__init__()
        self.name = "圣物匣"
        self.description = "信仰+1/2/3"
        self.upgrade_cost = {
            2: {PlayerResource.Gold: 100, PlayerResource.Wood: 100, PlayerResource.Food: 100},
            3: {PlayerResource.Gold: 150, PlayerResource.Stone: 50, PlayerResource.Food: 150},
        }

class Tech_032(Technology):
    def __init__(self):
        super().__init__()
        self.name = "神圣祝福"
        self.description = "你的大本营获得信仰值1/2/3倍的兵力"
        self.upgrade_cost = {
            2: {PlayerResource.Gold: 100, PlayerResource.Wood: 100},
            3: {PlayerResource.Stone: 100, PlayerResource.Gold: 100},
        }

class Tech_033(Technology):
    def __init__(self):
        super().__init__()
        self.name = "每日食粮"
        self.description = "每8/6/4块田地完全探索 +1信仰"
        self.upgrade_cost = {
            2: {PlayerResource.Food: 200},
            3: {PlayerResource.Food: 200, PlayerResource.Gold: 100},
        }

class Tech_034(Technology):
    def __init__(self):
        super().__init__()
        self.name = "宗教热情"
        self.description = "进攻时 用你的信仰减去对方兵力 如果结果小于10/20/30 获得对方兵力的控制权"
        self.upgrade_cost = {
            2: {PlayerResource.Food: 200, PlayerResource.Gold: 300},
            3: {PlayerResource.Food: 200, PlayerResource.Gold: 200, PlayerResource.Stone: 200},
        }

class Tech_035(Technology):
    def __init__(self):
        super().__init__()
        self.name = "什一奉献"
        self.description = "获得信仰时 获得5/10/15金币"
        self.upgrade_cost = {
            2: {PlayerResource.Food: 100, PlayerResource.Wood: 150},
            3: {PlayerResource.Food: 150, PlayerResource.Wood: 150, PlayerResource.Stone: 50},
        }

class Tech_036(Technology):
    def __init__(self):
        super().__init__()
        self.name = "隐居修士"
        self.description = "宗教建筑每与一个山地puzzle相邻 你的大本营获得1/2/3兵力"
        self.upgrade_cost = {
            2: {PlayerResource.Food: 50, PlayerResource.Stone: 50},
            3: {PlayerResource.Food: 100, PlayerResource.Stone: 100},
        }

class Tech_037(Technology):
    def __init__(self):
        super().__init__()
        self.name = "皇家旨意"
        self.description = "贵族建筑牌建成后 转变的单元格类型变为森林/水域/农田"
        self.upgrade_cost = {
            2: {PlayerResource.Gold: 200},
            3: {PlayerResource.Stone: 50, PlayerResource.Gold: 250},
        }

class Tech_038(Technology):
    def __init__(self):
        super().__init__()
        self.name = "天赋神权"
        self.description = "贵族建筑牌建成后 +1/2/3信仰"
        self.upgrade_cost = {
            2: {PlayerResource.Stone: 100},
            3: {PlayerResource.Stone: 150},
        }

