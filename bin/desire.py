from enum import Enum, unique

from box import Box
from location import Location

@unique
class DesireType(Enum):
    SLEEP = 0
    MOVE_TO_LOCATION = 1  # Box location or destination
    MOVE_BOX_TO_GOAL = 2


class Desire(object):
    def __init__(self, type: DesireType, element=None, location=None):
        self.__type = type
        self.__element = element  # Box or Goal
        # Where the agent wants to be
        # Should not be the same location as element
        self.location = location
        
    def __str__(self):
        return "{} {} {}".format(
            self.__type,
            self.location,
            self.__element or ''
        )
        
    def __repr__(self):
        return self.__str__()
    
    @property
    def element(self):
        return self.__element
    
    def is_sleep_desire(self):
        return self.type == DesireType.SLEEP
    
    def is_location_desire(self):
        return self.type == DesireType.MOVE_TO_LOCATION
    
    def is_move_box_desire(self):
        return self.type == DesireType.MOVE_BOX_TO_GOAL
    
    def is_box_desire(self):
        return isinstance(self.__element, Box)
    
    @property
    def type(self):
        return self.__type
