try:
    from Tetris.game.player import PlayerResource, Player
    from Tetris.game.terrain import Terrain, Shape, Puzzle
except:
    from player import PlayerResource, Player
    from terrain import Terrain, Shape, Puzzle

import os
import xml.etree.ElementTree as ET

class BuildingFactory:
    def __init__(self):
        self.buildings = {}
        self.config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'Buildings.xml')
    
    def ReadConfig(self):
        """从 XML 配置文件中读取建筑定义"""
        try:
            tree = ET.parse(self.config_path)
            root = tree.getroot()
            
            for building in root.findall('Building'):
                # 解析基本属性
                building_id = int(building.get('id'))
                name = building.get('Name')
                shape = building.get('shape')
                tags = building.get('tags', '').split(',')
                
                # 创建建筑实例
                building_instance = dict()
                building_instance['id'] = building_id
                building_instance['name'] = name
                building_instance['shape'] = Shape[shape]
                building_instance['tags'] = [tag.strip() for tag in tags if tag.strip()]
                
                
                # 解析升级成本
                cost_element = building.find('Cost')
                if cost_element is not None:
                    upgrade_costs = {}
                    for resource in cost_element.findall('Resource'):
                        resource_type = resource.get('Type')
                        amounts = resource.get('Amount').split('/')
                        
                        # 处理每个等级的成本
                        for level, amount in enumerate(amounts, start=2):
                            if level not in upgrade_costs:
                                upgrade_costs[level] = {}
                            if amount != '0':
                                upgrade_costs[level][PlayerResource[resource_type]] = int(amount)
                    
                    building_instance.upgrade_cost = upgrade_costs
                
                # 将建筑实例添加到字典中
                self.buildings[building_id] = building_instance
                
        except Exception as e:
            print(f"Error reading building config: {e}")
            raise
    
    def GetBuildingById(self, id):
        """根据ID获取建筑实例"""
        return self.buildings.get(id, None)
    
    def GetAllBuildings(self):
        """获取所有建筑实例"""
        return self.buildings

if __name__ == '__main__':
    main = BuildingFactory()
    main.ReadConfig()
    building = main.GetBuildingById(1)
    print(building)