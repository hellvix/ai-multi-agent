from goal import Goal
from level import Level
from agent import Agent


class State(object):
    def __init__(self, level: Level, agent: Agent):
        self.__level = level
        self.__agent = agent

        self._hash = None
        
    def __hash__(self):
        if self._hash is None:
            prime = 71
            _hash = 1
            _hash = _hash * prime + hash(self.__agent)

            self._hash = _hash
        return self._hash
    
    def apply_action(self):
        pass
    
    def is_goal_state(self) -> 'bool':
        pass
    
    def is_applicable(self, agent: Agent, action: 'Action') -> 'bool':
        pass

    def is_conflicting(self, joint_action: '[Action, ...]') -> 'bool':
        pass

    def is_location_free(self, location: 'Location') -> 'bool':
        pass
