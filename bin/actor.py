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
            self.__identifier,
            self.__color,
            self.__location
        )

    def __eq__(self, value):
        if self.__color != value.color:
            return False

        if self.__identifier != value.identifier:
            return False

        return True

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
        return self.__identifier

    def move(self, location: 'Location'):
        # Leaves previous location first
        if self.__location:
            self.__location.displace()
        self.__location = location
