import sys
import numpy as np

from eprint import deb

from queue import PriorityQueue

from copy import deepcopy

from box import Box
from goal import Goal
from level import Level
from agent import Agent
from color import Color
from location import Location
from action import Action, ActionType


class State(object):
    def __init__(self, level: Level, agents: Agent, boxes: Box, goals: Goal):
        self.__level = level
        self.__agents = agents
        self.__boxes = boxes
        self.__goals = goals
        
        # Attributes
        self._joint_actions = None
        self._hash = None
        self._parent = None
        self._g = 0
        
    @property
    def agents(self):
        return self.__agents
    
    @property
    def boxes(self):
        return self.__boxes
        
    def __hash__(self):
        if self._hash is None:
            prime = 71
            _hash = 1
            _hash = _hash * prime + hash(tuple(self.agents))
            _hash = _hash * prime + hash(tuple(self.boxes))
            _hash = _hash * prime + self._g
            self._hash = _hash
        return self._hash
    
    def __eq__(self, other):
        if not other: return False
        if not isinstance(other, State): 
            raise Exception('Cannot compare State with %s.' % type(other))
        if not np.array_equal(self.agents, other.agents): return False
        if not np.array_equal(self.boxes, other.boxes): return False
        return True
    
    def __lt__(self, other):
        return self.h <= other.h
    
    def extract_actors(self) -> '[Actors, ...]':
        return self.__agents, self.__boxes
    
    def extract_actions(self) -> '[Action, ...]':
        plan = [None for _ in range(self._g)]
        state = self
        while state._joint_actions is not None:
            plan[state._g - 1] = state._joint_actions
            state = state._parent
        return plan
    
    def __penalty_for_placement(self):
        """ Penalizes states where agents are standing where they should not
        such as other agent's goals.
        """
        
        PCONST = 100
        penalty = 0
        
        if self.__boxes.size:
            # Boxes are in their location
            all_boxes_done = sum([box.has_reached() for box in self.__boxes])
            
            if all_boxes_done:
                for agent in self.__agents:
                    other_goals = {loc for loc, goal in self.__goals.items() if goal.color != agent.color}

                    for agent in self.__agents:
                        if agent.location in other_goals:
                            penalty += PCONST
        return penalty
    
    def __box_to_goal_heuristic(self):
        # Distance from box to its destination
        return sum(box.distance(box.destination) for box in self.__boxes if box.destination)
    
    def __agent_to_desire_heuristic(self):
        # Distance from agent to desire (either box or goal)
        return sum(agent.distance(agent.desire.location) for agent in self.__agents)
    
    @property
    def h(self):
        return self._g + \
            self.__agent_to_desire_heuristic() + \
            self.__box_to_goal_heuristic() + \
            self.__penalty_for_placement()
    
    def move_box(self, rboxloc: Location, nloc: Location):
        """Change object in deepcopy
        """
        for nb, _dbox in enumerate(self.__boxes):
            if _dbox.location == rboxloc:
                self.__boxes[nb].move(self.__level.get_location(
                    (nloc.row, nloc.col), translate=True))
                return self.__boxes[nb]
        raise Exception('Cannot find box %s.' % rboxloc)

    def move_agent(self, ragent: Agent, aloc: Location):
        """Change object in deepcopy
        """
        # Get box in the copied state so we don't change the one we are in
        for na, _dagt in enumerate(self.__agents):
            if _dagt.identifier == ragent.identifier:
                self.__agents[na].move(
                    self.__level.get_location((aloc.row, aloc.col), translate=True)
                )
                return self.__agents[na]
        raise Exception('Cannot find agent %s.' % ragent)
    
    def __apply_action(self, joint_actions: '[Action, ...]') -> 'State':
        _state = deepcopy(self)

        for agent, action in joint_actions.items():
            # Get the agent and box location of the executed Action
            original_location = self.__level.location_from_action(agent.location, action)
            move_location = self.__level.location_from_action(agent.location, action, execute=True)
            
            if action.type == ActionType.NoOp:
                pass
            elif action.type == ActionType.Move:
                _state.move_agent(agent, move_location)
            elif action.type in (ActionType.Pull, ActionType.Push):
                if action.type is ActionType.Pull:
                    box_loc = original_location[1]
                    agt_mov_loc = move_location[0]
                    box_mov_loc = move_location[1]
                else:
                    box_loc = original_location[0]
                    agt_mov_loc = move_location[0]
                    box_mov_loc = move_location[1]
                _state.move_agent(agent, agt_mov_loc)
                _state.move_box(box_loc, box_mov_loc)
        
        _state._joint_actions = deepcopy(joint_actions)
        _state._parent = self
        _state._g += 1
        return _state
    
    def get_expanded_states(self) -> '{State, ...}':
        expanded_states = []
        
        agents = self.agents
        applicable_actions = {
            agent: [action for action in Action if self.__is_applicable(agent, action)] for agent in agents
        }
        joint_action = {agent: [] for agent in agents}
        actions_permutation = {agent: 0 for agent in agents}
        num_agents = len(agents)

        while True:
            for agent in agents:
                joint_action[agent] = applicable_actions[agent][actions_permutation[agent]]
            
            expanded_states.append(self.__apply_action(joint_action))

            # Advance permutation.
            done = False
            _cnt = 0
            for agent in agents:
                if actions_permutation[agent] < len(applicable_actions[agent]) - 1:
                    actions_permutation[agent] += 1
                    break
                else:
                    actions_permutation[agent] = 0
                    if _cnt == num_agents - 1:
                        done = True
                _cnt += 1
                
            # Last permutation?
            if done:
                break

        return expanded_states
        
    def is_goal_state(self) -> 'bool':
        
        if self.__boxes.size:
            for box in self.__boxes:
                if box.destination and box.location != box.destination:
                    return False
            return True
        return not sum(agent.distance(agent.desire.location) for agent in self.__agents)
    
    def __is_applicable(self, agent: Agent, action: 'Action') -> 'bool':
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
    
    def __is_location_with_box(self, location: Location, color: Color):
        """Check whether a location has a box of the same color as the agent.
        """
        for box in self.__boxes:
            if box.color == color and box.location == location:
                return True
        return False
    
    def __is_location_free(self, location: Location):
        if not location or location.is_wall:
            return False

        agent_locations = set(agent.location for agent in self.__agents)
        box_locations = set(box.location for box in self.__boxes)
        
        if location in agent_locations.union(box_locations):
            return False
        
        return True
