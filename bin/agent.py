from queue import PriorityQueue

from goal import Goal
from actor import Actor
from action import Action
from location import Location
from desire import Desire, DesireType

class Agent(Actor):
    
    def __init__(self, *args, **kwargs):
        self.__goals = PriorityQueue  # Goal objects
        super().__init__(*args, **kwargs)
        
        self.__desire = None
        self.__master_plan = []  # Locations
        
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
            _hash = _hash * prime + hash(self.__goals)
            _hash = _hash * prime + hash(tuple((self.location.row, self.location.col)))
            self._hash = _hash
        return self._hash
    
    def _get_goal(self) -> tuple:
        """Pop the first Goal from the list.
        
        @IMPORTANT: The goal is removed from the list!

        Returns:
            tuple: (distance, Goal)
        """
        return self.__goals.get()
    
    def add_goal(self, distance: int, goal: Goal):
        self.__goals.put(distance, goal)
        
    @property
    def master_plan(self):
        return self.__master_plan
    
    def update_master_plan(self, plan):
        if isinstance(plan, list):
            self.__master_plan.extend(plan)

        if isinstance(plan, Action):
            self.__master_plan.append(plan)
    
    def add_goal(self, goal: tuple):
        return self.__goals.put(goal)
        
    @property
    def goals(self) -> PriorityQueue:
        return self.__goals
    
    @goals.setter
    def goals(self, goals: PriorityQueue):
        # When we set new goals we update the desire
        self.__goals = goals
        self._update_desire()

    def _has_goals(self) -> bool:
        return not self.__goals.empty()
    
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
                self._get_goal()[1].location
            )
            
    def receive_plan(self, plan: [Location, ...]):
        if not self.__desire:
            raise Exception('Agent does not have a desire.')

        self.__desire.plan = plan
        
    def move(self, location: Location):
        super().move(location)
        
        # All goals acomplished
        if self._has_goals() and self.desire.location == location:
            self.__desire = Desire(DesireType.SLEEP)
