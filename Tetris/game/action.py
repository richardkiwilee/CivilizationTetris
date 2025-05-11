from enum import Enum

class SystemResponse(Enum):
    OK = 200
    ERROR = 400

class PlayerAction(Enum):
    StartGame = 0       # 仅房主可用 开始游戏
    Login = 1           # 加入大厅
    Logout = 2          # 退出大厅
    Ready = 3           # 仅大厅可用 等待确认
    CancelReady = 4     # 仅大厅可用 取消确认
    EndTurn = 5         # 仅游戏内可用 下一回合
    Place = 6           # 仅游戏内可用 放置一个板块
    Active = 7          # 仅游戏内可用 激活一个建筑的效果
    Upgrade = 8         # 仅游戏内可用 升级一个建筑
    Attack = 9          # 仅游戏内可用 发起进攻
    Sync = 10           # 强制同步游戏状态