try:
    from Tetris.game.player import PlayerResource, Player
    from Tetris.game.terrain import Terrain, ShapeHelper, Puzzle
except:
    from player import PlayerResource, Player
    from terrain import Terrain, ShapeHelper, Puzzle

import os
import xml.etree.ElementTree as ET

class BuildingFactory:
    def __init__(self):
        self.buildings = {}
        self.config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'Buildings.xml')
        self.ReadConfig()
    
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
                
                # 解析common
                common_element = building.find('Desc')
                common_text = common_element.get('text') if common_element is not None else ''
                
                # 创建建筑实例
                building_instance = dict()
                building_instance['id'] = building_id
                building_instance['name'] = name
                building_instance['shape'] = ShapeHelper().GetShape(shape)
                building_instance['tags'] = [tag.strip() for tag in tags if tag.strip()]
                building_instance['desc'] = common_text
                
                # 解析升级成本
                cost_element = building.find('Cost')
                if cost_element is not None:
                    upgrade_costs = {}
                    for resource in cost_element.findall('Resource'):
                        resource_type = resource.get('Type')
                        amounts = resource.get('Amount').split('/')
                        
                        # 处理每个等级的成本，从0级开始
                        max_level = 2  # 通常有3个等级 (0,1,2)
                        for level in range(max_level + 1):
                            if level not in upgrade_costs:
                                upgrade_costs[level] = {}
                            # 如果当前等级超出了amounts列表长度，视为0
                            amount = amounts[level] if level < len(amounts) else '0'
                            if amount != '0':
                                upgrade_costs[level][PlayerResource[resource_type].value] = int(amount)
                    
                    building_instance['cost'] = upgrade_costs
                # 解析Activate
                activate_element = building.find('Activate')
                if activate_element is not None:
                    building_instance['activate'] = activate_element
                # 解析Passive
                passive_element = building.find('Passive')
                if passive_element is not None:
                    building_instance['passive'] = passive_element
                # 将建筑实例添加到字典中
                self.buildings[building_id] = building_instance
                
        except Exception as e:
            print(f"Error reading building config: {e}")
            raise
    
    def GetBuildingById(self, id):
        """根据ID获取建筑实例"""
        return self.buildings.get(id, None)
    
    def GetCostById(self, id, level):
        """根据ID获取建筑升级成本"""
        building = self.GetBuildingById(id)
        if building is None:
            return None
        return building['cost'].get(level, None)

    def GetAllBuildings(self):
        """获取所有建筑实例"""
        return self.buildings

    def GetTextById(self, id):
        building = self.GetBuildingById(id)
        common_text = building.get('desc', '')
        activate_text = ''
        if building.get('activate') and building['activate'].find('Desc') is not None:
            activate_text = '激活时: ' + building['activate'].find('Desc').get('text')
        passive_text = ''
        if building.get('passive') and building['passive'].find('Desc') is not None:
            passive_text = '被动时: ' + building['passive'].find('Desc').get('text')
        return common_text, activate_text, passive_text


if __name__ == '__main__':
    main = BuildingFactory()
    main.ReadConfig()
    building = main.GetBuildingById(51)
    print(building)
    print(main.GetCostById(59, 0))
    print(main.GetTextById(51))
    