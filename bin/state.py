from level import Level
from agent import Agent
from action import Action
from location import Location


class State(object):
    def __init__(self, level: Level, agents: '[Agent, ...]', boxes: '[Box, ...]', goals: '[Location, ...]'):
        self.__level = level
        self.__agents = agents
        self.__boxes = boxes
        self.__goals = goals

        self.__gl_reach = len(goals)  # Number of unreached goals
        
        self._hash = None
        
    def __hash__(self):
        if self._hash is None:
            prime = 31
            _hash = 1
            _hash = _hash * prime + hash(tuple(self.__agents))
            _hash = _hash * prime + hash(tuple(self.__goals))

            self._hash = _hash
        return self._hash
    
    def is_goal_state(self) -> 'bool':
        pass
    
    def is_applicable(self, agent: Agent, action: Action) -> 'bool':
        pass

    def is_conflicting(self, joint_action: '[Action, ...]') -> 'bool':
        pass

    def is_location_free(self, location: Location) -> 'bool':
        pass
