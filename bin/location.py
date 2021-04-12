import sys
import heapq
import numpy as np
from actor import Actor


class Location(object):
    def __init__(self, row: int, col: int):
        self.__pos_row = row  # col
        self.__pos_col = col  # row
        self.__neighbors = None
        self.is_wall = None

        self._hash = None

    def __hash__(self):
        if self._hash is None:
            prime = 31
            _hash = 1
            _hash = _hash * prime + hash(self.__str__())
            _hash = _hash * prime + hash(tuple((self.__pos_row, self.__pos_col)))
            self._hash = _hash
        return self._hash

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return 'L{},{}'.format(
            self.__pos_row,
            self.__pos_col
        )

    def __eq__(self, value):
        if not isinstance(value, Location):
            raise Exception(
                'Cannot compare Location with %s.' % type(value)
            )
        
        if (self.row != value.row) or (self.col != value.col):
            return False
        
        return True
        
    @property
    def row(self):
        return self.__pos_row
    
    @property
    def col(self):
        return self.__pos_col
        
    @property
    def neighbors(self):
        return self.__neighbors
    
    @neighbors.setter
    def neighbors(self, value):
        self.__neighbors = value

    def manhattan_distance(self, destination):
        """ Manhattan distance from this location to destination
            Important: when passing distances as tuples, remember to index them
            just like Level.layout is index! That is, L1,1 is at index layout[0][0].
        Args:
            dest: either a tuple or Location

        Returns:
            int: distance
        """
        
        row, col = (
            destination.row,
            destination.col
        ) if isinstance(
            destination,
            Location
        ) else destination
             
        return abs(
            self.row - row
        ) + abs(
            self.col - col
        )
