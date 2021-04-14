from color import Color
from location import Location

class Goal(object):
    def __init__(self, identifier: str, location: 'Location', color: Color):
        self.__identifier = identifier
        self.__location = location
        self.__color = color
        
    def __hash__(self):
        if self._hash is None:
            prime = 31
            _hash = 1
            _hash = _hash * prime + hash(self.__str__())
            _hash = _hash * prime + hash(tuple((self.__location.row, self.__location.col)))
            self._hash = _hash
        return self._hash

    def __str__(self):
        return 'Goal{} ({}) at {}'.format(
            self.identifier,
            self.__color,
            self.__location
        )
    
    def __eq__(self, other):
        return self.location == other.location
    
    def __le__(self, other):
        return self.identifier < self.identifier
    
    @property
    def location(self):
        return self.__location
    
    @property
    def identifier(self):
        return str(self.__identifier)
    
    @property
    def color(self):
        return self.__color

    def __eq__(self, value):
        if isinstance(value, Location):
            return self.__location == value
        
        if not isinstance(value, Goal):
            raise Exception('Cannot compare Goal with this type of object.')
        
        if self.__color != value.color:
            return False

        if self.__identifier != value.identifier:
            return False

        return True

    def __repr__(self):
        return self.__str__()
