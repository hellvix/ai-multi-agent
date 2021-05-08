import sys
import time
import memory
import client
import logging
import numpy as np

from queue import PriorityQueue

from copy import deepcopy
from eprint import deb

from box import Box
from goal import Goal
from state import State
from color import Color
from agent import Agent
from level import Level
from action import Action
from location import Location
from desire import DesireType
from configuration import Configuration, StrategyType

from itertools import groupby

log = logging.getLogger(__name__)

globals().update(Action.__members__)


class Controller(object):
    def __init__(self, configuration: Configuration):
        print('Controller initialized.', file=sys.stderr, flush=True)
        log.debug('Controller initialized.')
        
        self.__parse_config__(configuration)
        self.__cached_routes = {}
    
    def __parse_config__(self, configuration: Configuration):
        """Parses Configuration into data structure with objects
        """
        __debug_msg = 'Parsing configuration.'
        print(__debug_msg, file=sys.stderr, flush=True)
        log.debug(__debug_msg)
        
        self.__level, self.__agents, self.__boxes, self.__goals = configuration.build_structure()
        self.__strategy = configuration.strategy_type
        
        __debug_msg = 'Parsing Finished.'
        print(__debug_msg, file=sys.stderr, flush=True)
        log.debug(__debug_msg)
                   
    def __define_initial_destinations(self):
        # Define initial destination for actors
        # Based on these destinations, agents will update their desire
        log.debug("Checking initial destinations...")

        # @ATTENTION: DO NOT CHANGE THE ORDERING BELOW
                
        # 1) First we find destination for the boxes
        for box in self.__boxes:
            box.destination = self.__destination_for_box(box)
            
        # 2) Based on 1, we find goals for the agents
        for agent in self.__agents:
            agent.goals = self.__goal_for_agent(agent)
        
        log.debug("Finished initial destinations.")
            
    def get_box_owner(self, box: 'Box') -> 'Agent':
        for agent in self.__agents:
            if agent.color == box.color:
                return agent
        
        __err = '%s has no owner (?).' % box
        log.error(__err)
        raise Exception(__err)
    
    def __downsize_level(self, agent: 'Agent'):
        """Copy and modify the level according to the route.
        """
        _level = self.__level.clone()
        _goals = self.__goals
        
        agent_locations = {agent.location for agent in self.__agents}
        box_locations = {box.location for box in self.__boxes if box != agent.desire.element}
        goal_locations = {loc for loc, goal in self.__goals.items() if goal.color != agent.color}
        
        layout = deepcopy(_level.layout)
        
        for row in layout:
            for rloc in row:
                if rloc in agent_locations.union(
                    box_locations,
                    goal_locations
                ):
                    rloc.is_wall = True
                    
        _level.__layout = layout
        _agents = deepcopy(np.array([agent]))
        _boxes = deepcopy(np.array([agent.desire.element] if self.__strategy != StrategyType.AGENTS else []))
        
        return _level, _agents, _boxes, _goals
    
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
        box_locations = {box.location: box for box in self.__boxes}
        agent_locations = {agt.location: agt for agt in self.__agents if not agt.equals(agent)}
        _agents = set()
        _boxes = set()
        
        for loc in route:
            if loc.is_wall:
                __err = "The path is blocked by a wall (?). find_route broken?"
                log.error(__err)
                raise Exception(__err)
            
            if loc in box_locations:
                box = box_locations[loc]
                oagt = self.get_box_owner(box)
                _boxes.add(box)
                if not oagt.equals(agent):
                    _agents.add(box_locations[loc])
                
            if loc in agent_locations:
                _agents.add(agent_locations[loc])
            
            if loc in other_routes:
                _agents.add(other_routes[loc])
                    
        __debug_msg = 'Conflicts found: %s' % (_agents.union(_boxes) or 'None')
        log.debug(__debug_msg)
        print(__debug_msg, file=sys.stderr, flush=True)
        
        if _agents or _boxes:
            return list(_agents), list(_boxes)
        
    
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
    
    def __is_location_free(self, location: 'Location', ignoring: {'Location', ...}):
        """Check whether a location is free. As parameter, a list of ignored locations can be given.
        This is useful if we are checking locations systematically, such as in find_route.

        Args:
            location (Location): Location to be checked
            ignoring ([type]): Set of locations to be ignored

        Returns:
            [boolean]: Location status
        """
        # Check whether this location should be ignored
        if location in ignoring: return True
        
        return not location in self.occupied_locations
    
    def __state_search(self, level: Level, agents: [Agent, ...], boxes: [Box, ...], goals: [Goal, ...]):
        """State space for current agent's plan
        """

        frontier = PriorityQueue()
        iterations = 0
        # frontier = set of all leaf nodes available for expansion
        frontier.put((0, State(level, agents, boxes, goals)))
        explored = set()
        
        while True:

            iterations += 1
            if iterations % 100 == 0:
                memory.print_search_status(explored, frontier)

            if memory.get_usage() > memory._max_usage:
                memory.print_search_status(explored, frontier)
                deb('Maximum memory usage exceeded.')
                return None

            # if the frontier is empty then return failure
            if frontier.empty():
                __err = "Could not solve conflicts. Problem infeasible?"
                log.error(__err)
                raise Exception(__err)

            # choose a leaf node and remove it from the frontier
            rank, state = frontier.get()

            # if the node contains a goal state then return the corresponding solution
            if state.is_goal_state():
                return state.extract_actors(), state.extract_actions()

            # add the node to the explored set
            explored.add(state)
            
            # expand the chosen node, adding the resulting nodes to the frontier
            # only if not in the frontier or explored set
            expanded = state.get_expanded_states()

            for n in expanded:
                rnode = n.h, n
                if not rnode in frontier.queue and not n in explored:
                    frontier.put(rnode)
                    
    def __agent_scheduler(self):
        """Define agents order in plan execution.
        Agents with furthest objectives are put further down the queue        
        """
        agents = self.__agents
        _pagts = PriorityQueue()
        _ord_agts = []
        
        _score = 0
        for agt in agents:
            for g in agt.goals:
                # Agents are scheduled ascending 
                # by distance from their location to their goal location
                _score += agt.location.distance(g.location) + g.location.distance(g.destination)
            _pagts.put((_score, agt))

        while not _pagts.empty():
            _, agt = _pagts.get()
            _ord_agts.append(agt)
            
        return _ord_agts
        

    def __planner(self):
        __debug_msg = 'Planner initialized.'
        print(__debug_msg, file=sys.stderr, flush=True)
        log.debug(__debug_msg)

        # Assign route for agents
        agents = self.__agent_scheduler()
        agents_desire = True
        
        while agents_desire:
            # Derive move actions
            for agent in agents:
                __debug_msg = 'Checking desire for Agent %s ...' % agent.identifier
                log.debug(__debug_msg)
                print(__debug_msg, file=sys.stderr, flush=True)
                
                agent.update_desire()

                if not agent.desire.is_sleep_desire():
                    __debug_msg = 'Creating route for Agent %s...' % agent.identifier
                    log.debug(__debug_msg)
                    print(__debug_msg, file=sys.stderr, flush=True)
                    
                    destination = agent.desire.location
                    route = self.__find_route(agent.location, destination)

                    # Update the desire in case boxes are involved
                    if agent.desire.is_box_desire():
                        log.debug("Adapting route and desire locations...")
                        # The agent is tanding too close to where it wants to go
                        if len(route) == 1:
                            route = [agent.location, ]
                            agent.desire.location = agent.location
                        # Avoid sending the last location (box is standing there)
                        else:
                            route = route[:-1]
                            agent.desire.location = route[-1:][0]

                    agent.update_route(route)
                    log.debug("Route for %s is %s." % (agent, agent.current_route))
                    log.debug("Desire location for %s is %s." % (agent, agent.desire.location))
        
            for agent in agents:
                __debug_msg = 'Checking route conflicts for Agent %s...' % agent.identifier
                log.debug(__debug_msg)
                print(__debug_msg, file=sys.stderr, flush=True)
                
                if not agent.desire.is_sleep_desire():
                    log.debug("%s is awake!" % agent)
                    
                    conflicts = self.__check_conflicts(agent)

                    # @TODO: Try to move the agent where the conflict starts
                    log.debug("Systematically generating movements for route %s." % agent.current_route)
                    actions = Controller.generate_move_actions(agent.current_route)
                    agent.update_actions(actions)
                    
                    # Last location from actions
                    last_loc, routes = self.__location_from_actions(agent.location, actions, return_route=True)
                    agent.update_route(routes)
                    log.debug("%s new route is %s." % (agent, agent.current_route))
                    
                    agent.move(last_loc)  # location nearby box
                    log.debug("%s moved to %s." % (agent, last_loc))
                    
                    agent.update_desire()
                    
                    __debug_msg = "Performing state search..."
                    log.debug(__debug_msg)
                    print(__debug_msg, file=sys.stderr, flush=True)
                    
                    list_actors, list_actions = self.__state_search(*self.__downsize_level(agent))
                    state_agents, state_boxes = list_actors
                    
                    __debug_msg = 'Extracting plan...'
                    log.debug(__debug_msg)
                    print(__debug_msg, file=sys.stderr, flush=True)
                    
                    # Extracting actions
                    agt_actions = []
                    for acts in list_actions:
                        for agt, action in acts.items():
                            if agt.equals(agent):
                                agt_actions.append(action)
                                
                    # Updating results from state
                    for a in state_agents:
                        for agt in self.__agents:
                            if a.equals(agt):
                                agt.move(a.location)
                                agent.update_desire()
                                log.debug("%s moved to %s." % (agt, agt.location))

                    # Moving boxes from result in state
                    for b in state_boxes:
                        for box in self.__boxes:
                            if b.equals(box):
                                box.move(b.location)
                                log.debug("%s moved to %s." % (box, box.location))

                    agent.update_actions(agt_actions)
                    
                    if conflicts:
                        self.__make_agents_wait(agent, conflicts[0])
                    
            # Are agents satisfied?
            agents_desire = sum([not agent.desire.is_sleep_desire() for agent in agents])
        # DONE
        
        __debug_msg = 'Solving level...'
        log.debug(__debug_msg)
        print(__debug_msg, file=sys.stderr, flush=True)
        
        self.__equalize_actions()
        client.Client.send_to_server(self.__assemble())
        
    def __location_from_actions(self, initial_loc: 'Location', actions: '[Action, ...]', return_route=False):
        plan = []
        last_loc = initial_loc
        
        for act in actions:
            last_loc = self.__level.location_from_action(last_loc, act)
            plan.append(last_loc)
        
        if return_route: return last_loc, plan

        return last_loc
        
    def __equalize_actions(self):
        """ Usually called after generating all actions for the agents. 
        This method ensures all agents have the same length in actions. 
        The difference is filled with NoOp.
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
        
        for other_agt in agents:
            sz_dif = len(agent.actions) - len(other_agt.actions)
            if sz_dif > 0:
                other_agt.update_actions([Action.NoOp for _ in range(sz_dif)])

    def __assemble(self) -> [Action, ...]:
        """Gather agents actions so they can be streamlined to the server

        Returns:
            [Action, ...]: Agent actions
        """
        
        # Sanity check (actions must have the same length)
        sizes = [len(agent.actions) for agent in self.__agents]  # Size of all actions
        gsiz = groupby(sizes)

        if next(gsiz, True) and next(gsiz, False):
            __err = "List of Actions for agents does not have the same size."
            log.error(__err)
            raise Exception(
                __err
            )
        
        acts_sz = len(self.__agents[0].actions)  # number of actions
        f_route = [[] for _ in range(acts_sz)]
        
        for act_index in range(acts_sz):
            for agent in self.__agents:
                f_route[act_index].append(agent.actions[act_index])
        
        return f_route

    def deploy(self) -> [Action, ...]:
        # Code goes here
        log.debug("Deploying...")
        self.__define_initial_destinations()
        self.__planner()
        log.debug("Finished deploying.")
    
    def __goal_for_agent(self, agent: Agent) -> [Location, ...]:
        """Return the location of the pre-defined level goals for the given agent (if exists).
        """
        _goals = PriorityQueue()
        
        if self.__strategy == StrategyType.AGENTS:
            for loc, goal in self.__goals.items():
                if goal.color == agent.color:
                    _goals.put((agent.distance(loc), goal))
        else:
            for box in self.__boxes:
                if box.destination and box.color == agent.color:
                    _goals.put((agent.distance(box.location), box))
        
        f_goal = []        
        while not _goals.empty():
            f_goal.append(_goals.get()[1])
        return f_goal

    def __destination_for_box(self, box: Box) -> Location:
        log.debug("Finding destination for boxes.")
        
        _dests = PriorityQueue()
        other_destinations = set(box.destination for box in self.__boxes if box.destination)

        for loc, goal in self.__goals.items():
            if not loc in other_destinations and goal.identifier == box.identifier:
                dist = box.location.distance(goal.location)
                _dests.put((dist, loc))
                
                log.debug("%s destination is %s, with distance %d." % (box, goal, dist))
        
        log.debug("Done finding destination for boxes.")
        # If a box has more than one destination we only care about the closest
        # @TODO: Can be improved
        if not _dests.empty(): return _dests.get()[1]
        return None

    def __find_route(self, start: Location, end: Location):
        """ Implementatoin of Greedy BFS
        Finds a path from A to B.
        
        Author: Shanna
        Co-author: Elvis (heapq && route caching)

        Args:
            start (Location): Start location
            end (Location): End location

        Returns:
            [Location]: [Location, ...]
        """
        
        class Node(object):
            location = None
            parent = None
            
            def __init__(self, location, parent):
                self.location = location
                self.parent = parent
            
            def __lt__(self, other):
                return self.location < other.location
        
        frontier = PriorityQueue()
        frontier.put((start.distance(end), Node(start, None)))
        explored = set()
        _rhash = hash((start, end))
        _ignored = {start, end}
        
        try:
            return self.__cached_routes[_rhash]
        except KeyError:
            pass

        while True:

            if frontier.empty():
                __err = "Could not find route from %s to %s." % (start, end)
                log.error(__err)
                raise Exception(__err)

            _, node = frontier.get()
            visited = node.location

            if visited == end:
                pnode = node.parent
                path = [visited, ]
                
                while pnode:
                    path.append(pnode.location)
                    pnode = pnode.parent
                    
                # Revert
                _r = path[::-1]
                # Ignore the first position (start)
                #_r = _r[1:]
                self.__cached_routes.update({_rhash: _r})
                self.__find_route(start, end)
                return _r

            explored.add(visited)
            expanded = visited.neighbors
            
            for loc in expanded:
                if self.__is_location_free(loc, _ignored):
                    nnode = loc.distance(end), Node(loc, node)
                    if not nnode in frontier.queue and not loc in explored:
                        frontier.put(nnode)

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
                __err = "Typo error: Agent cannot move 2 steps in y (rows) ! %s " % yval
                log.error(__err)
                raise Exception(__err)

        for xval in range(len(x) - 1):

            if x[xval + 1] == x[xval] + 1:
                path_x.append(MoveE)

            elif x[xval + 1] == x[xval] - 1:
                path_x.append(MoveW)

            elif x[xval + 1] == x[xval]:
                path_x.append('same x')

            else:
                __err = 'Typo error: Agent cannot move 2 steps in x (columns) ! %s ' % xval
                log.error(__err)
                raise Exception(__err)

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
                __err = 'Typo error: Agent cannot move diagonally / in both directions ! y: %s, x: %s' % (i, j)
                log.error(__err)

        return path_y
