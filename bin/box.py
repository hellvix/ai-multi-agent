from actor import Actor
from eprint import deb


class Box(Actor):
    destination = None
    
    def __init__(self, *args):
        super().__init__(*args)
        self.destination = None
        
    def has_reached(self):
        return self.location == self.destination
    
    def __actor_type__(self):
        return 'Box'
    
    def __hash__(self):
        if self._hash is None:
            prime = 97
            _hash = 1
            _hash = _hash * prime + hash(self.__str__())
            _hash = _hash * prime + hash(self.location)
            _hash = _hash * prime + hash(tuple((self.color.value, )))
            self._hash = _hash
        return self._hash
    
    def __eq__(self, value):

        if not isinstance(value, Box):
            return False

        return super().__eq__(value)

    @property
    def current_route(self):
        return self.__current_route

    def set_current_route(self, route: ['Location', ...]):
        self.__current_route = route
