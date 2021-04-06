from level import Level
from agent import Agent
from Location import Location


class State(object):
    def __init__(self, level: Level, agents: '[Agent, ...]', boxes: '[Box, ...]', goals: '[Location, ...]'):
        pass
    
    def is_goal_state(self) -> 'bool':
        pass
    
    def is_applicable(self, agent: Agent, action: Action) -> 'bool':
        pass

    def is_conflicting(self, joint_action: '[Action, ...]') -> 'bool':
        pass

    def is_location_free(self, location: Location) -> 'bool':
        pass
