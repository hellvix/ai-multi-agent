import sys
import heapq
import numpy as np
from location import Location


class Level(object):
    """A redifined definition of a level
    Defines locations as a a set of locations, together with its neighbors.
    """

    def __init__(self, layout: list, num_rows: int, num_cols: int):
        # Representation of the level in Location objects, ignoring outside walls.
        # This means row 1 in the level is actually located in row 0 in this array.
        # [
        #   [L1,1, L1,2, L1,3],
        #   [L2,1, L2,2, ... ]
        # ]

        self.__layout = layout
        self.__num_rows = num_rows  # Total number of rows (counting outside walls)
        self.__num_cols = num_cols  # Total number of cols (counting outside walls)
        
    def __hash__(self):
        if self._hash is None:
            prime = 31
            _hash = 1
            _hash = _hash * prime + hash(tuple(self.__layout))
            self._hash = _hash
        return self._hash
        
    @property
    def layout(self):
        return self.__layout

    @property
    def num_rows(self):
        return self.__num_rows
    
    @property
    def real_num_rows(self):
        """Number of rows ignoring outside walls

        Returns:
            int: number of rows
        """
        return self.num_rows - 2
    
    @property
    def num_cols(self):
        return self.__num_cols

    @property
    def real_num_cols(self):
        """Number of cols ignoring outside walls

        Returns:
            int: number of cols
        """
        return self.num_cols - 2
    
    def get_location(self, coordinates: tuple, translate=False) -> Location:
        """Given the coordinates (matrix indexes), which object location is at this position?
        Important: the layout vector is 0-indexed, this means L1,1 is located at position [0][0]
        
        If translate is True, then the coordinates are converted to 0-based indexes.

        Args:
            coordinates (tuple): (row, col)
            translate (bol): whether the coordinates are 0-index-based or not

        Returns:
            Location: object at this index
        """
        row, col = coordinates
        try:
            if translate:
                row = row - 1
                col = col - 1
            return self.__layout[row][col]
        except IndexError:
            raise Exception("Coordinates do not exist.")
