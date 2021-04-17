from box import Box
from level import Level
from agent import Agent
from box import Box
from color import Color
from location import Location
from action import Action, ActionType


class State(object):
    def __init__(self, level: Level, agents: Agent, boxes: Box, strategy: 'StrategyType'):
        self.__level = level
        self.__agents = agents
        self.__boxes = boxes
        self.__strategy = strategy
        self._hash = None
        
    def __hash__(self):
        if self._hash is None:
            prime = 71
            _hash = 1
            _hash = _hash * prime + hash(tuple (agt for agt in self.__agents))
            _hash = _hash * prime + hash(self.__level)
            self._hash = _hash
        return self._hash
    
    def __apply_action(self):
        pass
    
    def get_expanded_states(self):
        applicable_actions = [
            [
                action for action in Action if self.__is_applicable(agent, action)
            ] for agent in self.__agents
        ]
        
        print(applicable_actions)
        
    def is_goal_state(self) -> 'bool':
        pass
    
    def __is_applicable(self, agent: Agent, action: 'Action') -> 'bool':
        from configuration import StrategyType
        
        # @TODO: checek actions based on strategy type
        if action.type is ActionType.NoOp:
            return True
        
        if action.type is ActionType.Move:
            try:
                location = self.__level.location_from_action(agent.location, action)
                return self.__is_location_free(location)
            except Exception:
                # Location does not exist
                return False

        if action.type in (ActionType.Pull, ActionType.Push):
            try:
                location = self.__level.location_from_action(agent.location, action)
                
                if action.type is ActionType.Pull:
                    return self.__is_location_free(location[0]) and self.__is_location_with_box(location[1], agent.color)
                # Else
                return self.__is_location_free(location[1]) and self.__is_location_with_box(location[0], agent.color)
            except Exception:
                return False

    def __is_conflicting(self, joint_action: '[Action, ...]') -> 'bool':
        pass
    
    def __is_location_with_box(self, location: Location, color: Color):
        # Checks whether location has box of same color
        for box in self.__boxes:
            if box.color == color and box.location == location:
                return True
        return False
    
    def __is_location_free(self, location: Location):
        if not location or location.is_wall:
            return False

        agent_locations = set(agent.location for agent in self.__agents)
        box_locations = set(box.location for box in self.__boxes)
        
        if location in agent_locations or location in box_locations:
            return False
        
        return True
