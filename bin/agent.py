import logging

from eprint import deb

from queue import PriorityQueue

from goal import Goal
from actor import Actor
from action import Action
from location import Location
from desire import Desire, DesireType


log = logging.getLogger(__name__)


class Agent(Actor):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__goals = []
        self.__desire = None
        self.__actions = []
        
        self._hash = None
    
    def __actor_type__(self):
        return 'Agent'
    
    def __lt__(self, other):
        return int(self.identifier) < int(other.identifier)
    
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
    
    def has_route(self):
        return not self.current_route == None
    
    def reschedule_desire(self, goal):
        _ng = [goal, ]
        
        if not self.desire.is_sleep_desire():
            # Current desire must not be discarded
            _ng.append(self.desire.element)
        
        _ng.extend(self.__goals)
        self.__goals = _ng
        self.update_desire(overrule=True)
        
    def update_route(self, route):
        _r = self.__correct_route(route)
        super().update_route(_r)
    
    def update_actions(self, actions: [Action, ...]):
        self.__actions.extend(actions)

    def clear_actions(self):
        self.__actions = []
        self.clear_route()
    
    def _get_goal(self):
        """Get the first Goal from the list.
        
        @IMPORTANT: The goal is removed from the list!
        """
        _g = self.__goals[0]
        self.__goals.remove(_g)
        return _g

    def add_goal(self, goal):
        self.__goals.append(goal)
        
    @property
    def goals(self) -> list:
        return self.__goals
    
    @goals.setter
    def goals(self, goals):
        self.__goals = goals

    def _has_goals(self) -> bool:
        return self.__goals
    
    @property
    def desire(self):
        return self.__desire
    
    def _clear_desire(self):
        """ The current desire will be lost.
        It must be manually added to the list of goals.
        This method should ideally be called from 'reschedule_desire'
        """
        self.__desire = None
    
    @property
    def desire_type(self):
        return self.__desire.type
    
    def is_desire_satisfied(self):
        if self.desire.is_box_desire():
            if self.desire.is_move_box_desire():
                if self.desire.element.location == self.desire.element.destination:
                    return True

            elif self.desire.is_location_desire():
                if self.location in self.desire.element.location.neighbors:
                    return True
            
        elif self.desire.is_location_desire():
            if self.location == self.desire.location:
                return True
            
        elif self.desire.is_sleep_desire():
            return True
        return False
    
    def update_desire(self, overrule=False):
        """Update the agent desire until it defaults to sleep.

        Args:
            overrule (bool, optional): If given, the current desire will be discarded. Defaults to True.

        """
        if overrule: self._clear_desire()
            
        if self.desire:
            if self.is_desire_satisfied():
                if self.desire.is_location_desire():
                    if self.desire.is_box_desire():
                        self.__desire = Desire(
                            type=DesireType.MOVE_BOX_TO_GOAL,
                            element=self.desire.element,
                            location=self.desire.element.destination
                        )
                        # The desire might have already been satisfied by solving
                        # conflicts with other agents. Checking again.
                        return self.update_desire()
            else: 
                return

        if self._has_goals():
            _g = self._get_goal()
            
            self.__desire = Desire(
                type=DesireType.MOVE_TO_LOCATION,
                element=_g,
                location=_g.location
            )
            return
        self.__desire = Desire(
            DesireType.SLEEP,
            location=self.location
        )

    def __correct_route(self, route):
        """Redefine routes for each goal type.
        If boxes are involved, we cannot walk all the way to their location, but
        a location nearby.

        Args:
            agent ([Agent]): The agent
            route ([Location, ...]): Its route
        """
        # Update desire in case boxes are involved
        if self.desire.is_box_desire():
            log.debug("Adapting route and desire locations...")
            # The agent is too close to where it wants to go
            if len(route) == 1:
                _end = self.location
                route = [_end, ]
                self.desire.location = _end
            # Avoid sending the last location (box is standing there)
            else:
                route = route[:-1]
                self.desire.location = route[-1:][0]

        return route
    
    def equals(self, other: 'Agent'):
        return self.identifier == other.identifier and isinstance(other, Agent)
        
    def move(self, location: Location):
        super().move(location)
