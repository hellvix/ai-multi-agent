from enum import Enum, unique

from location import Location

@unique
class DesireType(Enum):
    SLEEP = 0
    MOVE_TO_GOAL = 1  # Location (Box or Goal), controller decides
    NEED_HELP = 2


class Desire(object):
    def __init__(self, type: DesireType, location=None):
        self.__type = type
        self.location = location
        self.route = []  # Locations
        
    def __str__(self):
        return '{} {} {}'.format(
            self.__type,
            self.location,
            self.route
        )
    
    @property
    def type(self):
        return self.__type
