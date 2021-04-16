import sys
import time
import memory

from queue import PriorityQueue

from copy import deepcopy

from state import State
from color import Color
from agent import Agent
from level import Level
from action import Action
from location import Location
from desire import DesireType
from configuration import Configuration, StrategyType

from itertools import groupby

import numpy as np


globals().update(Action.__members__)


class Controller(object):
    def __init__(self, configuration: Configuration):
        print('Controller initialized.', file=sys.stderr, flush=True)
        self.__parse_config__(configuration)
    
    def __parse_config__(self, configuration: Configuration):
        """Parses Configuration into data structure with objects
        """
        self.__level, self.__agents, self.__boxes, self.__goals = configuration.build_structure()
        self.__strategy = configuration.race_type
                   
    def __define_initial_goals(self):
        # Define initial goal for the agents
        # Based on these goals, the agents are going to update their desire

        for agent in self.__agents:
            agent.goals = self.__goals_for_agent(agent)
            
    def __is_plan_solid(self, agent: Agent, plan: [Location, ...]):
        """Check whether a given plan is achievable for the given agent
        """

        # Check the position of all agents, ignoring the one making the plan
        agent_locs = set(agt.location for agt in self.__agents if agent != agt)
        box_locs = set(box.location for box in self.__boxes)
        
        for loc in plan:
            # Check if the location is a wall (shouldn't be, but dobble checking)
            if loc.is_wall:
                return False

            # Check if there is something in the way
            if loc in agent_locs or loc in box_locs:
                return False

        return True
    
    def __adapt_level(self, plan: [[Location, ...], ...]):
        """Copy and modify the level according to the plan.
        
        We blur out any location that:
            1) is not in the plan;
            2) is not is a neighbor location in the plan;
            3) is not a wall.
            
        The reason for this is to give the search a sub-set of the level,
        so the search space is reduced. The reason not to blurry everything but the plan
        is that we want to ensure the agent has enough space to manouver in case this is necessary.
        
        Example with path from [L1,2, L2,2, L2,3] (0-based indexes):
        
        [x, x, x, x, x, x]
        [x, -, -, -, x, x]
        [-, -, -, -, -, x]
        [x, -, -, -, x, x]
        [x, x, x, x, x, x]
        
        x == blurred
        
        At this point we assume the plan given is achievable (__is_plan_solid was called).
        
        Args:
            plan ([Location, ...]): List of locations leading from point A to B.
            
        Returns:
            (Level): modified copy of the given level.
        """
        _level = self.__level.clone()
        all_neighbors = set(loc for loc in plan for loc in loc.neighbors)

        for row in _level.layout:
            for loc in row:
                # Location is not:
                # 1) in the plan;
                # 2) is a neighbor location in the plan;
                # 3) is not already a wall.
                if not loc in plan and not loc in all_neighbors and not loc.is_wall:
                    loc.is_wall = True

        return _level
    
    def __solve_conflicts(self, agents: [Agent, ], level: Level):
        """Solve conflicts in agents' plans
        """
        
        start_time = time.perf_counter()        
        frontier = PriorityQueue()
        iterations = 0
        # frontier = set of all leaf nodes available for expansion
        frontier.put((0, State(level, agents, self.__strategy)))
        explored = set()

        while True:

            iterations += 1
            if iterations % 10000 == 0:
                memory.print_search_status(explored, frontier)

            if memory.get_usage() > memory.max_usage:
                print_search_status(explored, frontier)
                print('Maximum memory usage exceeded.', file=sys.stderr, flush=True)
                return None

            # if the frontier is empty then return failure
            if frontier.empty():
                return None

            # choose a leaf node and remove it from the frontier
            state = frontier.get()[1]

            # if the node contains a goal state then return the corresponding solution
            if state.is_goal_state():
                return state.extract_plan()

            # add the node to the explored set
            explored.add(state)

            # expand the chosen node, adding the resulting nodes to the frontier
            # only if not in the frontier or explored set
            expanded = state.get_expanded_states()

            for n in expanded:
                if not (n in frontier or n in explored):
                    frontier.put(n)

    def __planner(self):
        # Assign plan for agents
        agents = self.__agents

        # @TODO: Improve which agent gets picked up first
        # @TODO: Allow parallelism between agent actions
        for agent in agents:
            if agent.desire_type == DesireType.MOVE_TO_GOAL:
                destination = agent.desire.location
                plan = self.__find_path(agent.location, destination)

                if self.__is_plan_solid(agent, plan):
                    # Allow the agent to execute its plan
                    agent.update_plan(plan)
                    actions = agent.derive_actions()
                    act_sz = len(actions)
                    agent.update_actions(actions)
                    agent.move(destination)
                    
                    # Update other agents' actions by making them wait
                    # @TODO: If no conflict, then agents can perform things in parallel
                    # @TODO: Improve. What to do while one agent is fulfilling its desire?
                    for other_agt in agents:
                        if other_agt != agent:
                            other_agt.update_plan([Action.NoOp for _ in range(act_sz)])
                            other_agt.update_actions()
                else:
                    # Conflicts
                    # @TODO: Get a list of agents and their plans
                    plan = self.__solve_conflicts(
                        deepcopy(agents),
                        self.__adapt_level(plan)
                    )
        return self.__assemble()

    def __assemble(self) -> [Action, ...]:
        """Gather agents actions

        Returns:
            [Action, ...]: Agent actions
        """
        
        # Sanity check (plans must have the same length)
        sizes = [len(agent.actions)
                 for agent in self.__agents]  # Size of all actions
        gsiz = groupby(sizes)

        if next(gsiz, True) and next(gsiz, False):
            raise Exception(
                'List of Actions for agents does not have the same size.'
            )
        
        acts_sz = len(self.__agents[0].actions)  # number of actions
        f_plan = [[] for _ in range(acts_sz)]
        
        for action in range(acts_sz):
            for agent in self.__agents:
                f_plan[action].append(agent.actions[action])
        
        return f_plan

    def deploy(self) -> [Action, ...]:
        print('Solving level...', file=sys.stderr, flush=True)
        
        # Code goes here
        self.__define_initial_goals()
        self.__planner()
        
        return self.__assemble()

    def __goals_for_agents(self) -> [Location, ...]:
        return {a: self.__goals_for_agent(a) for a in self.__agents}

    def __goals_for_agent(self, agent: Agent) -> [Location, ...]:
        """Return the location of the pre-defined level goals for the given agent (if exists).
        
        Args:
            agent (Agent): the agent

        Raises:
            Exception: If no goal exists for the agent.

        Returns:
            [Location, ...]: List of location objects
        """
        _goals = set()
        
        for row in self.__level.layout:
            for loc in row:
                
                if not loc.is_wall:
                    # If the location exists in the list with goals
                    # we append it to _goals
                    try:
                        goal = self.__goals[loc]
                        
                        if goal.color == agent.color:
                            # Race
                            if '0' <= goal.identifier <= '9':
                                if goal.identifier == agent.identifier:
                                    _goals.add(goal)
                            # Boxes
                            else:
                                # @TODO: function to calculate distance from agent to goal
                                # So it is sorted by the distance, therefore creating a priority
                                _goals.add(goal)
                            
                    except KeyError:
                        # Will fail if the location is not a goal
                        pass
        
        return _goals

    def __find_path(self, start: Location, end: Location):
        """ Shanna's implementatoin of A*.
        Finds the shorted path from A to B.
        
        Author: Shanna

        Args:
            start (Location): Start location
            end (Location): End location

        Returns:
            [Location]: [Location, ...]
        """
        open_list = []
        closed_list = []
        parent_list = [] # (child, parent)

        current_node = (start, 0)
        open_list.append(current_node)

        while len(open_list) > 0:

            current_node = open_list[0]
            for item in open_list:
                if item[1] < current_node[1]:
                    current_node = item

            open_list.remove(current_node)
            closed_list.append(current_node)

            if current_node[0] == end:

                path = []
                current = current_node[0]
                while current is not start:
                    path.append(current)
                    current = [node for node in parent_list if node[0] == current][0][1]

                path.append(start)
                return path[::-1]
                
            for child in current_node[0].neighbors:  

                parent_list.append((child, current_node[0]))          

                if child in [i[0] for i in closed_list]:
                    continue

                if child.is_wall:
                    print('Path: {}'.format('WALL ALERT! retard'), file=sys.stderr, flush=True)
                    continue
                    
                child_h = abs(child.col - end.col) + abs(child.row - end.row)
                child_g = current_node[1] - child_h + 1
                child_f = child_h + child_g
                
                if child in [i[0] for i in open_list] and child_f > [node for node in open_list if node[0] == child][0][1]:
                    continue
                
                open_list.append((child, child_f))

    @staticmethod
    def generate_move(path: '[Location, ...]') -> '[Actions, ...]':
        """Generate actions based on given locations.

        Author: dimos

        Args:
            path ([type]): list of locations

        Returns:
            [type]: list of actions
        """

        y = map(lambda yval: yval.row, path)
        y = list(y)

        x = map(lambda xval: xval.col, path)
        x = list(x)

        path_x = []
        path_y = []

        for yval in range(len(y) - 1):

            if y[yval + 1] == y[yval] + 1:
                path_y.append(MoveS)

            elif y[yval + 1] == y[yval] - 1:
                path_y.append(MoveN)

            elif y[yval + 1] == y[yval]:
                path_y.append('same y')

            else:
                raise Exception('Typo error: Agent cannot move 2 steps in y (rows) !')

        for xval in range(len(x) - 1):

            if x[xval + 1] == x[xval] + 1:
                path_x.append(MoveE)

            elif x[xval + 1] == x[xval] - 1:
                path_x.append(MoveW)

            elif x[xval + 1] == x[xval]:
                path_x.append('same x')

            else:
                raise Exception('Typo error: Agent cannot move 2 steps in x (columns) !')

        for i, j in zip(path_y, path_x):

            if i == 'same y' and j != 'same x':
                index=path_y.index(i)
                index2=path_x.index(j)
                path_y[index]=path_x[index2]

            elif i == 'same y' and j == 'same x':
                index=path_y.index(i)
                path_y[index]=(NoOp)

            elif i != 'same y' and j == 'same x':
                pass

            else:
                raise Exception('Typo error: Agent cannot move diagonally / in both directions !')

        return path_y
