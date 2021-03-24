from level import Level
from action import Action
from configuration import Configuration


globals().update(Action.__members__)


class Controller:
    def __init__(self, configuration: Configuration):
        self.__parse_config__(configuration)
    
    def __parse_config__(self, configuration: Configuration):
        """Parses Configuration into data structure with objects
        """
        self.__level = configuration.build_level()
        self.__agents = configuration.build_agents()
        self.__boxes = configuration.build_boxes()
        self.__goals = configuration.build_goals()
        
    def __spawn_state__(self):
        pass
    
    def deploy(self) -> '[Action, ...]':
        return [
            [MoveS],
            [MoveE],
            [MoveE],
            [MoveS]
        ]
