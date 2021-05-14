import numpy as np


class Location(object):
    __pos_row = None
    __pos_col = None
    __neighbors = None
    is_wall = None
    _hash = None
    __distances = None
    
    def __init__(self, row: int, col: int):
        self.__pos_row = row  # Y
        self.__pos_col = col  # X
        self.__neighbors = None
        self.is_wall = None
        self._hash = None
        self.__distances = None

    def __hash__(self):
        if self._hash is None:
            prime = 31
            _hash = 1
            _hash = _hash * prime + hash(self.__str__())
            _hash = _hash * prime + hash((self.row, self.col))
            self._hash = _hash
        return self._hash

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        # LY,X === LROW, COL
        return "{}R{},C{}".format(
            'W' if self.is_wall else 'L',
            self.row,  # Y
            self.col   # y
        )

    def __eq__(self, value):
        if not value:
            return False

        if not (isinstance(value, Location)):
            raise Exception(
                'Cannot compare Location with %s.' % type(value)
            )
        
        if (self.row != value.row or self.col != value.col):
            return False
        
        return True
    
    def __lt__(self, other):
        return (self.row + self.col) < (other.row + other.col)
    
    @property
    def distances(self):
        return self.__distances
        
    @property
    def row(self):
        # Y
        return self.__pos_row
    
    @property
    def col(self):
        # X
        return self.__pos_col
        
    @property
    def neighbors(self):
        return self.__neighbors
    
    @neighbors.setter
    def neighbors(self, value):
        self.__neighbors = value
        
    def build_distance_array(self, rows: int, cols: int):
        """Precompute Manhattan distance for all points

        Args:
            rows (int): real number of rows the level has
            cols (int): real number of cols the level has
        """
        self.__distances = np.zeros((rows, cols), dtype=int)
        
        for row in range(rows):
            for col in range(cols):
                self.__distances[row][col] = abs(col - self.col) + abs(row - self.row)
        
    def distance(self, location: 'Location'):
        """Pre-computed distance from this location to Y.
        """
        return self.distances[location.row][location.col]
