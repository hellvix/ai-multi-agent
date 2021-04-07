from actor import Actor
from location import Location


class Agent(Actor):
    
    def __init__(self, *args, **kwargs):
        self.__goals = set()  # List of Locations
        super().__init__(*args, **kwargs)
    
    def __actor_type__(self):
        return 'Agent'
    
    def __eq__(self, value):

        if not isinstance(value, Agent):
            return False

        return super().__eq__(value)
<<<<<<< Updated upstream
    
    def __hash__(self):
        if self._hash is None:
            prime = 31
            _hash = 1
            _hash = _hash * prime + hash(self.__str__())
            _hash = _hash * prime + hash(tuple(self.__goals))
            _hash = _hash * prime + \
                hash(tuple((self.__location.row, self.__location.col)))
            self._hash = _hash
        return self._hash
    
    def add_goal(self, value: '[Location, ...]'):
        if isinstance(value, list):
            self.__goals.update(value)
        elif isinstance(value, Location):
            self.__goals.add(value)

    @property
    def goals(self):
        return set(self.__goals)
    
    @goals.setter
    def goals(self, value):
        self.__goals = value
=======
        
        
        
    
>>>>>>> Stashed changes

