import sys
import time
import memory
import client

from queue import PriorityQueue

from copy import deepcopy

from box import Box
from eprint import deb
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
        self.__strategy = configuration.strategy_type
                   
    def __define_initial_destinations(self):
        # Define initial destination for actors
        # Based on these destinations, agents will update their desire

        for agent in self.__agents:
            agent.goals = self.__destination_for_agent(agent)
            
        for box in self.__boxes:
            box.destination = self.__destination_for_box(box)
            box.set_current_route(self.__find_path(box.location, box.destination))
            
    def get_box_owner(self, box: 'Box') -> 'Agent':
        for agent in self.__agents:
            if agent.color == box.color:
                return agent
        raise Exception('Box has no owner (?).')
    
    def __check_conflicts(self, agent: Agent):
        """Check for conflicts with the current agent's route.

        Args:
            agent (Agent): the agent to have its route checked.

        Raises:
            Exception: Exception if by mistake the given route has a wall.

        Returns:
            [list]: An empty list of agents with conflicting interests with the current route
        """
        route = agent.current_route
        other_routes = {loc: agt for agt in self.__agents for loc in agt.current_route if not agt.equals(agent)}
        box_locations = {box.location: self.get_box_owner(box) for box in self.__boxes}
        agent_locations = {agt.location: agt for agt in self.__agents if not agt.equals(agent)}
        _actors = set()
        
        for loc in route:
            if loc.is_wall:
                raise Exception("The path is blocked by a wall (?). find_route broken?")
            
            if loc != agent.location:
                if loc in box_locations:
                    oagt = box_locations[loc]
                    if not oagt.equals(agent):
                        _actors.add(box_locations[loc])
                    
                if loc in agent_locations:
                    _actors.add(agent_locations[loc])
                
                if loc in other_routes:
                    _actors.add(other_routes[loc])
                    
        deb('Conflicts found: ', _actors)
        return _actors
    
    def __is_goal(self, location: 'Location'):
        """Check whether the given position is a goal

        Returns:
            [bool]: [whether the position is a goal]
        """
        return location in {loc for loc, goal in self.__goals.items()}
    
    @property
    def occupied_locations(self):
        goal_loc = {loc for loc, goal in self.__goals.items()}
        agent_loc = {agent.location for agent in self.__agents}
        box_loc = {box.location for box in self.__boxes}
        
        return goal_loc.union(
            agent_loc,
            box_loc
        )
    
    def __is_location_free(self, location: 'Location'):
        return not location in self.occupied_locations
    
    def __downsize_level(self, agent: Agent):
        """Copy and modify the level according to the route.
        
        We blur out any location that:
            1) is not in the route;
            2) is not is a neighbor location in the route;
            3) is not a wall;
            4) is not a goal.
            
        The reason for this is to give the search a sub-set of the level,
        so the search space is reduced. The reason not to blurry everything but the route
        is that we want to ensure the agent has enough space to manouver in case this is necessary.
        
        Example with path from [L1,2, L2,2, L2,3] (0-based indexes):
        
        [x, x, x, x, x, x]
        [x, -, -, -, x, x]
        [-, -, -, -, -, x]
        [x, -, -, -, x, x]
        [x, x, x, x, x, x]
        
        x == blurred
        
        At this point we assume the route given is achievable (__check_conflicts was called).
        
        Args:
            route ([Location, ...]): List of locations leading from point A to B.
            
        Returns:
            (Level): modified copy of the given level.
        """
        
        _level = self.__level.clone()
        
        # SETS THAT DO NOT BECOME WALLS
        boxes_neighbors = {
            loc for box in self.__boxes for loc in box.location.neighbors if box.color == agent.color
        }
        boxes_routes = {
            loc for box in self.__boxes for loc in box.current_route if box.color == agent.color
        }
        # Locations around goals the agent own. If another goal is found
        # it must belong to the agent
        goals_neighbors = {
            loc for loc, goal in self.__goals.items() for loc in goal.location.neighbors \
                if goal.color == agent.color and not self.__is_goal(loc)
        }
        # Locations around the agent
        agt_neighbors = {
            loc for loc in agent.location.neighbors
        }
        current_route = {
            loc for loc in agent.current_route
        }
        
        for row in _level.layout:
            for loc in row:
                # Location is not:
                # 1) in the route;
                # 2) is a neighbor location in the route;
                # 3) is not already a wall.
                # 4) Is not a goal
                if not (
                    loc in boxes_neighbors.union(
                        boxes_routes,
                        goals_neighbors,
                        agt_neighbors,
                        current_route
                    ) or
                    loc.is_wall
                ):
                    loc.is_wall = True
        return _level
    
    def __solve_conflicts(self, level: Level, agents: [Agent, ...], boxes: [Box, ...]):
        """Solve conflicts in agents' routes using state space search
        """

        frontier = PriorityQueue()
        iterations = 0
        # frontier = set of all leaf nodes available for expansion
        frontier.put((0, State(level, agents, boxes)))
        explored = set()
        
        while True:

            iterations += 1
            if iterations % 10000 == 0:
                memory.print_search_status(explored, frontier)

            if memory.get_usage() > memory._max_usage:
                memory.print_search_status(explored, frontier)
                deb('Maximum memory usage exceeded.')
                return None

            # if the frontier is empty then return failure
            if frontier.empty():
                raise Exception('Could not solve conflicts. Problem infeasible?')

            # choose a leaf node and remove it from the frontier
            rank, state = frontier.get()

            # if the node contains a goal state then return the corresponding solution
            if state.is_goal_state():
                return state.extract_actions()

            # add the node to the explored set
            explored.add(state)
            
            # expand the chosen node, adding the resulting nodes to the frontier
            # only if not in the frontier or explored set
            expanded = state.get_expanded_states()

            for n in expanded:
                if not ((n.hrt_value, n) in frontier.queue or n in explored):
                    frontier.put((n.hrt_value, n))

    def __planner(self):
        print('Planner initialized.', file=sys.stderr, flush=True)

        # Assign route for agents
        agents = self.__agents
        boxes = self.__boxes
        conflicts = {
            'agents': [],
            'boxes': []
        }

        # Computing route for each agent desire
        print('Generating initial plan for agents...', file=sys.stderr, flush=True)
        for agent in agents:
            agent.update_desire()

            if agent.desire_type == DesireType.MOVE_TO_GOAL:
                destination = agent.desire.location
                route = self.__find_path(agent.location, destination)
                
                if agent.desire.is_box_desire():
                    # Avoid sending the last location (box is standing there)
                    route = route[:-1]
                    agent.desire.location = route[-1:][0]
                    
                agent.update_route(route)
        
        for agent in agents:
            print('Checking conflicts for Agent %s...' % agent.identifier, file=sys.stderr, flush=True)
            
            if agent.has_route():
                actions = Controller.generate_move_actions(agent.current_route)
                agent.update_actions(actions)
                agent.move(agent.desire.location)  # location nearby box
                conflicts = self.__check_conflicts(agent)

                if conflicts:
                    print('Doing state-space search...', file=sys.stderr, flush=True)
                    _level = self.__downsize_level(agent)
                    list_actions = self.__solve_conflicts(
                        _level,
                        np.array([agent]),
                        deepcopy(np.array([box for box in self.__boxes if box.color == agent.color]))
                    )
                    print('Extracting plan...', file=sys.stderr, flush=True)
                    # Extracting actions
                    agt_actions = []
                    for acts in list_actions:
                        for agt, action in acts.items():
                            if agt.equals(agent):
                                agt_actions.append(action)
                    agent.update_actions(agt_actions)

                    # @TODO: Make only the agents that are in the path wait
                    self.__make_agents_wait(agent, conflicts)
                print('Solving level...', file=sys.stderr, flush=True)
                
        self.__equalize_actions()
        client.Client.send_to_server(self.__assemble())
    
    def __equalize_actions(self):
        """ Usually called after generating actions for the agents. 
        This method ensures all agents have the same length in actions. 
        The difference is filled with NoOp actions.
        """
        # Equalize actions size
        agents = self.__agents

        for agent in agents:
            act_sz = len(agent.actions)

            for other_agt in agents:
                if not other_agt.equals(agent):
                    sz_diff = act_sz - len(other_agt.actions)
                    # Actions of current are greater
                    if sz_diff > 0:
                        other_agt.update_actions(
                            [Action.NoOp for _ in range(sz_diff)]
                        )
        return
    
    def __make_agents_wait(self, agent: Agent, agents: {Agent, ...}):
        """Insert NoOps for agents. 
        Handful when one agent is executing its actions and the others have to wait.

        Args:
            agent (Agent): The agent we derive the waiting from.
        """
        
        for other_agt in self.__agents:
            if not other_agt.equals(agent) and other_agt in agents:
                sz_dif = len(agent.actions) - len(other_agt.actions)
                if sz_dif > 0:
                    other_agt.update_actions([Action.NoOp for _ in range(sz_dif)])
        return

    def __assemble(self) -> [Action, ...]:
        """Gather agents actions so they can be streamlined to the server

        Returns:
            [Action, ...]: Agent actions
        """
        
        # Sanity check (routes must have the same length)
        sizes = [len(agent.actions) for agent in self.__agents]  # Size of all actions
        deb(sizes)
        gsiz = groupby(sizes)

        if next(gsiz, True) and next(gsiz, False):
            raise Exception(
                'List of Actions for agents does not have the same size.'
            )
        
        acts_sz = len(self.__agents[0].actions)  # number of actions
        f_route = [[] for _ in range(acts_sz)]
        
        for act_index in range(acts_sz):
            for agent in self.__agents:
                f_route[act_index].append(agent.actions[act_index])
        
        return f_route

    def deploy(self) -> [Action, ...]:
        # Code goes here
        self.__define_initial_destinations()
        self.__planner()
        
    def __destination_for_agents(self) -> [Location, ...]:
        return {a: self.__destination_for_agent(a) for a in self.__agents}
    
    def __destination_for_agent(self, agent: Agent) -> [Location, ...]:
        """Return the location of the pre-defined level goals for the given agent (if exists).
        """
        _goals = set()
        if self.__strategy == StrategyType.AGENTS:
            for loc, goal in self.__goals.items():
                if goal.color == agent.color:
                    _goals.add(goal)
        else:
            for box in self.__boxes:
                if box.color == agent.color:
                    _goals.add(box)
        return _goals

    def __destination_for_box(self, box: Box) -> Location:
        _dests = {loc for loc, goal in self.__goals.items() if goal.identifier == box.identifier}
        
        # If a box has more than one destination we only care about one
        if _dests: return _dests.pop()

        return None

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
    def generate_move_actions(path: '[Location, ...]') -> '[Actions, ...]':
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
