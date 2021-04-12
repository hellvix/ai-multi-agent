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


        # placeholder, should put priorities in future first
        path = self.find_path(
            self.__level.get_location((1,1), translate=True),    # (1, 1)
            self.__level.get_location((5,11), translate=True)   # (3, 10)
            )

        coords = []
        for cell in path:
            coords.append((cell.row, cell.col))

        actions = self.generate_move(coords)
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
                   
                
        #def h(start: Location, end: Location):
        #   return abs((start.col - end.col) + (start.row - end.row))

      
        open_list = []  # @TODO: needs proper declaration. 

        closed_list = [] # @TODO: needs proper declaration. Is it a list or a set?

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

            if y[yval + 1] > y[yval]:
                path_y.append([MoveS, ])

            elif y[yval + 1] < y[yval]:
                path_y.append([MoveN, ])

            elif y[yval + 1] == y[yval]:
                path_y.append('same y')

            else:
                pass

        for xval in range(len(x) - 1):

            if x[xval + 1] > x[xval]:
                path_x.append([MoveE, ])

            elif x[xval + 1] < x[xval]:
                path_x.append([MoveW, ])

            elif x[xval + 1] == x[xval]:
                path_x.append('same x')

            else:
                pass

        for i in path_y:

            if i == 'same y':
                index = path_y.index(i)
                path_y[index] = path_x[index]
            else:
                pass

        return path_y
