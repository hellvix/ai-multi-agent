from state import State
from color import Color
from agent import Agent
from action import Action
from location import Location
from configuration import Configuration


globals().update(Action.__members__)


class Controller(object):
    def __init__(self, configuration: Configuration):
        self.__parse_config__(configuration)
    
    def __parse_config__(self, configuration: Configuration):
        """Parses Configuration into data structure with objects
        """
        self.__level, self.__agents, self.__boxes, self.__goals = configuration.build_structure()
                
    def __spawn_state__(self):
        pass
    
    def deploy(self) -> [Action, ...]:
        # Here starts the algorithm
        agt = self.__agents[0]
        actions = self.generate_move(
            [
                (5, 1),
                (5, 2),
                (4, 2),
                (4, 3),
                (4, 4)
            ]
        )
        print(actions, flush=True)
        return actions
        
    def goals_for_agent(self, agent: Agent) -> [Location, ...]:
        """Return the location of the pre-defined level goals for the given agent (if exists).

        Args:
            agent (Agent): the agent

        Raises:
            Exception: If no goal exists for the agent.

        Returns:
            [Location, ...]: List of location objects
        """
        _goals = []
        
        for row in self.__level.layout:
            for loc in row:
                
                # If the location exists in the list with goals
                # we append it to _goals
                try:
                    goal = self.__goals[loc]
                    
                    if goal.color == agent.color:
                        # Race
                        if '0' <= goal.identifier <= '9':
                            if goal.identifier == agent.identifier:
                                _goals.append(goal.location)
                        # Boxes
                        else:
                            _goals.append(goal.location)
                        
                except KeyError:
                    # Will fail if the location is not a goal
                    pass
        
        if not _goals:
            raise Exception('Agent %s does not have a goal.' % agent)
    
        return _goals

    def find_path(self, start: Location, end: Location):
        
        def h(child, end):
            # @TODO needs implementation
            return
        
        open_list = []  # @TODO: needs proper declaration. Is it a list or a set?
        closed_list = [] # @TODO: needs proper declaration. Is it a list or a set?

        current_node = (start, 0)
        open_list.append(current_node)

        while len(open_list) > 0:

            if current_node[0] == end:
                break
                
            current_node = min(open_list, key = lambda t: t[1])
            closed_list.add(current_node)
            open_list.remove(current_node)

            for child in current_node[0].neighbors():
                
                if child in closed_list:
                    continue

                if child.is_wall:
                    continue
                    
                child_h = h(child, end)
                child_g = current_node[1] - child_h + 1
                child_f = child_h + child_g
                
                if child in open_list and child_f > [node[0] for node in open_list if node[0] == child]:
                    continue
                
                open_list.append((child, child_f))

        return closed_list

    def generate_move(self, path: '[tuple, ....]') -> '[Actions, ...]':
        """Generate actions based on given locations.

        Args:
            path ([type]): list of locations
        
        Author: dimos

        Returns:
            [type]: list of actions
        """

        y = map(lambda yval: yval[0], path)
        y = list(y)

        x = map(lambda xval: xval[1], path)
        x = list(x)

        path_x = []
        path_y = []

        for yval in range(len(y) - 1):

            if y[yval + 1] == y[yval] + 1:
                path_y.append([MoveS, ])

            elif y[yval + 1] == y[yval] - 1:
                path_y.append([MoveN, ])

            elif y[yval + 1] == y[yval]:
                path_y.append(['same y'])

            else:
                raise Exception('Typo error: Agent cannot move 2 steps in y (rows) !')

        for xval in range(len(x) - 1):

            if x[xval + 1] == x[xval] + 1:
                path_x.append([MoveE, ])

            elif x[xval + 1] == x[xval] - 1:
                path_x.append([MoveW, ])

            elif x[xval + 1] == x[xval]:
                path_x.append(['same x'])

            else:
                raise Exception('Typo error: Agent cannot move 2 steps in x (columns) !')

        for i, j in zip(path_y, path_x):

            if i == ['same y'] and j != ['same x']:
                index=path_y.index(i)
                index2=path_x.index(j)
                path_y[index]=path_x[index2]

            elif i == ['same y'] and j == ['same x']:
                index=path_y.index(i)
                path_y[index]=([NoOp, ])

            elif i != ['same y'] and j == ['same x']:
                pass

            else:
                raise Exception('Typo error: Agent cannot move diagonally / in both directions !')

        return path_y
