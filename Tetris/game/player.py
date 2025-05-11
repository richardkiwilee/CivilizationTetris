from enum import Enum

class PlayerResource(Enum):
    Gold = 0        # 金币
    Food = 1        # 粮食
    Wood = 2        # 木头
    Stone = 3       # 石头
    Iron = 4        # 铁
    Horse = 5       # 马
    Faith = 6       # 信仰
    Decree = 7      # 政令点数
    Citizen = 8    # 市民

class Player:
    def __init__(self, name: str):
        self.name = name
        self.resources = {
            PlayerResource.Gold.value: 100,
            PlayerResource.Food.value: 100,
            PlayerResource.Wood.value: 100,
            PlayerResource.Stone.value: 0,
            PlayerResource.Iron.value: 0,
            PlayerResource.Horse.value: 0,
            PlayerResource.Faith.value: 0,
            PlayerResource.Decree.value: 0,
            PlayerResource.Citizen.value: 0
        }
