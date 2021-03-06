from actor import Actor
from eprint import deb


class Box(Actor):
    destination = None
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
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
    
    def __eq__(self, other):

        if not isinstance(other, Box):
            return False

        return super().__eq__(other)
    
    def __lt__(self, other):
        return self.identifier < other.identifier
    
    def equals(self, other: 'Box'):
        return self.identifier == other.identifier and isinstance(other, Box)
