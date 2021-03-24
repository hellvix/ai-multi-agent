from location import Location
from color import Color
from abc import ABCMeta, abstractmethod


class Actor(metaclass=ABCMeta):
    def __init__(self, identifier: str, location: Location, color: Color):
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
        if self is value:
            return True
        
        if not isinstance(value, Actor):
            return False
        
        if self.__identifier != value.identifier:
            return False
        
        if self.__color != value.__color:
            return False
        
        return True

    def __repr__(self):
        return self.__str__()

    @abstractmethod
    def __actor_type__(self): raise NotImplementedError

    @property
    def location(self):
        return self.__location

    @location.setter
    def move(self, value: Location):
        self.__location = value
