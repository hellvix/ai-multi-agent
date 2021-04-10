from state import State
from color import Color
from agent import Agent
from action import Action
from location import Location
from configuration import Configuration

globals ().update ( Action.__members__ )


class Controller ( object ):
    def __init__(self, configuration: Configuration):
        self.__parse_config__ ( configuration )

    def __parse_config__(self, configuration: Configuration):
        """Parses Configuration into data structure with objects
        """
        self.__level, self.__agents, self.__boxes, self.__goals = configuration.build_structure ()

    def __spawn_state__(self):
        pass

    def deploy(self) -> [Action, ...]:
        # Here starts the algorithm
        agt = self.__agents[2]
        agt.goals = self.goals_for_agent ( agt )
        print ( agt.goals, flush=True )

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
                                _goals.append ( goal.location )
                        # Boxes
                        else:
                            _goals.append ( goal.location )

                except KeyError:
                    # Will fail if the location is not a goal
                    pass

        if not _goals:
            raise Exception ( 'Agent %s does not have a goal.' % agent )

        return _goals

    def generate_move(path):

        y = map ( lambda yval: yval[0], path )
        y = list ( y )

        x = map ( lambda xval: xval[1], path )
        x = list ( x )

        path_x = []
        path_y = []

        for yval in range ( len ( y ) - 1 ):

            if y[yval + 1] > y[yval]:
                path_y.append ( MoveS )

            elif y[yval + 1] < y[yval]:
                path_y.append ( MoveN )

            elif y[yval + 1] == y[yval]:
                path_y.append ( 'same y' )

            else:
                pass

        for xval in range ( len ( x ) - 1 ):

            if x[xval + 1] > x[xval]:
                path_x.append ( MoveE )

            elif x[xval + 1] < x[xval]:
                path_x.append ( MoveW )

            elif x[xval + 1] == x[xval]:
                path_x.append ( 'same x' )

            else:
                pass

        for i in path_y:

            if i == 'same y':

                index = path_y.index ( i )

                path_y[index] = path_x[index]

            else:
                pass

        moves = path_y

    generate_move()

