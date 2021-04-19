from goal import Goal
from actor import Actor
from action import Action
from location import Location
from desire import Desire, DesireType

class Agent(Actor):
    
    def __init__(self, *args, **kwargs):
        self.__goals = set()  # Goal objects
        super().__init__(*args, **kwargs)
        
        self.__desire = None
        # Current route. Can either be discarded or be added to master route
        self.__current_route = None
        # The set of actions leading to the completion of the level
        self.__actions = []
        
        # Object properties
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
            _hash = _hash * prime + hash(tuple(goal for goal in self.__goals))
            _hash = _hash * prime + hash(tuple((self.location.row, self.location.col)))
            self._hash = _hash
        return self._hash
    
    def _get_goal(self):
        """Pop the first Goal from the list.
        
        @IMPORTANT: The goal is removed from the list!
        """
        return self.__goals.pop()
    
    def add_goal(self, distance: int, goal: Goal):
        self.__goals.add(goal)
        
    @property
    def current_route(self):
        return self.__current_route
    
    def update_route(self, route: [Location, ...]):
        if not isinstance(route[0], Location):
            raise Exception('The agent route must be a list of Locations, not %s.' % type(route[0]))
        self.__current_route = route
        
    @property
    def actions(self):
        return self.__actions
    
    def derive_move_actions(self):
        """Derive move actions from current route.
        """
        from controller import Controller
        return Controller.generate_move(self.current_route)
    
    def update_actions(self, actions: [Action, ...]):
        self.__actions.extend(actions)
    
    def add_goal(self, goal: tuple):
        return self.__goals.add(goal)
    
    def has_reached(self):
        if not self.desire:
            return True
        return self.location == self.desire.location
        
    @property
    def goals(self) -> set:
        return self.__goals
    
    @goals.setter
    def goals(self, goals: set):
        # When we set new goals we update the desire
        self.__goals = goals
        self._update_desire()

    def _has_goals(self) -> bool:
        return not self.__goals == set()
    
    @property
    def desire(self):
        return self.__desire
    
    @property
    def desire_type(self):
        return self.__desire.type
    
    def _update_desire(self):
        if not self._has_goals():
            self.__desire = Desire(DesireType.SLEEP)
        else:
            self.__desire = Desire(
                DesireType.MOVE_TO_GOAL,
                self._get_goal()
            )
            
        
    def move(self, location: Location):
        super().move(location)
        
        # All goals acomplished
        if self._has_goals() and self.desire.location == location:
            self.__desire = Desire(DesireType.SLEEP)
