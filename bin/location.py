import sys
import heapq
import numpy as np


class Location:
    def __init__(self, pos_row: int, pos_col: int):
        self.__pos_row = pos_row  # col
        self.__pos_col = pos_col  # row
        self.__neighbors = None
        self.is_wall = None
        self.is_goal = None

        self._hash = None

    def __hash__(self):
        if self._hash is None:
            prime = 31
            _hash = 1
            _hash = _hash * prime + hash(self.__str__())
            _hash = _hash * prime + hash(tuple((self.pos_row, self.pos_col)))
            self._hash = _hash
        return self._hash

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return 'L{},{}'.format(
            self.pos_row,
            self.pos_col
        )

    def __eq__(self, value):
        
        if self is value:
            return True
        
        if not isinstance(value, Location):
            raise Exception('Cannot compare Location with this type of object.')
        
        if (self.pos_row != value.pos_row) and (self.pos_col != value.pos_col):
            return False
        
        return True
        
    @property
    def pos_row(self):
        return self.__pos_row
    
    @property
    def pos_col(self):
        return self.__pos_col
        
    @property
    def neighbors(self):
        return self.__neighbors
    
    @neighbors.setter
    def neighbors(self, value):
        self.__neighbors = value

    def manhattan_distance(self, dest: tuple):
        """ Manhattan distance from this location to dest

        Args:
            dest (tuple): (row, column)

        Returns:
            int: distance
        """
        return abs(
            self.pos_row - dest[0]
        ) + abs(
            self.pos_col - dest[1]
        )
