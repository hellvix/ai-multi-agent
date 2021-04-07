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
        
        
        
    # ========  DIMOS ===========
    
    def generate_move():

    path = [(1, 1), (1, 2), (1, 3), (2, 3), (3, 3), (4, 3), (5, 3), (6, 3), (7, 3), (8, 3), (9, 3), (10, 3), (11, 3), (12, 3), (13, 3), (14, 3), (15, 3), (16, 3), (17, 3), (17,4), (17,3)]

    x = map(lambda xval: xval[0], path)
    x = list(x)

    y = map(lambda yval: yval[1], path)
    y = list(y)

    path_x = []
    path_y = []

    for xval in range(len(x)-1):

        if x[xval+1] > x[xval]:
            path_x.append('MoveE')

        elif x[xval+1] < x[xval]:
            path_x.append('MoveW')

        elif x[xval+1] == x[xval]:
            path_x.append('same x')

        else:
            print('none of the above')

    for yval in range(len(y)-1):

        if y[yval+1] > y[yval]:
            path_y.append('MoveS')

        elif y[yval+1] < y[yval]:
            path_y.append('MoveN')

        elif y[yval+1] == y[yval]:
            path_y.append('same location')

        else:
            print('none of the above')

    for i in path_x:

        if i == 'same x':

            index = path_x.index(i)

            path_x[index] = path_y[index]

        else:
            pass

    moves = path_x

    print(path)  # The path we have in the beginning
    print(moves)  # The moves we want in the end
    print(len(moves))

    generate_move()

    return moves
>>>>>>> Stashed changes

