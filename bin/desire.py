from enum import Enum, unique

from box import Box
from location import Location

@unique
class DesireType(Enum):
    SLEEP = 0
    MOVE_TO_GOAL = 1  # Location (Box or Goal), controller decides


class Desire(object):
    def __init__(self, type: DesireType, obj=None, location=None):
        self.__type = type
        self.__object = obj  # Box or Goal
        self.location = location
        
    def __str__(self):
        return '{} {} {}'.format(
            self.__type,
            self.location,
            self.__object
        )
        
    def __repr__(self):
        return self.__str__()
    
    def is_box_desire(self):
        return isinstance(self.__object, Box)
    
    @property
    def type(self):
        return self.__type
