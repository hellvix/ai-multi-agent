from eprint import deb

from queue import PriorityQueue

from goal import Goal
from actor import Actor
from action import Action
from location import Location
from desire import Desire, DesireType

class Agent(Actor):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__goals = set()
        self.__desire = None
        self.__actions = []
        
        self._hash = None
    
    def __actor_type__(self):
        return 'Agent'
    
    def __eq__(self, value):

        if not isinstance(value, Agent):
            return False

        return super().__eq__(value)
    
    def __hash__(self):
        if self._hash is None:
            prime = 41
            _hash = 1
            _hash = _hash * prime + hash(self.__str__())
            _hash = _hash * prime + hash(tuple(self.__goals))
            _hash = _hash * prime + hash(tuple((self.location.row, self.location.col)))
            self._hash = _hash
        return self._hash
        
    @property
    def actions(self):
        return self.__actions
    
    def update_actions(self, actions: [Action, ...]):
        self.__actions.extend(actions)

    def clear_actions(self):
        self.__actions = []
        self.clear_route()
    
    def has_reached(self):
        if not self.desire:
            return True
        return self.location in self.desire.location
    
    def _get_goal(self):
        """Pop the first Goal from the list.
        
        @IMPORTANT: The goal is removed from the list!
        """
        return self.__goals.pop()

    def add_goal(self, goal: Goal):
        self.__goals.add(goal)
        
    @property
    def goals(self) -> set:
        return self.__goals
    
    @goals.setter
    def goals(self, goals: set):
        # When we set new goals we update the desire
        if not isinstance(goals, set):
            raise Exception('Attribute goals must be of type set.')
        self.__goals = goals

    def _has_goals(self) -> bool:
        return not self.__goals == set()
    
    @property
    def desire(self):
        return self.__desire
    
    @property
    def desire_type(self):
        return self.__desire.type
    
    def update_desire(self):
        if not self._has_goals():
            self.__desire = Desire(DesireType.SLEEP)
        else:
            _g = self._get_goal()
            self.__desire = Desire(
                type=DesireType.MOVE_TO_GOAL,
                obj=_g,
                location=_g.location
            )
    
    def equals(self, other: 'Agent'):
        return self.identifier == other.identifier
        
    def move(self, location: Location):
        super().move(location)
        
        # All goals acomplished
        if self._has_goals() and self.desire.location == location:
            self.__desire = Desire(DesireType.SLEEP)
