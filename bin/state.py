from box import Box
from level import Level
from agent import Agent
from color import Color
from location import Location
from action import Action, ActionType


class State(object):
    def __init__(self, level: Level, agents: Agent, strategy: 'StrategyType'):
        self.__level = level
        self.__agents = agents
        # This will limit actions
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
        
    def is_goal_state(self) -> 'bool':
        pass
    
    def __is_applicable(self, agent: Agent, action: 'Action') -> 'bool':
        from configuration import StrategyType
        
        # @TODO: checek actions based on strategy type
        if action.type is ActionType.NoOp:
            return True

        if action.type in (ActionType.Pull, ActionType.Push, ActionType.Move):
            try:
                location = self.__level.location_from_action(agent.location, action)
            except Exception:
                # Location does not exist
                return False
        
            if action.type is ActionType.Move:
                return self.__is_location_free(location)
            
            elif action.type in (ActionType.Pull, ActionType.Push):
                location = self.__level.location_from_action(agent.location, action)
                
                print("@@@ DEBVUG@ FROM ", agent.location, " PERFORM ", action," result ", location)
                
                if action.type is ActionType.Pull:
                    # Pull
                    # 1) The neighbouring cell of the agent
                    # in direction <move-dir-agent> is currently free
                    # 2) The neighbouring cell of the agent i the opposite direction
                    # of <move-dir-box> contains B (a box) of the same color as the agent
                    # (N and S are opposite directoins of each other, the same for E and W)
                    return self.__is_location_free(location[0]) and self.__is_location_with_box(location[1], agent.color)
                elif action.type is ActionType.Push:
                    # Push
                    # 1) The neighbouring cell of the agent in direction <move-dir-agent> constains
                    # B (a box) of the same color as the agent
                    # 2) The neighbouring cell of B (a box) in directoin <move-dir-box> is currently free
                    return self.__is_location_free(location[1]) and self.__is_location_with_box(location[0], agent.color)

    def __is_conflicting(self, joint_action: '[Action, ...]') -> 'bool':
        pass
    
    def __is_location_with_box(self, location: Location, color: Color):
        # @TODO: Change box reference here
        for box in []:
            if box.color == color and box.location == location:
                return True
        return False
    
    def __is_location_free(self, location: Location):
        if not location or not location.is_wall:
            return False

        agent_locations = set(agent.location for agent in self.__agents)
        # @TODO: Change box reference here
        box_locations = set(box.location for box in [])
        
        if location in agent_locations or location in box_locations:
            return False
        
        # @TODO: Check if location is free from boxes
        return True
