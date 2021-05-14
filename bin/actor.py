import location

from color import Color

class Actor(object):
    __identifier = None
    __location = None
    __color = None
    _hash = None
    __current_route = None

    def __init__(self, identifier: str, location: 'Location', color: Color):
        self.__identifier = identifier
        self.__location = location
        self.__color = color
        self.__current_route = None
        
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
            raise Exception('Parameter location must be an instance of Location, not %s.' % type(location))
        self.__location = location
        
    def distance(self, location: 'Location') -> int:
        return self.location.distance(location)

    @property
    def current_route(self):
        return self.__current_route
    
    def clear_route(self):
        self.__current_route = None
        
    def add_to_route(self, loc: 'Location'
                     ):
        if not isinstance(loc, location.Location):
            raise Exception('Parameter must be of type location.')

        self.__current_route.append(loc)

    def update_route(self, route: ['Location', ...]):
        if route and not isinstance(route[0], location.Location):
            raise Exception(
                'The agent route must be a list of Locations, not %s.' % type(route[0]))
        self.__current_route = route
