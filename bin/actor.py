from color import Color
from abc import ABCMeta, abstractmethod


class Actor(metaclass=ABCMeta):
    def __init__(self, identifier: str, location: 'Location', color: Color):
        self.__identifier = identifier
        self.__location = location
        self.__color = color

    def __str__(self):
        return '{}{} ({}) at {}'.format(
            self.__actor_type__(),
            self.identifier,
            self.__color,
            self.__location
        )

    def __eq__(self, value):
        if self.__color != value.color:
            return False

        if self.identifier != value.identifier:
            return False

        return True
    
    def __hash__(self):
        if self._hash is None:
            prime = 31
            _hash = 1
            _hash = _hash * prime + hash(self.__str__())
            _hash = _hash * prime + hash(tuple((self.__location.row, self.__location.col)))
            self._hash = _hash
        return self._hash

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
        self.__location = location
