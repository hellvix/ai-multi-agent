from actor import Actor


class Box(Actor):
    def __actor_type__(self):
        return 'Box'
    
    def __eq__(self, value):

        if not isinstance(value, Box):
            return False

        return super().__eq__(value)
