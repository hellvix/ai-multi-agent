import sys
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
from agent import Agent
from level import Level
from action import Action
from location import Location
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
        self.__rev_cnfs = {a: [] for a in self.__agents}
    
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
            _d = self.__destination_for_box(box)
            box.destination = self.__destination_for_box(box)
            if _d: box.update_route(self.__find_route(box.location, _d))
            
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
    
    def __adapt_level(self, agent: 'Agent', conflicts=None):
        """Copy and modify the level according to the route.
        """
        __a = {agent, }
        __b = {agent.desire.element, } if agent.desire.is_box_desire() else set()
        
        if conflicts:
            __a = __a.union(conflicts[0])
            __b = __b.union(conflicts[1])
        
        _level = self.__level.clone()
        _agents = deepcopy(np.array(list(__a)))
        _boxes = deepcopy(np.array(list(__b)))
        _goals = self.__goals
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

        other_routes = {}
        
        for agt in self.__agents:
            if agt.current_route and not agt.equals(agent):
                for _r in agt.current_route:
                    other_routes[_r] = agt
        
        box_locations = {box.location: box for box in self.__boxes}
        agent_locations = {agt.location: agt for agt in self.__agents if not agt.equals(agent)}
        _agents = set()
        _boxes = set()
        
        for loc in route:
            if loc.is_wall:
                __err = "%s is blocked by a wall. find_route broken?" % loc
                log.error(__err)
                raise Exception(__err)
            
            if loc in box_locations:
                box = box_locations[loc]
                oagt = self.get_box_owner(box)
                
                _boxes.add(box)
                if not oagt.equals(agent):
                    _agents.add(oagt)
                
            if loc in agent_locations:
                _agents.add(agent_locations[loc])
            
            if loc in other_routes:
                _agents.add(other_routes[loc])
                    
        __debug_msg = 'Conflicts found for %s: %s' % (agent, _agents.union(_boxes) or 'None')
        log.debug(__debug_msg)
        print(__debug_msg, file=sys.stderr, flush=True)

        if _agents or _boxes:
            return list(_agents), list(_boxes)
        
    def __route_sweeper(self, route: ['Location', ...], ignore=set()):
        """Given a route, check whether something is standing in it.

        Args:
            route ([Location]): the route
            ignore ([Actor]): In case any actor should be ignored from it

        Returns:
            [{}]: a set with the actors in the route
        """
        _alocs = {agent.location: agent for agent in self.__agents}
        _blocs = {box.location: box for box in self.__boxes}
        _alocs.update(_blocs)
        _m = []
        
        for _l in route:
            if _l in _alocs: 
                _a = _alocs[_l]
                if ignore:
                    if _a not in ignore:
                        _m.append(_a)
                else:
                    _m.append(_a)
                    
                __debug_msg = 'Actor %s found on route %s.' % (_a, route)
                print(__debug_msg, file=sys.stderr, flush=True)
                log.debug(__debug_msg)
        return _m
    
    def __schedule_obstructions(self, obstructions):
        """Given a list of obstructions, find out what to do with it.
        """
        for _o in obstructions:
            if isinstance(_o, Box):
                owner = self.get_box_owner(_o)
                if not _o.destination:
                    _o.destination = self.__level.get_location(
                        (_o.location.row + 2, _o.location.col),
                        translate=True
                    ) # WHERE_PUT_BOX_GOES HERE
                owner.reschedule_desire(_o)  # update_desire gets called inside
                owner.update_route(self.__find_route(owner.location, owner.desire.location))
                
                __debug_msg = 'Rescheduling desire for Agent %s. New desire is %s.' % (owner.identifier, owner.desire)
                print(__debug_msg, file=sys.stderr, flush=True)
                log.debug(__debug_msg)
            else:
                # Should find out where to put the agent
                # @TODO: recompute their route too
                pass
                
            obstructions.remove(_o)
    
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
            if iterations % 50 == 0:
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
                if not (rnode in frontier.queue or n in explored):
                    frontier.put(rnode)
                    
    def __agent_scheduler(self):
        """Define agents order in plan execution.
        Agents with furthest objectives are put further down the queue        
        """
        agents = self.__agents
        _pagts = PriorityQueue()
        _ord_agts = []
        
        for agt in agents:
            _score = 0
            for g in agt.goals:
                # Agents are scheduled ascending 
                # by distance from their location to their goal location
                _score += agt.location.distance(g.location)
                
                if hasattr(g, 'destination'):
                    _score +=  g.location.distance(g.destination)

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
            to_move = []
            
            for agent in agents:
                # Create desire from the goals
                agent.update_desire()
                
                __debug_msg = 'Desire for agent Agent %s is %s.' % (agent.identifier, agent.desire)
                log.debug(__debug_msg)
                print(__debug_msg, file=sys.stderr, flush=True)

                if not agent.desire.is_sleep_desire():
                    log.debug("%s is awake! Desire is %s." % (agent, agent.desire))
                    __debug_msg = 'Creating preliminary route for Agent %s...' % agent.identifier
                    log.debug(__debug_msg)
                    print(__debug_msg, file=sys.stderr, flush=True)
                    
                    destination = agent.desire.location
                    agent.update_route(self.__find_route(agent.location, destination))
                    
                    # Check whether something is on this route and add to solve it later
                    to_move.extend(self.__route_sweeper(agent.current_route, ignore={agent, }))
                    
                    log.debug("Route for %s is %s and desire is %s " % (agent, agent.current_route, agent.desire))

                    # Move obstructions
                    self.__schedule_obstructions(to_move)
                    
                    actions = Controller.generate_move_actions(agent.current_route)
                    agent.update_actions(actions)
                    
                    # # Check for conflicts and update actions
                    # conflicts = self.__check_conflicts(agent)

                    # if conflicts:
                    #     cnfs_agts = conflicts[0]
                    #     self.__rev_cnfs[agent] = cnfs_agts

                    #     for other_agt in agents:
                    #         if not agent.equals(other_agt):
                    #             if agent not in self.__rev_cnfs[other_agt]:
                    #                 self.__make_agent_wait(agent, other_agt)
                                    
                    # Last location from actions
                    last_loc = self.__location_from_actions(
                        agent.location, 
                        actions
                    )
                    
                    __debug_msg = "Moving %s to %s." % (agent, last_loc)
                    log.debug(__debug_msg)
                    print(__debug_msg, file=sys.stderr, flush=True)
                    
                    agent.move(last_loc)  # location nearby box
                    agent.update_desire()
                    
                    __debug_msg = "Performing state search..."
                    log.debug(__debug_msg)
                    print(__debug_msg, file=sys.stderr, flush=True)
                    
                    list_actors, list_actions = self.__state_search(*self.__adapt_level(agent))
                    state_agents, state_boxes = list_actors
                                    
                    __debug_msg = "Extracting actions..."
                    log.debug(__debug_msg)
                    print(__debug_msg, file=sys.stderr, flush=True)
                    
                    # Extracting actions
                    agt_actions = []
                    for acts in list_actions:
                        for agt, action in acts.items():
                            if agt.equals(agent):
                                agt_actions.append(action)
                                
                    # Updating locations from actions received from state
                    for a in state_agents:
                        for agt in agents:
                            if a.equals(agt):
                                agt.add_to_route(a.location)
                                agt.move(a.location)
                                agent.update_desire()
                                log.debug("%s moved to %s." % (agt, agt.location))

                    agent.update_actions(agt_actions)
                    log.debug('%s new route is %s with actions %s.' % (
                        agent,
                        agent.current_route,
                        agent.actions
                    ))
                    
                    # Updating locations from actions received from state
                    for b in state_boxes:
                        for box in self.__boxes:
                            if b.equals(box):
                                box.move(b.location)
                                log.debug("%s moved to %s." % (box, box.location))

                    dbg += 1
            # Are agents satisfied?
            agents_desire = sum([not agent.desire.is_sleep_desire() for agent in agents])
        
        __debug_msg = 'Sending final plan to server...'
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
    
    def __make_agent_wait(self, agent: Agent, other_agt: Agent):
        """Insert NoOps for agents. 
        Handful when one agent is executing its actions and the others have to wait.

        Args:
            agent (Agent): The agent we derive the waiting from.
        """
        
        sz_dif = len(agent.actions) - len(other_agt.actions)
        if sz_dif > 0:
            other_agt.update_actions([Action.NoOp for _ in range(sz_dif)])
        else:
            # Tries to find where the route intersects
            intersect = 0
            for n, loc in enumerate(agent.current_route):
                for l in other_agt.current_route:
                    if l == loc: intersect = n
            other_agt.update_actions([Action.NoOp for _ in range(0, intersect)])

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
                if goal.identifier == agent.identifier:
                    _goals.put((agent.distance(loc), goal))
        else:
            for box in self.__boxes:
                if box.destination and box.color == agent.color:
                    _goals.put((agent.distance(box.location), box))
        
        f_goal = []
        
        # Sort boxes by score (distance)
        while not _goals.empty():
            f_goal.append(_goals.get()[1])
        return f_goal

    def __destination_for_box(self, box: Box) -> Location:
        log.debug("Finding destination for boxes.")
        
        _dests = PriorityQueue()
        other_destinations = set(box.destination for box in self.__boxes if box.destination)

        for loc, goal in self.__goals.items():
            if loc not in other_destinations and goal.identifier == box.identifier:
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
        # # This override is because of a Python variable address reference issue. 
        # # Neighbors from the given arguments somehow disappear.
        # # I dont have time to debug this
        # start = self.__level.get_location((start.row, start.col), translate=True)
        # end = self.__level.get_location((end.row, end.col), translate=True)
        
        class Node(object):
            location = None
            parent = None
            
            def __init__(self, location, parent):
                self.location = location
                self.parent = parent
                
            def __repr__(self) -> str:
                return 'N(%s)' % self.location
            
            def __lt__(self, other):
                return self.location < other.location
        
        frontier = PriorityQueue()
        frontier.put((start.distance(end), Node(start, None)))
        explored = set()
        _rhash = hash((start, end))
        
        # Checking cache
        try:
            return self.__cached_routes[_rhash]
        except KeyError:
            pass
        
        # Is end nearby?
        if end in start.neighbors: return [end, ]
        
        # Compute route
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
                return _r

            explored.add(visited)
            expanded = visited.neighbors
            
            for loc in expanded:
                nnode = loc.distance(end), Node(loc, node)
                if not (nnode in frontier.queue or loc in explored) and not loc.is_wall:
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
