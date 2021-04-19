from color import Color
from abc import ABCMeta, abstractmethod


class Actor(metaclass=ABCMeta):
    __identifier = None
    __location = None
    __color = None
    _hash = None

    def __init__(self, identifier: str, location: 'Location', color: Color):
        self.__identifier = identifier
        self.__location = location
        self.__color = color
        
        self._hash
        
    def __hash__(self): raise NotImplementedError

    def __str__(self):
        return '{}{} ({}) @{}'.format(
            self.__actor_type__(),
            self.identifier,
            self.__color,
            self.__location
        )

    def __eq__(self, other):
        if not self.__color == other.color:
            return False

        if not self.identifier == other.identifier:
            return False
        
        if not self.location == other.location:
            return False

        return True
    
    def __hash__(self): raise NotImplementedError

    def __repr__(self):
        return self.__str__()

    @abstractmethod
    def __actor_type__(self): raise NotImplementedError

    @property
    def location(self):
        return self.__location
    
    @property
    def color(self):
        return self.__color

    @property
    def identifier(self):
        return str(self.__identifier)

    def move(self, location: 'Location'):
        """Change actor location. Should not be called without checking whether
        the new Location is already occupied.

        Args:
            location (Location): [description]
        """
        from location import Location

        if not isinstance(location, Location):
            raise Exception('Parameter location must be an instance of Location.')
        self.__location = location
