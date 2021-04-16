from actor import Actor


class Box(Actor):
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
