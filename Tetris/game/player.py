from enum import Enum

class PlayerResource(Enum):
    Gold = 0        # 金币
    Food = 1        # 粮食
    Wood = 2        # 木头
    Stone = 3       # 石头
    Faith = 6       # 信仰
    Decree = 7      # 政令点数
    Citizen = 8    # 市民

prod_resource = {
            PlayerResource.Gold.value: 0,
            PlayerResource.Food.value: 100,
            PlayerResource.Wood.value: 100,
            PlayerResource.Stone.value: 0,
            PlayerResource.Faith.value: 0,
            PlayerResource.Decree.value: 0,
            PlayerResource.Citizen.value: 0
        }

debug_resource = {
            PlayerResource.Gold.value: 1000,
            PlayerResource.Food.value: 1000,
            PlayerResource.Wood.value: 1000,
            PlayerResource.Stone.value: 1000,
            PlayerResource.Faith.value: 1000,
            PlayerResource.Decree.value: 1000,
            PlayerResource.Citizen.value: 1000
        }

class Player:
    def __init__(self):
        self.name = None
        self.resources = debug_resource
        self.puzzles = dict()

    def ResourceEnough(self, cost: dict) -> bool:
        if cost is None:
            return True
        for resource, count in cost.items():
            if self.resources[resource] < count:
                return False
        return True

    def AddResource(self, resource: PlayerResource, count: int):
        self.resources[resource.value] += count

    def Cost(self, cost: dict):
        if cost is None:
            return
        for resource, count in cost.items():
            self.resources[resource] -= count
        
    def Serialize(self):
        ret = dict()
        ret['name'] = self.name
        ret['resources'] = self.resources
        ret['puzzles'] = {puzzle.puzzle_id: puzzle.dump() for puzzle in self.puzzles.values()}
        return ret

    def Deserialize(self, data):
        self.name = data['name']
        self.resources = data['resources']
        self.puzzles = {puzzle_id: load_puzzle(puzzle) for puzzle_id, puzzle in data['puzzles'].items()}

def load_players(data: list) -> list:
    players = []
    for player in data:
        player = Player()
        player.Deserialize(player)
        players.append(player)
    return players