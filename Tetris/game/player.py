from enum import Enum

class PlayerResource(Enum):
    Gold = 0        # 金币
    Food = 1        # 粮食
    Wood = 2        # 木头
    Stone = 3       # 石头
    Faith = 6       # 信仰
    Decree = 7      # 政令点数
    Citizen = 8    # 市民

class Player:
    def __init__(self):
        self.name = None
        self.resources = {
            PlayerResource.Gold: 100,
            PlayerResource.Food: 100,
            PlayerResource.Wood: 100,
            PlayerResource.Stone: 0,
            PlayerResource.Faith: 0,
            PlayerResource.Decree: 0,
            PlayerResource.Citizen: 0
        }

    def ResourceEnough(self, cost: dict) -> bool:
        if cost is None:
            return True
        for resource, count in cost.items():
            if self.resources[resource] < count:
                return False
        return True

    def Cost(self, cost: dict):
        if cost is None:
            return
        for resource, count in cost.items():
            self.resources[resource] -= count
        
    def Serialize(self):
        ret = dict()
        ret['name'] = self.name
        ret['resources'] = self.resources
        return ret

    def Deserialize(self, data):
        self.name = data['name']
        self.resources = data['resources']


def load_players(data: list) -> list:
    players = []
    for player in data:
        player = Player()
        player.Deserialize(player)
        players.append(player)
    return players