import sys

from queue import PriorityQueue

from state import State
from color import Color
from agent import Agent
from action import Action
from location import Location
from configuration import Configuration, RaceType
from desire import DesireType

from itertools import groupby


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
                   
    def define_initial_goals(self):
        # Define initial goal for the agents
        # Based on these goals, the agents are going to update their desire

        for agent in self.__agents:
            agent.goals = self.goals_for_agent(agent)
            
    def is_plan_solid(self, agent: Agent, plan: [Location, ...]):
        """Check whether a given plan is achievable for the given agent
        """

        # Check the position of all agents, ignoring the one making the plan
        agent_locs = set(agt.location for agt in self.__agents if agent != agt)
        box_locs = set(box.location for box in self.__boxes if box.color != agent.color)
        
        for loc in plan:
            # Check if the location is a wall (shouldn't be, but dobble checking)
            if loc.is_wall:
                return False

            # Check if there is something in the way
            if loc in agent_locs or loc in box_locs:
                return False

        return True
    
    def planner(self):
        # Assign plan for agents
        agents = self.__agents

        # @TODO: Improve which agent gets picked up first
        # @TODO: Allow parallelism between agent actions
        for agent in agents:
            
            if agent.desire_type == DesireType.MOVE_TO_GOAL:
                destionation = agent.desire.location
                plan = self.find_path(agent.location, destionation)

                if self.is_plan_solid(agent, plan):
                    actions = self.generate_move(plan)
                    act_sz = len(actions)

                    # Allow the agent to execute its plan
                    agent.move(destionation)
                    agent.update_master_plan(actions)
                    
                    # Update other agents' master_plan
                    # Make them wait
                    # @TODO: Improve. What to do while one agent is fulfilling its desire?
                    for other_agt in agents:
                        if other_agt != agent:
                            other_agt.update_master_plan(
                                [Action.NoOp for _ in range(act_sz)]
                            )
                    
    def assemble_solution(self) -> [Action, ...]:
        """Gather agents actions

        Returns:
            [Action, ...]: Agent actions
        """
        
        acts_sz = len(self.__agents[0].master_plan)  # number of actions
        f_plan = [[] for _ in range(acts_sz)]
        
        # Sanity check (plans must have the same length)
        sizes = [len(agent.master_plan) for agent in self.__agents]  # Size of all actions
        gsiz = groupby(sizes)
        
        if next(gsiz, True) and next(gsiz, False):
            raise Exception('Size in list of Actions for agents differ.')
        
        for action in range(acts_sz):
            for agent in self.__agents:
                f_plan[action].append(agent.master_plan[action])
        
        return f_plan

    def deploy(self) -> [Action, ...]:
        print('Solving level...', file=sys.stderr, flush=True)
        
        # Code goes here
        self.define_initial_goals()
        self.planner()
        
        return self.assemble_solution()

    def goals_for_agents(self) -> [Location, ...]:
        return {a: self.goals_for_agent(a) for a in self.__agents}

    def goals_for_agent(self, agent: Agent) -> [Location, ...]:
        """Return the location of the pre-defined level goals for the given agent (if exists).
        
        Args:
            agent (Agent): the agent

        Raises:
            Exception: If no goal exists for the agent.

        Returns:
            [Location, ...]: List of location objects
        """
        _goals = PriorityQueue()
        
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
                                    _goals.put((1, goal))
                            # Boxes
                            else:
                                # @TODO: function to calculate distance from agent to goal
                                # So it is sorted by the distance, therefore creating a priority
                                _goals.put((1, goal))
                            
                    except KeyError:
                        # Will fail if the location is not a goal
                        pass
        
        return _goals

    def find_path(self, start: Location, end: Location):
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

    def generate_move(self, path: '[Location, ...]') -> '[Actions, ...]':
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
