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
        path = self.find_path(agt.location, self.goals_for_agent(agt)[0])
        print(path, flush=True)

        return [
        ]
        
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
         	       
                
    	def h(start: Location, end: Location):
        	return abs((start.col - end.col) + (start.row - end.row))

        
        """It's a list of tuples of locations and it's f score. Before adding each new element we check if it's already inside, so technically 
        it acts like a set """
        open_list = []  # @TODO: needs proper declaration. 

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
